import logging
from agents.deduplicator import SignalDeduplicator
from agents.opportunity_builder import OpportunityBuilder
from agents.semantic_clusterer import SemanticClusterer
from agents.signal_miner import SignalMiner
from sources.github_issues import GitHubIssuesSource
from sources.hackernews import HackerNewsSource

log = logging.getLogger(__name__)


class ScoutAgent:
    """v0.3 live discovery: mine -> dedupe -> semantic cluster -> opportunity."""

    def __init__(self, sources=None):
        self.sources = sources or [HackerNewsSource(), GitHubIssuesSource()]
        self.miner = SignalMiner()
        self.deduplicator = SignalDeduplicator()
        self.clusterer = SemanticClusterer()
        self.builder = OpportunityBuilder()
        self.last_signals = []
        self.last_clusters = []

    def discover(self, per_source: int = 40):
        raw = []
        for source in self.sources:
            try:
                raw.extend(source.fetch(limit=per_source))
            except Exception as exc:
                log.warning("Scout source %s failed: %s", source.name, exc)

        mined = [self.miner.analyze(x) for x in raw]
        useful = [x for x in mined if self.miner.keep(x)]
        self.last_signals = self.deduplicator.dedupe(useful)
        self.last_clusters = self.clusterer.cluster(self.last_signals)
        return self.builder.build(self.last_clusters)
