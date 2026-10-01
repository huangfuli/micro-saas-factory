import json
from pathlib import Path

from agents.product_manager import ProductManagerAgent
from builder.agent import BuilderAgent
from builder.queue import BuilderQueue
from reports.product_package import write_product_package
from tests.test_product_manager import report


def test_builder_creates_workspace_without_external_commands(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package = ProductManagerAgent().productize(report("BUILD"))
    write_product_package(package)

    queue = BuilderQueue("data/build_queue.jsonl")
    assert queue.enqueue(package)

    agent = BuilderAgent(queue=queue)
    result = agent.build_next(use_ai=False, install=False, qa=False)

    assert result is not None
    assert result.status == "DRY_RUN"
    workspace = Path(result.workspace)
    assert (workspace / "package.json").exists()
    assert (workspace / "src/app/page.tsx").exists()
    assert (workspace / "docs/PRD.md").exists()\n    assert (workspace / "src/app/api/billing/checkout/route.ts").exists()\n    env_text = (workspace / ".env.example").read_text(encoding="utf-8")\n    assert "STRIPE_PRICE_ID=" in env_text

    rows = [
        json.loads(x)
        for x in Path("data/build_queue.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert rows[0]["status"] == "SCAFFOLDED"
