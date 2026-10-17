from dataclasses import dataclass
from pathlib import Path
@dataclass
class Prediction:
    detected: bool
    label: str | None
    confidence: float | None
    provider: str
class InferenceProvider:
    def predict(self, image: Path) -> Prediction: raise NotImplementedError

