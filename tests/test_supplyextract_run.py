from pathlib import Path

from builder.agent import BuilderAgent
from builder.queue import BuilderQueue
from schemas.product import ProductPackage


ROOT = Path(__file__).resolve().parents[1]


def test_supplyextract_package_and_overrides_build_into_workspace(tmp_path):
    product_path = ROOT / "products" / "supplyextract" / "product.json"
    package = ProductPackage.model_validate_json(
        product_path.read_text(encoding="utf-8")
    )
    assert package.readiness == "READY_FOR_BUILD"
    assert package.positioning.product_name == "SupplyExtract"
    assert "bank-statement" not in package.positioning.one_liner.lower()

    queue = BuilderQueue(str(tmp_path / "build_queue.jsonl"))
    assert queue.enqueue(package) is True

    agent = BuilderAgent(
        queue=queue,
        builds_root=str(tmp_path / "builds"),
        products_root=str(ROOT / "products"),
    )
    result = agent.build_next(use_ai=False, install=False, qa=False)

    assert result is not None
    assert result.status == "DRY_RUN"

    workspace = Path(result.workspace)
    extract_route = (
        workspace / "src/app/api/extract/route.ts"
    ).read_text(encoding="utf-8")
    dashboard = (
        workspace / "src/app/dashboard/page.tsx"
    ).read_text(encoding="utf-8")
    privacy = (
        workspace / "src/app/privacy/page.tsx"
    ).read_text(encoding="utf-8")

    assert "api.openai.com/v1/responses" in extract_route
    assert "api.lemonsqueezy.com/v1/licenses/validate" in extract_route
    assert "MAX_PAID_BYTES = 10 * 1024 * 1024" in extract_route
    assert "Review line items" in dashboard
    assert "AI extraction can be incomplete or wrong" in dashboard
    assert "does not intentionally" in privacy
    assert "zero retention" in privacy
