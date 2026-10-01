import os
from agents.scout import ScoutAgent
from scoring.engine import score_opportunity


class FactoryWorkflow:
    def __init__(self) -> None:
        self.scout = ScoutAgent()
        self.min_score = float(os.getenv("FACTORY_MIN_SCORE", "65"))

    def run_discovery(self):
        opportunities = self.scout.discover()
        scored = [score_opportunity(x, self.min_score) for x in opportunities]
        return sorted(scored, key=lambda x: x.total_score, reverse=True)
