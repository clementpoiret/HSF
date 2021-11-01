import shutil
from pathlib import Path

import ants
import hsf.engines
import hsf.factory
import hsf.fetch_models
import hsf.roiloc_wrapper
import hsf.segment
import hsf.uncertainty
import pytest
import torch
from hsf import __version__
from omegaconf import DictConfig


def test_version():
    assert __version__ == '0.1.2'


# SETUP FIXTURES
@pytest.fixture(scope="session")
def models_path(tmpdir_factory):
    """Setup tmpdir."""
    url = "https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1"
    xxh3 = "d0de65baa81d9382"

    tmpdir_path = tmpdir_factory.mktemp("hsf")
    tmpdir_path = Path(tmpdir_path)

    # Copy sample mri
    shutil.copy("tests/mri/tse.nii.gz", tmpdir_path / "tse.nii.gz")
    shutil.copy("tests/mri/mask.nii.gz", tmpdir_path / "mask.nii.gz")

    # Download model
    hsf.fetch_models.fetch(tmpdir_path, "model.onnx", url, xxh3)

    assert xxh3 == hsf.fetch_models.get_hash(tmpdir_path / "model.onnx")

    return tmpdir_path


@pytest.fixture(scope="session")
def config(models_path):
    """Setup DictConfig."""
    configuration = {
        "files": {
            "path": str(models_path),
            "pattern": "tse.nii.gz",
            "mask_pattern": None,
            "output_dir": "hsf_outputs",
        },
        "hardware": {
            "engine": "onnxruntime",
            "engine_settings": {
                "execution_providers": [[
                    "CUDAExecutionProvider", {
                        "device_id": 0,
                        "gpu_mem_limit": 2147483648
                    }
                ], "CPUExecutionProvider"],
                "batch_size": 1
            }
        },
        "roiloc": {
            "roi": "hippocampus",
            "contrast": "t2",
            "margin": [2, 0, 2]
        },
        "augmentation": {
            "flip": {
                "axes": ["LR"],
                "flip_probability": 0.5,
            },
            "affine_probability": 0.8,
            "affine": {
                "scales": 0.2,
                "degrees": 15,
                "translation": 3,
                "isotropic": False,
            },
            "elastic_probability": 0.20,
            "elastic": {
                "num_control_points": 4,
                "max_displacement": 4,
                "locked_borders": 0
            },
        },
        "segmentation": {
            "ca_mode": "1/2/3",
            "models_path": str(models_path),
            "models": {
                "model.onnx": {
                    "url":
                        "https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1",
                    "xxh3_64":
                        "d0de65baa81d9382"
                }
            },
            "segmentation": {
                "test_time_augmentation": False,
                "test_time_num_aug": 1
            }
        },
    }

    return DictConfig(configuration)


@pytest.fixture(scope="session")
def deepsparse_inference_engines(models_path):
    """Tests that models can be loaded using ORT"""
    settings = DictConfig({"num_cores": 0, "num_sockets": 0, "batch_size": 1})

    engines = hsf.engines.get_inference_engines(models_path,
                                                engine_name="onnxruntime",
                                                engine_settings=settings)

    return engines


# TESTS
# Main script called by the `hsf` command
def test_main(config):
    """Tests that the main script can be called."""
    hsf.engines.print_deepsparse_support()
    hsf.factory.main(config)


def test_main_compute_uncertainty(models_path):
    """Tests that the main script can compute uncertainty."""
    soft_pred = torch.randn(5, 6, 448, 30, 448)
    soft_pred = torch.softmax(soft_pred, dim=1)

    hsf.factory.compute_uncertainty(models_path / "tse.nii.gz", soft_pred)


# fetch_models
def test_fetch_models(models_path, config):
    """Tests that models can be (down)loaded"""
    # Delete the model if it exists
    filepath = models_path / "model.onnx"
    filepath.unlink()

    with filepath.open("w", encoding="utf-8") as f:
        f.write("Dummy model with wrong hash")

    # Redownload when wrong hash
    hsf.fetch_models.fetch_models(models_path, config.segmentation.models)


# # ROILoc
def test_roiloc(models_path):
    """Tests that we can locate and save hippocampi."""
    mris = hsf.roiloc_wrapper.load_from_config(models_path, "tse.nii.gz")
    assert mris

    mri, mask = hsf.roiloc_wrapper.get_mri(mris[0], mask_pattern="mask.nii.gz")
    assert isinstance(mask, ants.ANTsImage)
    mri, mask = hsf.roiloc_wrapper.get_mri(mris[0],
                                           mask_pattern="no_mask.nii.gz")
    assert isinstance(mri, ants.ANTsImage)
    assert mask == None

    _, right, left = hsf.roiloc_wrapper.get_hippocampi(mri, {
        "contrast": "t2",
        "margin": [2, 0, 2],
        "roi": "hippocampus"
    }, mask)

    assert isinstance(right, ants.ANTsImage)
    assert isinstance(left, ants.ANTsImage)

    # Saving to {tmpdir}/tse_{side}_hippocampus.nii.gz
    hsf.roiloc_wrapper.save_hippocampi(right, left, models_path, mris[0])


# Segmentation
def test_segment(models_path, config, deepsparse_inference_engines):
    """Tests that we can segment and save a hippocampus."""
    mri = models_path / "tse_right_hippocampus.nii.gz"
    sub = hsf.segment.mri_to_subject(mri)
    aug = hsf.segment.get_augmentation_pipeline(config.augmentation)
    sub = aug(sub)

    for ca_mode in ["1/23", "123"]:
        _, pred = hsf.segment.segment(sub, config.augmentation,
                                      config.segmentation.segmentation,
                                      deepsparse_inference_engines, ca_mode)

    hsf.segment.save_prediction(mri, pred)


def test_uncertainty():
    """Tests that uncertainty can be computed."""
    n_classes = 1
    sample_probs = torch.randn(1, n_classes, 16, 16, 16)

    unc = hsf.uncertainty.voxelwise_uncertainty(sample_probs)

    assert unc.shape == (16, 16, 16)
