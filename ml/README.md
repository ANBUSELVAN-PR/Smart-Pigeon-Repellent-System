# Machine learning

Inference runs on the computer. The default provider is explicitly simulated and returns no detection, so startup never downloads weights. Add an `InferenceProvider` adapter for a compatible detector and configure `MODEL_PATH`. A generic pretrained model is not assumed to recognize pigeons; use a compatible custom-trained model and document its dataset and evaluation.
