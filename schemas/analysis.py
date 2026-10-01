from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Competitor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url: str
    pricing: str
    positioning: str


class AnalystReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_title: str
    target_user: str
    job_to_be_done: str
    evidence_summary: str
    commercial_intent_score: float = Field(ge=0, le=10)
    urgency_score: float = Field(ge=0, le=10)
    frequency_score: float = Field(ge=0, le=10)
    budget_score: float = Field(ge=0, le=10)
    competitors: list[Competitor]
    pricing_low_usd: float = Field(ge=0)
    pricing_high_usd: float = Field(ge=0)
    pricing_model: str
    mvp_features: list[str]
    acquisition_channels: list[str]
    risks: list[str]
    source_urls: list[str]
    analyst_score: float = Field(ge=0, le=100)
    recommendation: Literal["BUILD", "VALIDATE", "WATCH", "REJECT"]
    rationale: str
