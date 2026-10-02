import math
import re
from collections import Counter
from uuid import uuid4
from agents.commercial_intent import CommercialIntentMiner
from schemas.cluster import SignalCluster
from schemas.signal import DemandSignal


STOPWORDS = {
    "the","a","an","and","or","to","of","for","in","on","with","is","are","it","this","that",
    "i","we","you","my","our","your","be","can","could","would","should","how","what","any",
    "there","from","as","at","by","do","does","not","have","has","need","want","looking"
}


def _tokens(text: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9]{2,}", text.lower()) if x not in STOPWORDS]


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    common = set(a).intersection(b)
    numerator = sum(a[x] * b[x] for x in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return numerator / (da * db) if da and db else 0.0


class SemanticClusterer:
    """Deterministic TF-IDF clustering; keeps Scout useful without an embedding API."""

    def __init__(self, threshold: float = 0.24):
        self.threshold = threshold
        self.intent = CommercialIntentMiner()

    def cluster(self, signals: list[DemandSignal]) -> list[SignalCluster]:
        if not signals:
            return []

        docs = [_tokens((x.title + " " + x.text[:1200])) for x in signals]
        df = Counter(term for doc in docs for term in set(doc))
        n = len(docs)
        vectors = []
        for doc in docs:
            tf = Counter(doc)
            vectors.append({
                term: count * (math.log((1 + n) / (1 + df[term])) + 1.0)
                for term, count in tf.items()
            })

        raw_clusters: list[list[int]] = []
        centroids: list[dict[str, float]] = []
        for idx, vector in enumerate(vectors):
            sims = [_cosine(vector, c) for c in centroids]
            best = max(range(len(sims)), key=sims.__getitem__) if sims else None
            if best is not None and sims[best] >= self.threshold:
                raw_clusters[best].append(idx)
                centroids[best] = self._centroid([vectors[i] for i in raw_clusters[best]])
            else:
                raw_clusters.append([idx])
                centroids.append(vector)

        clusters = []
        for indexes in raw_clusters:
            members = [signals[i] for i in indexes]
            pattern_counts = Counter(p for x in members for p in x.matched_patterns)
            commercial_score, commercial_tags = self.intent.score_cluster(members)
            top_terms = self._top_terms([vectors[i] for i in indexes])
            label = " / ".join(top_terms[:3]) or (pattern_counts.most_common(1)[0][0] if pattern_counts else "emerging")
            clusters.append(SignalCluster(
                cluster_id="clu_" + uuid4().hex[:10],
                label=label,
                signals=members,
                dominant_patterns=[x for x, _ in pattern_counts.most_common(4)],
                commercial_tags=commercial_tags,
                source_count=len({x.source for x in members}),
                avg_signal_strength=round(sum(x.signal_strength for x in members) / len(members), 2),
                commercial_intent_score=commercial_score,
            ))
        return sorted(
            clusters,
            key=lambda x: (x.commercial_intent_score, len(x.signals), x.avg_signal_strength),
            reverse=True,
        )

    @staticmethod
    def _centroid(vectors: list[dict[str, float]]) -> dict[str, float]:
        total = Counter()
        for vector in vectors:
            total.update(vector)
        return {k: v / len(vectors) for k, v in total.items()}

    @staticmethod
    def _top_terms(vectors: list[dict[str, float]]) -> list[str]:
        total = Counter()
        for vector in vectors:
            total.update(vector)
        return [term for term, _ in total.most_common(5)]
