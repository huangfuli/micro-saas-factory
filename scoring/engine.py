from schemas.opportunity import Opportunity

WEIGHTS = {
    "pain_score": 0.22,
    "demand_score": 0.20,
    "willingness_to_pay": 0.22,
    "competition_advantage": 0.10,
    "build_ease_score": 0.12,
    "acquisition_score": 0.14,
}


def score_opportunity(item: Opportunity, min_score: float = 65) -> Opportunity:
    competition_advantage = 10 - item.competition_score
    weighted_10 = (
        item.pain_score * WEIGHTS["pain_score"]
        + item.demand_score * WEIGHTS["demand_score"]
        + item.willingness_to_pay * WEIGHTS["willingness_to_pay"]
        + competition_advantage * WEIGHTS["competition_advantage"]
        + item.build_ease_score * WEIGHTS["build_ease_score"]
        + item.acquisition_score * WEIGHTS["acquisition_score"]
    )
    item.total_score = round(weighted_10 * 10, 2)
    evidence_ok = len(item.evidence) >= 1
    item.decision = "PASS" if item.total_score >= min_score and evidence_ok else "REJECT"
    return item
