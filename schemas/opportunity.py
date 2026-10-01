from typing import List
from pydantic import BaseModel, Field, HttpUrl


class Evidence(BaseModel):
    source: str
    quote: str
    url: HttpUrl | None = None


class Opportunity(BaseModel):
    title: str
    problem: str
    target_user: str
    proposed_solution: str
    evidence: List[Evidence] = Field(default_factory=list)

    cluster_id: str = ""
    signal_count: int = 0
    source_count: int = 0
    commercial_intent_score: float = Field(default=0, ge=0, le=10)
    evidence_quality_score: float = Field(default=0, ge=0, le=10)

    pain_score: float = Field(ge=0, le=10)
    demand_score: float = Field(ge=0, le=10)
    willingness_to_pay: float = Field(ge=0, le=10)
    competition_score: float = Field(ge=0, le=10, description="10 means crowded")
    build_ease_score: float = Field(ge=0, le=10, description="10 means easy for an AI-first team")
    acquisition_score: float = Field(ge=0, le=10)

    total_score: float = 0
    decision: str = "UNSCORED"
