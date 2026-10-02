from agents.semantic_clusterer import SemanticClusterer
from schemas.signal import DemandSignal


def signal(i, title):
    return DemandSignal(
        source="test",
        external_id=str(i),
        title=title,
        url=f"https://example.com/{i}",
        signal_strength=6,
        matched_patterns=["automation"],
    )


def test_related_workflows_cluster_together():
    items = [
        signal(1, "Automate weekly CSV report generation for clients"),
        signal(2, "Need automation for weekly CSV client reports"),
        signal(3, "VR headset rendering bug on Android"),
    ]
    clusters = SemanticClusterer(threshold=0.20).cluster(items)
    assert any(len(x.signals) >= 2 for x in clusters)
