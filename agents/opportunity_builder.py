import re
from collections import defaultdict
from schemas.opportunity import Evidence, Opportunity
from schemas.signal import DemandSignal


class OpportunityBuilder:
    """Groups related pain signals into auditable opportunity candidates.

    v0.2 deliberately uses deterministic heuristics. A later Analyst agent will
    enrich target users, competitors and pricing with model-assisted research.
    """

    def build(self, signals: list[DemandSignal]) -> list[Opportunity]:
        groups: dict[str, list[DemandSignal]] = defaultdict(list)
        for signal in signals:
            key = signal.matched_patterns[0] if signal.matched_patterns else "other"
            groups[key].append(signal)

        opportunities = []
        for theme, items in groups.items():
            items = sorted(items, key=lambda x: x.signal_strength, reverse=True)[:5]
            if not items:
                continue
            avg_strength = sum(x.signal_strength for x in items) / len(items)
            evidence = [Evidence(source=x.source, quote=(x.title + (" — " + x.text[:220] if x.text else ""))[:500], url=x.url) for x in items]
            title = self._title(theme)
            opportunities.append(Opportunity(
                title=title,
                problem=f"Repeated public demand signals around {theme.replace('_', ' ')} workflows.",
                target_user="Developers, operators and small online businesses",
                proposed_solution=f"A focused MicroSaaS that removes {theme.replace('_', ' ')} friction with a narrow automated workflow.",
                evidence=evidence,
                pain_score=min(10, 4.5 + avg_strength * 0.55),
                demand_score=min(10, 4.0 + len(items) * 0.8 + avg_strength * 0.25),
                willingness_to_pay=min(10, 4.0 + (1.2 if theme in {"too_expensive", "manual_work", "integration"} else 0.5) + avg_strength * 0.25),
                competition_score=5.0,
                build_ease_score=7.0,
                acquisition_score=min(10, 4.5 + len({x.source for x in items}) + len(items) * 0.35),
            ))
        return opportunities

    @staticmethod
    def _title(theme: str) -> str:
        names = {
            "manual_work": "Manual Workflow Automation Opportunity",
            "missing_tool": "Missing Tool / Feature Opportunity",
            "too_expensive": "Lower-Cost Focused Alternative Opportunity",
            "too_complex": "Simpler Vertical Tool Opportunity",
            "automation": "Workflow Automation Opportunity",
            "integration": "Integration & Sync Opportunity",
            "spreadsheet": "Spreadsheet-to-App Opportunity",
        }
        return names.get(theme, "Emerging MicroSaaS Opportunity")
