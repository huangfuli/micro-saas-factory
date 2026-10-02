from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class DemandSignal(BaseModel):
    source: str
    external_id: str
    title: str
    text: str = ""
    url: HttpUrl
    author: str | None = None
    created_at: datetime | None = None
    engagement: int = 0
    matched_patterns: list[str] = Field(default_factory=list)
    signal_strength: float = Field(default=0, ge=0, le=10)

    @property
    def fingerprint_text(self) -> str:
        return (self.title + " " + self.text).strip().lower()
