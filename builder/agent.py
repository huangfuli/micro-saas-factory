import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from builder.codegen import OpenAICodegenProvider
from builder.queue import BuilderQueue
from builder.runtime import Runtime
from builder.scaffold import NextJsScaffolder
from schemas.build import BuildResult
from schemas.product import ProductPackage


class BuilderAgent:
    def __init__(
        self,
        queue: BuilderQueue | None = None,
        builds_root: str = "builds",
        products_root: str = "products",
    ):
        self.queue = queue or BuilderQueue()
        self.builds_root = Path(builds_root)
        self.products_root = Path(products_root)
        self.runtime = Runtime()
        self.scaffolder = NextJsScaffolder()
        self.codegen = OpenAICodegenProvider()

    def build_next(
        self,
        use_ai: bool = False,
        install: bool = False,
        qa: bool = False,
        clean: bool = False,
    ) -> BuildResult | None:
        job = self.queue.claim_next()
        if not job:
            return None

        slug = job["product_slug"]
        workspace = self.builds_root / slug
        result = BuildResult(product_slug=slug, status="DRY_RUN", workspace=str(workspace))

        try:
            self.queue.update_status(slug, "BUILDING")
            package = self._load_package(slug)
            if package.readiness != "READY_FOR_BUILD":
                raise ValueError("Builder received a product that is not READY_FOR_BUILD.")

            if clean and workspace.exists():
                shutil.rmtree(workspace)

            result.generated_files.extend(self.scaffolder.create(workspace, package))
            self._copy_product_docs(slug, workspace)

            if use_ai:
                bundle = self.codegen.generate(package)
                result.generated_files.extend(self.codegen.apply(workspace, bundle))

            result.generated_files.extend(
                self._apply_product_overrides(slug, workspace)
            )

            result.completed_tasks.extend(["T001", "T005"])
            qa_commands = [["npm", "run", "lint"], ["npm", "run", "build"]]
            result.qa_commands = [" ".join(x) for x in qa_commands]

            if install or qa:
                if not self.runtime.which("npm"):
                    raise RuntimeError(
                        "npm was not found. Install Node.js 20.9+ before executable builds."
                    )
                self.runtime.run(["npm", "install"], workspace, timeout=1200)

            if qa:
                for command in qa_commands:
                    self.runtime.run(command, workspace, timeout=1200)
                result.completed_tasks.append("T006")
                result.status = "BUILT"
                self.queue.update_status(slug, "BUILT")
            else:
                result.status = "DRY_RUN"
                self.queue.update_status(slug, "SCAFFOLDED")

        except Exception as exc:
            result.status = "FAILED"
            result.errors.append(str(exc))
            self.queue.update_status(slug, "FAILED", error=str(exc))
        finally:
            result.finished_at = datetime.now(timezone.utc)
            self._write_result(workspace, result)

        return result

    def _load_package(self, slug: str) -> ProductPackage:
        path = self.products_root / slug / "product.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing product package: {path}")
        return ProductPackage.model_validate_json(path.read_text(encoding="utf-8"))

    def _copy_product_docs(self, slug: str, workspace: Path) -> None:
        source = self.products_root / slug
        target = workspace / "docs"
        target.mkdir(parents=True, exist_ok=True)
        names = [
            "PRD.md",
            "LANDING_PAGE.md",
            "VALIDATION.md",
            "TECH_SPEC.md",
            "TASKS.md",
            "builder_manifest.json",
        ]
        for name in names:
            src = source / name
            if src.exists():
                shutil.copy2(src, target / name)

    def _apply_product_overrides(
        self,
        slug: str,
        workspace: Path,
    ) -> list[str]:
        source = self.products_root / slug / "overrides"
        if not source.exists():
            return []

        written = []
        for src in source.rglob("*"):
            if not src.is_file():
                continue
            relative = src.relative_to(source)
            if relative.parts[0] not in {"src", "docs"}:
                raise ValueError(
                    "Product overrides may only write under src/ or docs/: "
                    + str(relative)
                )
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            written.append(str(relative).replace("\\", "/"))
        return written

    @staticmethod
    def _write_result(workspace: Path, result: BuildResult) -> None:
        folder = workspace / ".factory"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "build_result.json").write_text(
            json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
