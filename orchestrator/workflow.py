import os
from agents.scout import ScoutAgent
from reports.json_report import write_report
from scoring.engine import score_opportunity


class FactoryWorkflow:
    def __init__(self) -> None:
        self.scout = ScoutAgent()
        self.min_score = float(os.getenv("FACTORY_MIN_SCORE", "65"))
        self.top_n = int(os.getenv("SCOUT_TOP_N", "20"))

    def run_discovery(self, write_json: bool = True):
        opportunities = self.scout.discover()
        scored = [score_opportunity(x, self.min_score) for x in opportunities]
        ranked = sorted(scored, key=lambda x: x.total_score, reverse=True)[: self.top_n]
        report_path = write_report(ranked, self.scout.last_signals) if write_json else None
        return ranked, report_path
