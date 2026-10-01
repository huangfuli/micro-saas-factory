import json
import logging
import os
from schemas.analysis import AnalystReport
from schemas.opportunity import Opportunity

log = logging.getLogger(__name__)


class AnalystAgent:
    """Turns an evidence-backed opportunity into a commercial product thesis."""

    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-6-astra")

    def analyze(self, opportunity: Opportunity, web_research: bool = False) -> AnalystReport:
        if web_research and os.getenv("OPENAI_API_KEY"):
            try:
                return self._analyze_with_web(opportunity)
            except Exception as exc:
                log.warning("Live Analyst research failed; using deterministic fallback: %s", exc)
        return self._fallback(opportunity)

    def _analyze_with_web(self, opportunity: Opportunity) -> AnalystReport:
        from openai import OpenAI

        evidence = [
            {"source": x.source, "quote": x.quote, "url": str(x.url) if x.url else ""}
            for x in opportunity.evidence
        ]
        prompt = f"""
You are a MicroSaaS investment analyst. Research this product opportunity on the live web.

Opportunity: {opportunity.title}
Problem: {opportunity.problem}
Target user hypothesis: {opportunity.target_user}
Solution hypothesis: {opportunity.proposed_solution}
Demand evidence: {json.dumps(evidence, ensure_ascii=False)}

Tasks:
1. Verify that the problem exists beyond the supplied evidence.
2. Identify direct and adjacent competitors and their public pricing when available.
3. Estimate a realistic initial USD pricing range for a narrow MicroSaaS.
4. Define a small MVP, likely acquisition channels, and the main commercial risks.
5. Score commercial intent, urgency, usage frequency, budget evidence, and overall attractiveness.
6. Use BUILD only when evidence is unusually strong; otherwise prefer VALIDATE.
7. Put the web pages used into source_urls. Never invent a company, price, URL, or evidence.
"""
        schema = AnalystReport.model_json_schema()
        client = OpenAI()
        response = client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            include=["web_search_call.action.sources"],
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "analyst_report",
                    "strict": True,
                    "schema": schema,
                }
            },
            store=False,
        )
        return AnalystReport.model_validate_json(response.output_text)

    def _fallback(self, opportunity: Opportunity) -> AnalystReport:
        evidence_urls = [str(x.url) for x in opportunity.evidence if x.url]
        commercial = opportunity.commercial_intent_score
        urgency = min(10.0, 3.5 + opportunity.pain_score * 0.45)
        frequency = min(10.0, 3.0 + opportunity.demand_score * 0.5)
        budget = min(10.0, 2.5 + opportunity.willingness_to_pay * 0.55)
        analyst_score = round(
            opportunity.total_score * 0.55
            + commercial * 2.0
            + opportunity.evidence_quality_score * 1.5
            + budget,
            2,
        )
        analyst_score = min(100.0, analyst_score)
        if analyst_score >= 76:
            recommendation = "BUILD"
        elif analyst_score >= 62:
            recommendation = "VALIDATE"
        elif analyst_score >= 48:
            recommendation = "WATCH"
        else:
            recommendation = "REJECT"

        low = 9.0 if budget < 6 else 19.0
        high = 29.0 if budget < 7 else 49.0
        return AnalystReport(
            opportunity_title=opportunity.title,
            target_user=opportunity.target_user,
            job_to_be_done=opportunity.problem,
            evidence_summary=f"{len(opportunity.evidence)} evidence items across {opportunity.source_count or 1} source(s).",
            commercial_intent_score=commercial,
            urgency_score=round(urgency, 2),
            frequency_score=round(frequency, 2),
            budget_score=round(budget, 2),
            competitors=[],
            pricing_low_usd=low,
            pricing_high_usd=high,
            pricing_model="monthly subscription; validate willingness-to-pay before implementation",
            mvp_features=[
                "one core workflow solving the repeated pain",
                "simple onboarding and result export",
                "usage limits and basic account management",
            ],
            acquisition_channels=["problem-keyword SEO", "communities where source evidence appeared", "direct outreach to early users"],
            risks=["competition/pricing not yet live-researched", "cluster may combine adjacent jobs-to-be-done", "willingness-to-pay requires interview or preorder validation"],
            source_urls=evidence_urls,
            analyst_score=analyst_score,
            recommendation=recommendation,
            rationale="Fallback analysis uses observed demand evidence and Scout scores; run with --web-research for current competitor and pricing verification.",
        )
