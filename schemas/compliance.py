from pydantic import BaseModel, ConfigDict, Field


class ComplianceReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    checked_pages: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
