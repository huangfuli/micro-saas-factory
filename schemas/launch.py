from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from schemas.compliance import ComplianceReport


class ReleaseManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_slug: str
    version: str = "0.1.0"
    workspace: str
    release_dir: str
    archive_path: str
    github_repo: str | None = None
    deployment_provider: str = "vercel"
    billing_provider: str = "lemon_squeezy"
    required_env: list[str] = Field(default_factory=list)
    smoke_paths: list[str] = Field(
        default_factory=lambda: [
            "/",
            "/pricing",
            "/privacy",
            "/terms",
            "/refund-policy",
            "/contact",
            "/api/health",
        ]
    )


class BillingProvision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = "lemon_squeezy"
    store_id: str | None = None
    product_id: str | None = None
    variant_id: str | None = None
    checkout_url: str | None = None
    webhook_id: str | None = None
    monthly_amount_usd: float | None = None
    test_mode: bool | None = None


class LaunchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_slug: str
    status: Literal[
        "READY_TO_PUBLISH",
        "PUBLISHED",
        "SITE_LIVE",
        "BILLING_TEST",
        "LIVE",
        "FAILED",
    ]
    release_dir: str
    archive_path: str
    github_repo: str | None = None
    deployment_url: str | None = None
    billing: BillingProvision = Field(default_factory=BillingProvision)
    compliance: ComplianceReport | None = None
    smoke_results: dict[str, bool] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
