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

    Args:
        engine_name (str): Name of the engine.
        engine_settings (DictConfig): Settings for the engine.
        model (PosixPath): Path to the model.
    """

    def __init__(self, engine_name: str, engine_settings: DictConfig,
                 model: PosixPath):
        self.engine_name = engine_name
        self.engine_settings = engine_settings
        self.model = model

        if engine_name == "deepsparse":
            support = deepsparse_support()
            print(f"DeepSparse's optimizations support: {support}")
            set_engine = self.set_deepsparse_engine
            raise NotImplementedError
        elif engine_name == "onnxruntime":
            set_engine = self.set_ort_engine

        set_engine(model)

    def __call__(self, x):
        if self.engine_name == "onnxruntime":
            return self.engine.run(None, {"input": x})

        elif self.engine_name == "deepsparse":
            raise NotImplementedError

    def set_deepsparse_engine(self, model: PosixPath):
        """
        Sets the DeepSparse engine.

        Args:
            model (PosixPath): Path to the model.
        """
        raise NotImplementedError

    def set_ort_engine(self, model):
        """
        Sets the ONNXRuntime engine.

        Args:
            model (PosixPath): Path to the model.
        """

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
        self.engine = ort.InferenceSession(str(model), providers=providers)
