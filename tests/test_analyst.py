from agents.analyst import AnalystAgent
from schemas.opportunity import Evidence, Opportunity
from scoring.engine import score_opportunity


def test_analyst_fallback_returns_actionable_report():
    item = Opportunity(
        title="CSV reporting automation",
        problem="Agencies manually create recurring client CSV reports.",
        target_user="Small agencies",
        proposed_solution="Automate recurring report generation.",
        evidence=[
            Evidence(source="hn", quote="We do this manually every week.", url="https://example.com/1"),
            Evidence(source="github", quote="Feature request: automate CSV reports.", url="https://example.com/2"),
        ],
        pain_score=8,
        demand_score=8,
        willingness_to_pay=7,
        competition_score=5,
        build_ease_score=8,
        acquisition_score=7,
        commercial_intent_score=7,
        evidence_quality_score=8,
        source_count=2,
        signal_count=2,
    )
    item = score_opportunity(item)
    report = AnalystAgent().analyze(item, web_research=False)
    assert report.recommendation in {"BUILD", "VALIDATE", "WATCH", "REJECT"}
    assert report.mvp_features
    assert len(report.source_urls) == 2
