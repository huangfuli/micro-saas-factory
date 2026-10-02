import json
from pathlib import Path

from agents.product_manager import ProductManagerAgent
from builder.queue import BuilderQueue
from launch.agent import LaunchAgent
from launch.compliance import REQUIRED_PAGES
from reports.product_package import write_product_package
from tests.test_product_manager import report


def test_launch_prepare_stops_before_external_publish(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package = ProductManagerAgent().productize(report("BUILD"))
    write_product_package(package)

    queue = BuilderQueue("data/build_queue.jsonl")
    assert queue.enqueue(package)
    queue.update_status(package.builder_manifest.product_slug, "BUILT")

    workspace = Path("builds") / package.builder_manifest.product_slug
    (workspace / ".factory").mkdir(parents=True)

    for relative in REQUIRED_PAGES.values():
        page = workspace / relative
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            "This page accurately describes the SaaS product and its current "
            "features, pricing, legal information, support process, and "
            "subscription billing through Lemon Squeezy. " * 4,
            encoding="utf-8",
        )

    (workspace / ".factory" / "build_result.json").write_text(
        json.dumps({"status": "BUILT"}),
        encoding="utf-8",
    )

    result = LaunchAgent(build_queue=queue).prepare_next()
    assert result is not None
    assert result.status == "READY_TO_PUBLISH"
    assert result.compliance is not None
    assert result.compliance.passed is True
    assert Path(result.archive_path).exists()
