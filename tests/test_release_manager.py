import json
from pathlib import Path

from agents.product_manager import ProductManagerAgent
from reports.product_package import write_product_package
from launch.release import ReleaseManager
from tests.test_product_manager import report


def test_only_built_workspace_can_be_released(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package = ProductManagerAgent().productize(report("BUILD"))
    write_product_package(package)

    workspace = Path("builds") / package.builder_manifest.product_slug
    (workspace / ".factory").mkdir(parents=True)
    (workspace / "src").mkdir()
    (workspace / "src" / "index.txt").write_text("ok", encoding="utf-8")
    (workspace / ".factory" / "build_result.json").write_text(
        json.dumps({"status": "BUILT"}),
        encoding="utf-8",
    )

    manifest = ReleaseManager().prepare(package.builder_manifest.product_slug)
    assert Path(manifest.release_dir).exists()
    assert Path(manifest.archive_path).exists()
    assert Path(manifest.release_dir, "src", "index.txt").exists()
