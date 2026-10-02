from schemas.cluster import SignalCluster
from schemas.opportunity import Evidence, Opportunity


class OpportunityBuilder:
    """Turns semantic demand clusters into auditable product hypotheses."""

    def build(self, clusters: list[SignalCluster]) -> list[Opportunity]:
        opportunities = []
        for cluster in clusters:
            items = sorted(cluster.signals, key=lambda x: x.signal_strength, reverse=True)[:8]
            if not items:
                continue

            evidence = [
                Evidence(
                    source=x.source,
                    quote=(x.title + (" — " + x.text[:220] if x.text else ""))[:500],
                    url=x.url,
                )
                for x in items
            ]
            avg_strength = cluster.avg_signal_strength
            evidence_quality = min(
                10.0,
                2.0
                + min(5.0, len(items) * 0.65)
                + min(2.0, cluster.source_count * 0.8)
                + avg_strength * 0.15,
            )
            primary = cluster.dominant_patterns[0] if cluster.dominant_patterns else "workflow"
            title = self._title(primary, cluster.label)

            build_ease = 7.5
            if "integration" in cluster.dominant_patterns:
                build_ease -= 0.7

            opportunities.append(Opportunity(
                title=title,
                problem=f"Repeated public demand signals describe friction around: {cluster.label}.",
                target_user="Developers, operators and small online businesses exhibiting this repeated workflow pain",
                proposed_solution="A narrow MicroSaaS that automates the repeated job-to-be-done with minimal setup.",
                evidence=evidence,
                cluster_id=cluster.cluster_id,
                signal_count=len(cluster.signals),
                source_count=cluster.source_count,
                commercial_intent_score=cluster.commercial_intent_score,
                evidence_quality_score=round(evidence_quality, 2),
                pain_score=min(10, 4.0 + avg_strength * 0.62),
                demand_score=min(10, 3.2 + len(items) * 0.62 + cluster.source_count * 0.7),
                willingness_to_pay=min(10, 3.0 + cluster.commercial_intent_score * 0.62),
                competition_score=5.0,
                build_ease_score=max(0, build_ease),
                acquisition_score=min(10, 3.8 + len(items) * 0.32 + cluster.source_count * 0.8),
            ))
        return opportunities

    @staticmethod
    def _title(theme: str, label: str) -> str:
        names = {
            "manual_work": "Manual Workflow Automation",
            "missing_tool": "Missing Tool / Feature",
            "too_expensive": "Lower-Cost Focused Alternative",
            "too_complex": "Simpler Vertical Tool",
            "automation": "Workflow Automation",
            "integration": "Integration & Sync",
            "spreadsheet": "Spreadsheet-to-App",
        }
        prefix = names.get(theme, "Emerging MicroSaaS")
        clean = label.replace("_", " ").strip()
        return f"{prefix}: {clean}" if clean else prefix
