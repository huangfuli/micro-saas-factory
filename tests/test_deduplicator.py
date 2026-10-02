from agents.deduplicator import SignalDeduplicator
from schemas.signal import DemandSignal


def test_similar_titles_are_deduplicated():
    items = [
        DemandSignal(source="a", external_id="1", title="Need a tool to automate CSV reports", url="https://example.com/1", signal_strength=8),
        DemandSignal(source="b", external_id="2", title="Need a tool to automate CSV reports!", url="https://example.com/2", signal_strength=7),
    ]
    assert len(SignalDeduplicator().dedupe(items)) == 1
