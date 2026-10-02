import json
from pathlib import Path

from agents.product_manager import ProductManagerAgent
from builder.agent import BuilderAgent
from builder.queue import BuilderQueue
from reports.product_package import write_product_package
from tests.test_product_manager import report


def test_builder_creates_review_ready_workspace_without_external_commands(
    tmp_path,
    monkeypatch,
):
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
    assert (workspace / "docs/PRD.md").exists()
    assert (workspace / "src/app/pricing/page.tsx").exists()
    assert (workspace / "src/app/privacy/page.tsx").exists()
    assert (workspace / "src/app/terms/page.tsx").exists()
    assert (workspace / "src/app/refund-policy/page.tsx").exists()
    assert (workspace / "src/app/contact/page.tsx").exists()
    assert (workspace / "src/app/api/billing/checkout/route.ts").exists()
    assert (workspace / "src/app/api/billing/webhook/route.ts").exists()

    env_text = (workspace / ".env.example").read_text(encoding="utf-8")
    assert "LEMON_SQUEEZY_API_KEY=" in env_text
    assert "LEMON_SQUEEZY_STORE_ID=" in env_text
    assert "LEMON_SQUEEZY_VARIANT_ID=" in env_text
    assert "LEMON_SQUEEZY_WEBHOOK_SECRET=" in env_text
    assert "STRIPE_" not in env_text

    rows = [
        json.loads(x)
        for x in Path("data/build_queue.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert rows[0]["status"] == "SCAFFOLDED"
