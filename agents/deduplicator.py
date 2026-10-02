import re
from difflib import SequenceMatcher
from schemas.signal import DemandSignal


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


class SignalDeduplicator:
    def dedupe(self, signals: list[DemandSignal], threshold: float = 0.88) -> list[DemandSignal]:
        kept: list[DemandSignal] = []
        normalized: list[str] = []
        seen_ids: set[tuple[str, str]] = set()
        for signal in sorted(signals, key=lambda x: x.signal_strength, reverse=True):
            key = (signal.source, signal.external_id)
            if key in seen_ids:
                continue
            current = normalize(signal.title)
            if any(SequenceMatcher(None, current, old).ratio() >= threshold for old in normalized if old):
                continue
            kept.append(signal)
            normalized.append(current)
            seen_ids.add(key)
        return kept
