import json
import os
from datetime import datetime, timezone
from pathlib import Path

from builder.queue import BuilderQueue
from launch.compliance import WebsiteComplianceGate
from launch.github_publish import GitHubPublisher
from launch.lemonsqueezy import LemonSqueezyProvisioner
from launch.release import ReleaseManager
from launch.smoke import SmokeChecker
from launch.vercel import VercelDeployer
from schemas.compliance import ComplianceReport
from schemas.launch import BillingProvision, LaunchResult
from schemas.product import ProductPackage


class LaunchAgent:
    def __init__(
        self,
        build_queue: BuilderQueue | None = None,
        products_root: str = "products",
    ):
        self.build_queue = build_queue or BuilderQueue()
        self.products_root = Path(products_root)
        self.release_manager = ReleaseManager()
        self.github = GitHubPublisher()
        self.billing = LemonSqueezyProvisioner()
        self.vercel = VercelDeployer()
        self.smoke = SmokeChecker()
        self.compliance = WebsiteComplianceGate()

    def prepare_next(
        self,
        publish_github: bool = False,
        configure_lemonsqueezy: bool = False,
        deploy_vercel: bool = False,
    ) -> LaunchResult | None:
        job = self._next_launchable()
        if not job:
            return None

        slug = job["product_slug"]
        result = None

        try:
            manifest = self.release_manager.prepare(slug)
            release_dir = Path(manifest.release_dir)
            source_review = self.compliance.review_source(release_dir)

            result = LaunchResult(
                product_slug=slug,
                status="READY_TO_PUBLISH",
                release_dir=manifest.release_dir,
                archive_path=manifest.archive_path,
                compliance=source_review,
            )

            if not source_review.passed:
                raise RuntimeError(
                    "Merchant-review website preflight failed: "
                    + "; ".join(source_review.errors)
                )

            self.build_queue.update_status(slug, "READY_TO_PUBLISH")

            if publish_github:
                result.github_repo = self.github.publish(release_dir, slug)
                result.status = "PUBLISHED"
                self.build_queue.update_status(slug, "PUBLISHED")

            runtime_env = self._public_runtime_env()
            verified_billing = BillingProvision()

            if configure_lemonsqueezy:
                verified_billing = self.billing.verify_plan()
                result.billing = verified_billing
                runtime_env.update({
                    "LEMON_SQUEEZY_API_KEY": os.getenv(
                        "LEMON_SQUEEZY_API_KEY", ""
                    ).strip(),
                    "LEMON_SQUEEZY_STORE_ID": verified_billing.store_id or "",
                    "LEMON_SQUEEZY_VARIANT_ID": verified_billing.variant_id or "",
                    "LEMON_SQUEEZY_WEBHOOK_SECRET": os.getenv(
                        "LEMON_SQUEEZY_WEBHOOK_SECRET", ""
                    ).strip(),
                    "NEXT_PUBLIC_PLAN_PRICE": (
                        "$" + "{:.2f} / month".format(
                            verified_billing.monthly_amount_usd
                        )
                        if verified_billing.monthly_amount_usd is not None
                        else ""
                    ),
                })

                runtime_review = self.compliance.review_runtime(
                    overrides=runtime_env
                )
                result.compliance = self._merge_compliance(
                    source_review,
                    runtime_review,
                )
                if not result.compliance.passed:
                    raise RuntimeError(
                        "Merchant-review runtime preflight failed: "
                        + "; ".join(result.compliance.errors)
                    )

                self._write_runtime_env_hint(release_dir, runtime_env)

            if deploy_vercel:
                if not configure_lemonsqueezy:
                    raise RuntimeError(
                        "Public launch requires --configure-lemonsqueezy so the "
                        "published pricing and checkout can be verified against "
                        "a real Lemon Squeezy subscription variant."
                    )

                result.deployment_url = self.vercel.deploy(
                    release_dir,
                    production=True,
                    environment=runtime_env,
                )
                result.status = "SITE_LIVE"
                self.build_queue.update_status(slug, "SITE_LIVE")

                result.billing.webhook_id = self.billing.ensure_webhook(
                    result.deployment_url,
                    test_mode=bool(result.billing.test_mode),
                )

                result.smoke_results = self.smoke.check(
                    result.deployment_url,
                    manifest.smoke_paths,
                )
                if not result.smoke_results or not all(
                    result.smoke_results.values()
                ):
                    raise RuntimeError(
                        f"Deployment smoke test failed: {result.smoke_results}"
                    )

                if result.billing.test_mode:
                    result.status = "BILLING_TEST"
                    self.build_queue.update_status(slug, "BILLING_TEST")
                else:
                    result.status = "LIVE"
                    self.build_queue.update_status(slug, "LIVE")

        except Exception as exc:
            if result is None:
                result = LaunchResult(
                    product_slug=slug,
                    status="FAILED",
                    release_dir=f"releases/{slug}",
                    archive_path="",
                )
            result.status = "FAILED"
            result.errors.append(str(exc))
            self.build_queue.update_status(
                slug,
                "LAUNCH_FAILED",
                error=str(exc),
            )
        finally:
            result.finished_at = datetime.now(timezone.utc)
            self._write_result(result)

        return result

    def _next_launchable(self) -> dict | None:
        launchable = {
            "BUILT",
            "READY_TO_PUBLISH",
            "PUBLISHED",
            "SITE_LIVE",
            "BILLING_TEST",
            "LAUNCH_FAILED",
        }
        for row in self.build_queue._read():
            if row.get("status") in launchable:
                return row
        return None

    @staticmethod
    def _public_runtime_env() -> dict[str, str]:
        keys = [
            "NEXT_PUBLIC_LEGAL_BUSINESS_NAME",
            "NEXT_PUBLIC_SUPPORT_EMAIL",
            "NEXT_PUBLIC_REFUND_POLICY_TEXT",
        ]
        return {
            key: os.getenv(key, "").strip()
            for key in keys
        }

    @staticmethod
    def _merge_compliance(
        source: ComplianceReport,
        runtime: ComplianceReport,
    ) -> ComplianceReport:
        return ComplianceReport(
            passed=source.passed and runtime.passed,
            checked_pages=source.checked_pages,
            errors=source.errors + runtime.errors,
            warnings=source.warnings + runtime.warnings,
        )

    @staticmethod
    def _write_runtime_env_hint(
        release_dir: Path,
        values: dict[str, str],
    ) -> None:
        safe_values = {}
        for key, value in values.items():
            if not value:
                continue
            upper = key.upper()
            is_secret = any(
                marker in upper
                for marker in ("SECRET", "TOKEN", "KEY", "API_KEY")
            )
            safe_values[key] = "***configured***" if is_secret else value

        path = release_dir / ".factory" / "runtime_env.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(safe_values, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _write_result(result: LaunchResult) -> None:
        folder = Path("releases") / result.product_slug / ".factory"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "launch_result.json").write_text(
            json.dumps(
                result.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
