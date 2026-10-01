from schemas.opportunity import Evidence, Opportunity
from scoring.engine import score_opportunity


def test_strong_opportunity_passes():
    item = Opportunity(
        title="Focused tool", problem="Repeated painful workflow", target_user="B2B team",
        proposed_solution="Automate it", evidence=[Evidence(source="test", quote="Need this")],
        pain_score=9, demand_score=9, willingness_to_pay=9, competition_score=3,
        build_ease_score=8, acquisition_score=8,
    )
    result = score_opportunity(item)
    assert result.total_score >= 65
    assert result.decision == "PASS"


def test_missing_evidence_rejects():
    item = Opportunity(
        title="Unsupported idea", problem="Unknown", target_user="Unknown", proposed_solution="Unknown",
        pain_score=10, demand_score=10, willingness_to_pay=10, competition_score=0,
        build_ease_score=10, acquisition_score=10,
    )
    assert score_opportunity(item).decision == "REJECT"
