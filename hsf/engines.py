from pathlib import Path, PosixPath

import deepsparse
import onnxruntime as ort
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig


def deepsparse_support() -> str:
    """
    Check if the CPU supports DeepSparse's optimizations.

    Returns:
        str: Support Status
    """
    avx2 = deepsparse.cpu.cpu_avx2_compatible()
    avx512 = deepsparse.cpu.cpu_avx512_compatible()
    vnni = deepsparse.cpu.cpu_vnni_compatible()

    if vnni:
        return "full"
    elif avx512:
        return "partial"
    elif avx2:
        return "minimal"
    else:
        return "not supported"


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


class InferenceEngine:
    """
    Base class for inference engines.
    """

    def __init__(self, engine: str, engine_settings: DictConfig,
                 models_path: PosixPath):
        self.engine = engine
        self.engine_settings = engine_settings

        if engine == "deepsparse":
            support = deepsparse_support()
            print(f"DeepSparse's optimizations support: {support}")

        p = Path(models_path).expanduser()
        self.models = list(p.glob("*.onnx"))

    def __call__(self):
        raise NotImplementedError

    def get_ort_engines(self):

        def _correct_provider(provider):
            if isinstance(provider, str):
                return provider
            elif isinstance(provider, ListConfig):
                provider = list(provider)
                assert len(provider) == 2
                provider[1] = dict(provider[1])

                return tuple(provider)

        providers = [
            _correct_provider(provider)
            for provider in self.engine_settings.execution_providers
        ]

        return [
            ort.InferenceSession(str(model_path), providers=providers)
            for model_path in self.models
        ]

    def get_deepsparse_engines(self):
        raise NotImplementedError
