import re
from collections import Counter
from schemas.signal import DemandSignal


PATTERNS = {
    "budget": (r"\b(pay|paid|budget|price|pricing|subscription|cost|expensive|cheaper)\b", 2.2),
    "urgency": (r"\b(asap|urgent|urgently|blocked|right now|immediately|today)\b", 1.8),
    "frequency": (r"\b(daily|weekly|monthly|every day|every week|each time|repeatedly|often)\b", 1.6),
    "business": (r"\b(client|customer|business|agency|team|company|store|shop|revenue|sales)\b", 1.5),
    "workaround": (r"\b(manual|spreadsheet|excel|copy.?paste|script|zapier|notion|airtable)\b", 1.4),
    "replacement": (r"\b(alternative|replace|switch from|instead of|migrate)\b", 1.0),
    "integration": (r"\b(api|webhook|integration|sync|export|import)\b", 1.0),
}


class CommercialIntentMiner:
    def score_signal(self, signal: DemandSignal) -> tuple[float, list[str]]:
        text = signal.fingerprint_text
        tags = []
        score = 0.0
        for tag, (pattern, weight) in PATTERNS.items():
            if re.search(pattern, text, re.I):
                tags.append(tag)
                score += weight
        engagement_bonus = min(1.5, signal.engagement / 50.0)
        return round(min(10.0, score + engagement_bonus), 2), tags

    def score_cluster(self, signals: list[DemandSignal]) -> tuple[float, list[str]]:
        if not signals:
            return 0.0, []
        scored = [self.score_signal(x) for x in signals]
        avg = sum(x[0] for x in scored) / len(scored)
        tag_counts = Counter(tag for _, tags in scored for tag in tags)
        diversity_bonus = min(1.5, len(tag_counts) * 0.2)
        source_bonus = min(1.0, len({x.source for x in signals}) * 0.35)
        tags = [tag for tag, _ in tag_counts.most_common()]
        return round(min(10.0, avg + diversity_bonus + source_bonus), 2), tags
