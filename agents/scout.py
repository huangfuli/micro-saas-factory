from schemas.opportunity import Evidence, Opportunity


class ScoutAgent:
    """v0.1 deterministic Scout. v0.2 will ingest live public demand signals."""

    def discover(self) -> list[Opportunity]:
        return [
            Opportunity(
                title="AI Screenshot-to-SOP",
                problem="Small teams repeatedly turn screenshots into step-by-step internal SOPs.",
                target_user="Agencies, support teams and operations teams",
                proposed_solution="Upload screenshots and automatically generate an editable SOP with steps and annotations.",
                evidence=[Evidence(source="seed", quote="Teams repeatedly document browser workflows by hand.")],
                pain_score=7.5, demand_score=7.0, willingness_to_pay=7.0,
                competition_score=5.5, build_ease_score=8.5, acquisition_score=7.0,
            ),
            Opportunity(
                title="Generic AI Chatbot",
                problem="Users want another general-purpose chatbot.",
                target_user="Everyone",
                proposed_solution="A generic chat interface.",
                evidence=[Evidence(source="seed", quote="Generic AI chat is already widely available.")],
                pain_score=3.0, demand_score=5.0, willingness_to_pay=2.0,
                competition_score=10.0, build_ease_score=9.0, acquisition_score=2.0,
            ),
        ]
