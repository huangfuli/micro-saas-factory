from agents.signal_miner import SignalMiner
from schemas.signal import DemandSignal


def test_pain_language_is_detected():
    signal = DemandSignal(source="test", external_id="1", title="Need to automate this manual workflow", url="https://example.com/1", engagement=20)
    mined = SignalMiner().analyze(signal)
    assert "manual_work" in mined.matched_patterns
    assert "automation" in mined.matched_patterns
    assert mined.signal_strength >= 4
