from agents.commercial_intent import CommercialIntentMiner
from schemas.signal import DemandSignal


def test_business_budget_signal_scores_higher():
    item = DemandSignal(
        source="test",
        external_id="1",
        title="Our agency pays too much and needs a cheaper API every week",
        text="We manually copy results for clients.",
        url="https://example.com/1",
        engagement=15,
    )
    score, tags = CommercialIntentMiner().score_signal(item)
    assert score >= 5
    assert "budget" in tags
    assert "business" in tags
