from agents.product_manager import ProductManagerAgent
from schemas.analysis import AnalystReport


def report(recommendation="BUILD"):
    return AnalystReport(
        opportunity_title="Weekly client CSV automation",
        target_user="Small marketing agencies",
        job_to_be_done="Generate recurring client reports from CSV inputs.",
        evidence_summary="4 evidence items across 2 sources.",
        commercial_intent_score=8,
        urgency_score=7,
        frequency_score=9,
        budget_score=7,
        competitors=[],
        pricing_low_usd=19,
        pricing_high_usd=49,
        pricing_model="monthly subscription",
        mvp_features=["upload CSV", "generate report", "export result"],
        acquisition_channels=["SEO", "agency communities"],
        risks=["narrow willingness-to-pay not yet proven"],
        source_urls=["https://example.com/1"],
        analyst_score=82,
        recommendation=recommendation,
        rationale="Strong repeated workflow pain.",
    )


def test_build_report_becomes_builder_ready():
    package = ProductManagerAgent().productize(report("BUILD"))
    assert package.readiness == "READY_FOR_BUILD"
    assert package.builder_manifest.status == "READY_FOR_BUILD"
    assert package.builder_manifest.tasks
    assert package.prd.in_scope


def test_validate_report_is_blocked_from_builder():
    package = ProductManagerAgent().productize(report("VALIDATE"))
    assert package.readiness == "BLOCKED_FOR_VALIDATION"
    assert package.validation_experiments
