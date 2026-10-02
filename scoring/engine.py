from schemas.opportunity import Opportunity

WEIGHTS = {
    "pain_score": 0.17,
    "demand_score": 0.16,
    "willingness_to_pay": 0.18,
    "competition_advantage": 0.08,
    "build_ease_score": 0.10,
    "acquisition_score": 0.10,
    "commercial_intent_score": 0.13,
    "evidence_quality_score": 0.08,
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
        + item.commercial_intent_score * WEIGHTS["commercial_intent_score"]
        + item.evidence_quality_score * WEIGHTS["evidence_quality_score"]
    )
    item.total_score = round(weighted_10 * 10, 2)

    # Two distinct evidence items are required before an idea can enter product validation.
    evidence_ok = len(item.evidence) >= 2
    item.decision = "PASS" if item.total_score >= min_score and evidence_ok else "REJECT"
    return item
