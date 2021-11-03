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
        # Optimal for int8 quantized NN
        return "full"
    elif avx512:
        # AVX512 vector instruction set for fast NN inference
        return "partial"
    elif avx2:
        # AVX2 vector instruction set slower than AVX512
        return "minimal"
    else:
        # No AVX2/512 or VNNI -> Risk of slow inference time
        return "not supported"


def print_deepsparse_support():
    """
    Prints DeepSparse Support Status.
    """
    print(
        "DeepSparse Optimization Status (minimal: AVX2 | partial: AVX512 | full: AVX512 VNNI):",
        deepsparse_support())


def get_inference_engines(models_path: PosixPath, engine_name: str,
                          engine_settings: DictConfig) -> list:
    """
    Returns Inference Engines.

    Args:
        models_path (PosixPath): Path to the models.
        engine_name (str): Name of the engine. Can be "onnxruntime" or "deepsparse".
        engine_settings (DictConfig): Engine settings.

    Returns:
        List[InferenceEngine]: Inference Engines.
    """
    p = Path(models_path).expanduser()
    models = list(p.glob("*.onnx"))

    return [
        InferenceEngine(engine_name=engine_name,
                        engine_settings=engine_settings,
                        model=model) for model in models
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
            print_deepsparse_support()
            set_engine = self.set_deepsparse_engine
        elif engine_name == "onnxruntime":
            set_engine = self.set_ort_engine

        set_engine(model)

    def __call__(self, x):
        if self.engine_name == "onnxruntime":
            return self.engine.run(None, {"input": x})

        elif self.engine_name == "deepsparse":
            return self.engine.run([x])

    def set_deepsparse_engine(self, model: PosixPath):
        """
        Sets the DeepSparse engine.

        Args:
            model (PosixPath): Path to the model.
        """
        self.engine = deepsparse.compile_model(
            str(model),
            batch_size=self.engine_settings.batch_size,
            num_cores=self.engine_settings.num_cores,
            num_sockets=self.engine_settings.num_sockets)

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
