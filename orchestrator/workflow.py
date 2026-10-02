import os
from agents.analyst import AnalystAgent
from agents.product_manager import ProductManagerAgent
from agents.scout import ScoutAgent
from builder.queue import BuilderQueue
from reports.analysis_report import write_analysis_report
from reports.json_report import write_report
from reports.product_package import write_product_package
from scoring.engine import score_opportunity


class FactoryWorkflow:
    def __init__(self) -> None:
        self.scout = ScoutAgent()
        self.analyst = AnalystAgent()
        self.product_manager = ProductManagerAgent()
        self.builder_queue = BuilderQueue()
        self.min_score = float(os.getenv("FACTORY_MIN_SCORE", "65"))
        self.top_n = int(os.getenv("SCOUT_TOP_N", "20"))
        self.analyst_top_n = int(os.getenv("ANALYST_TOP_N", "5"))

    def run_discovery(self, write_json: bool = True):
        opportunities = self.scout.discover()
        scored = [score_opportunity(x, self.min_score) for x in opportunities]
        ranked = sorted(scored, key=lambda x: x.total_score, reverse=True)[: self.top_n]
        report_path = write_report(ranked, self.scout.last_signals) if write_json else None
        return ranked, report_path

    def run_analysis(self, opportunities, web_research: bool = False, write_json: bool = True):
        candidates = [x for x in opportunities if x.decision == "PASS"][: self.analyst_top_n]
        reports = [self.analyst.analyze(x, web_research=web_research) for x in candidates]
        reports = sorted(reports, key=lambda x: x.analyst_score, reverse=True)
        report_path = write_analysis_report(reports) if write_json else None
        return reports, report_path

    def run_productization(self, reports, use_ai: bool = False):
        eligible = [x for x in reports if x.recommendation in {"BUILD", "VALIDATE"}]
        outputs = []
        for report in eligible:
            package = self.product_manager.productize(report, use_ai=use_ai)
            folder = write_product_package(package)
            queued = self.builder_queue.enqueue(package)
            outputs.append({
                "package": package,
                "folder": str(folder),
                "queued": queued,
            })
        return outputs
