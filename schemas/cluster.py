from pydantic import BaseModel, Field
from schemas.signal import DemandSignal


class SignalCluster(BaseModel):
    cluster_id: str
    label: str
    signals: list[DemandSignal] = Field(default_factory=list)
    dominant_patterns: list[str] = Field(default_factory=list)
    commercial_tags: list[str] = Field(default_factory=list)
    source_count: int = 0
    avg_signal_strength: float = 0
    commercial_intent_score: float = 0
