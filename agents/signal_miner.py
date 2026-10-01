import re
from schemas.signal import DemandSignal

PAIN_PATTERNS = {
    "manual_work": r"\b(manual|manually|tedious|repetitive|copy.?paste)\b",
    "missing_tool": r"\b(wish|need|looking for|is there|any tool|feature request)\b",
    "too_expensive": r"\b(expensive|overpriced|pricing|costs? too much)\b",
    "too_complex": r"\b(complex|complicated|bloated|overkill|hard to use)\b",
    "automation": r"\b(automate|automation|automatically|workflow)\b",
    "integration": r"\b(integrat(?:e|ion)|api|webhook|sync)\b",
    "spreadsheet": r"\b(spreadsheet|excel|google sheets|csv)\b",
}


class SignalMiner:
    def analyze(self, signal: DemandSignal) -> DemandSignal:
        text = signal.fingerprint_text
        matches = [name for name, pattern in PAIN_PATTERNS.items() if re.search(pattern, text, re.I)]
        signal.matched_patterns = matches
        pattern_score = min(7.0, len(matches) * 1.7)
        engagement_bonus = min(3.0, signal.engagement / 20.0)
        signal.signal_strength = round(min(10.0, pattern_score + engagement_bonus), 2)
        return signal

    def keep(self, signal: DemandSignal, threshold: float = 2.0) -> bool:
        return signal.signal_strength >= threshold
