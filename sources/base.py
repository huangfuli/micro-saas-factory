from abc import ABC, abstractmethod
from schemas.signal import DemandSignal


class SignalSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, limit: int = 50) -> list[DemandSignal]:
        raise NotImplementedError
