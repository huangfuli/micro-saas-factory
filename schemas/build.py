from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class GeneratedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    content: str


class CodeBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str
    files: list[GeneratedFile] = Field(default_factory=list)
    verification_commands: list[str] = Field(default_factory=list)


class BuildResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_slug: str
    status: Literal["BUILT", "FAILED", "DRY_RUN"]
    workspace: str
    generated_files: list[str] = Field(default_factory=list)
    completed_tasks: list[str] = Field(default_factory=list)
    failed_task: str | None = None
    qa_commands: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
