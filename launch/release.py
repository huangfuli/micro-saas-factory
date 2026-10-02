import json
import shutil
from pathlib import Path
from schemas.launch import ReleaseManifest
from schemas.product import ProductPackage


IGNORE = shutil.ignore_patterns(
    "node_modules",
    ".next",
    ".git",
    ".vercel",
    ".env",
    ".env.local",
)


class ReleaseManager:
    def __init__(
        self,
        builds_root: str = "builds",
        products_root: str = "products",
        releases_root: str = "releases",
    ):
        self.builds_root = Path(builds_root)
        self.products_root = Path(products_root)
        self.releases_root = Path(releases_root)

    def prepare(self, slug: str, clean: bool = True) -> ReleaseManifest:
        workspace = self.builds_root / slug
        product_path = self.products_root / slug / "product.json"
        build_result = workspace / ".factory" / "build_result.json"

        if not workspace.exists():
            raise FileNotFoundError(f"Missing build workspace: {workspace}")
        if not product_path.exists():
            raise FileNotFoundError(f"Missing product package: {product_path}")
        if not build_result.exists():
            raise FileNotFoundError(f"Missing Builder audit file: {build_result}")

        build_payload = json.loads(build_result.read_text(encoding="utf-8"))
        if build_payload.get("status") != "BUILT":
            raise ValueError("Only BUILT workspaces can enter Launch.")

        package = ProductPackage.model_validate_json(
            product_path.read_text(encoding="utf-8")
        )
        release_dir = self.releases_root / slug

        if clean and release_dir.exists():
            shutil.rmtree(release_dir)
        shutil.copytree(workspace, release_dir, ignore=IGNORE)

        archive_base = self.releases_root / f"{slug}-0.1.0"
        archive_path = shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=release_dir,
        )

        manifest = ReleaseManifest(
            product_slug=slug,
            workspace=str(workspace),
            release_dir=str(release_dir),
            archive_path=archive_path,
            required_env=package.builder_manifest.required_env,
        )
        (release_dir / ".factory").mkdir(exist_ok=True)
        (release_dir / ".factory" / "release_manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return manifest
