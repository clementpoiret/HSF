from pathlib import Path, PosixPath

import onnxruntime as ort
from omegaconf.listconfig import ListConfig


def get_inference_sessions(models_path: PosixPath, providers: list) -> list:
    """
    Returns ONNX runtime sessions.

    Args:
        models_path (PosixPath): Path to the models.

    Returns:
        List[ort.InferenceSession]: ONNX runtime sessions.
    """

    def _correct_provider(provider):
        if isinstance(provider, str):
            return provider
        elif isinstance(provider, ListConfig):
            provider = list(provider)
            assert len(provider) == 2
            provider[1] = dict(provider[1])

            return tuple(provider)

    p = Path(models_path).expanduser()
    models = list(p.glob("*.onnx"))

    providers = [_correct_provider(provider) for provider in providers]

    return [
        ort.InferenceSession(str(model_path), providers=providers)
        for model_path in models
    ]
