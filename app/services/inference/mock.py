from pathlib import Path
from .base import InferenceProvider, Prediction
class MockInference(InferenceProvider):
    def predict(self, image: Path) -> Prediction:
        return Prediction(False, None, None, "mock-simulated")

