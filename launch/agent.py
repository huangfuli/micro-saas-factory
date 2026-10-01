import json
import os
from datetime import datetime, timezone
from pathlib import Path

from builder.queue import BuilderQueue
from launch.github_publish import GitHubPublisher
from launch.release import ReleaseManager
from launch.smoke import SmokeChecker
from launch.stripe import StripeProvisioner
from launch.vercel import VercelDeployer
from schemas.launch import LaunchResult
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
        self.stripe = StripeProvisioner()
        self.vercel = VercelDeployer()
        self.smoke = SmokeChecker()

    def prepare_next(
        self,
        publish_github: bool = False,
        provision_stripe: bool = False,
        deploy_vercel: bool = False,
    ) -> LaunchResult | None:
        job = self._next_launchable()
        if not job:
            return None

        slug = job["product_slug"]
        result = None

        try:
            manifest = self.release_manager.prepare(slug)
            result = LaunchResult(
                product_slug=slug,
                status="READY_TO_PUBLISH",
                release_dir=manifest.release_dir,
                archive_path=manifest.archive_path,
            )
            self.build_queue.update_status(slug, "READY_TO_PUBLISH")
            package = self._load_package(slug)

            if publish_github:
                result.github_repo = self.github.publish(
                    Path(manifest.release_dir),
                    slug,
                )
                result.status = "PUBLISHED"
                self.build_queue.update_status(slug, "PUBLISHED")

            runtime_env = {}
            if provision_stripe:
                low = self._pricing_floor(package.pricing_plan)
                result.billing = self.stripe.provision(
                    slug,
                    package.positioning.product_name,
                    low,
                )
                runtime_env = {
                    "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
                    "STRIPE_PRICE_ID": result.billing.price_id or "",
                    "STRIPE_WEBHOOK_SECRET": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
                }
                self._write_runtime_env_hint(
                    Path(manifest.release_dir),
                    runtime_env,
                )

            if deploy_vercel:
                result.deployment_url = self.vercel.deploy(
                    Path(manifest.release_dir),
                    production=True,
                    environment=runtime_env,
                )
                result.status = "DEPLOYED"
                self.build_queue.update_status(slug, "DEPLOYED")

                result.smoke_results = self.smoke.check(
                    result.deployment_url,
                    manifest.smoke_paths,
                )
                if result.smoke_results and all(result.smoke_results.values()):
                    result.status = "LIVE"
                    self.build_queue.update_status(slug, "LIVE")
                else:
                    raise RuntimeError(
                        f"Deployment smoke test failed: {result.smoke_results}"
                    )

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
            "DEPLOYED",
            "LAUNCH_FAILED",
        }
        for row in self.build_queue._read():
            if row.get("status") in launchable:
                return row
        return None

    def _load_package(self, slug: str) -> ProductPackage:
        path = self.products_root / slug / "product.json"
        return ProductPackage.model_validate_json(path.read_text(encoding="utf-8"))

    @staticmethod
    def _pricing_floor(text: str) -> float:
        import re
        values = [
            float(x)
            for x in re.findall(r"USD\s*(\d+(?:\.\d+)?)", text)
        ]
        return min(values) if values else 19.0

    @staticmethod
    def _write_runtime_env_hint(
        release_dir: Path,
        values: dict[str, str],
    ) -> None:
        safe_values = {
            key: ("***configured***" if "SECRET" in key or "KEY" in key else value)
            for key, value in values.items()
            if value
        }
        path = release_dir / ".factory" / "runtime_env.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(safe_values, indent=2),
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
