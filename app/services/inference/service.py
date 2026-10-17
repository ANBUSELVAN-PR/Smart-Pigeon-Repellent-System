from pathlib import Path
from app.core.config import settings
from .mock import MockInference
from .base import InferenceProvider, Prediction
class ModelInference(InferenceProvider):
    """Optional Ultralytics adapter. It requires a model with a pigeon label."""
    def __init__(self, path, threshold):
        from ultralytics import YOLO
        self.model=YOLO(str(path)); self.threshold=threshold
        names=self.model.names.values() if isinstance(self.model.names,dict) else self.model.names
        self.pigeon_labels={str(x).lower() for x in names if str(x).lower() in {"pigeon","rock dove","columba livia"}}
        if not self.pigeon_labels: raise ValueError("Configured model has no pigeon-compatible class label")
    def predict(self, image: Path):
        result=self.model(str(image), verbose=False)[0]; best=None
        for box in result.boxes:
            conf=float(box.conf[0]); label=str(result.names[int(box.cls[0])]).lower()
            if label in self.pigeon_labels and conf >= self.threshold and (best is None or conf>best): best=conf
        return Prediction(best is not None,"pigeon" if best is not None else None,best,"model")
def provider():
    if settings.inference_provider.lower() == "model":
        return ModelInference(settings.model_path, settings.confidence_threshold)
    return MockInference()
def infer(path: Path): return provider().predict(path)
