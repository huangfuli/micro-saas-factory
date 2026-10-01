from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ProductPositioning(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_name: str
    one_liner: str
    target_user: str
    painful_job: str
    unique_value: str


class PRD(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objective: str
    user_story: str
    in_scope: list[str]
    out_of_scope: list[str]
    success_metrics: list[str]
    acceptance_criteria: list[str]


class LandingPage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    headline: str
    subheadline: str
    problem_bullets: list[str]
    solution_bullets: list[str]
    primary_cta: str
    pricing_anchor: str
    faq: list[str]


class ValidationExperiment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hypothesis: str
    audience: str
    channel: str
    offer: str
    primary_metric: str
    pass_threshold: str
    fail_threshold: str
    max_days: int = Field(ge=1, le=30)


class TechnicalSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    architecture: str
    frontend: str
    backend: str
    database: str
    integrations: list[str]
    entities: list[str]
    endpoints: list[str]
    non_functional_requirements: list[str]


class DevTask(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    description: str
    priority: Literal["P0", "P1", "P2"]
    acceptance: list[str]
    dependencies: list[str]


class BuilderManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_slug: str
    status: Literal["READY_FOR_BUILD", "BLOCKED_FOR_VALIDATION"]
    source_recommendation: Literal["BUILD", "VALIDATE"]
    build_goal: str
    tasks: list[DevTask]
    required_env: list[str]


class ProductPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_opportunity: str
    source_analyst_score: float = Field(ge=0, le=100)
    readiness: Literal["READY_FOR_BUILD", "BLOCKED_FOR_VALIDATION"]
    positioning: ProductPositioning
    prd: PRD
    landing_page: LandingPage
    validation_experiments: list[ValidationExperiment]
    pricing_plan: str
    technical_spec: TechnicalSpec
    builder_manifest: BuilderManifest
    risks: list[str]
