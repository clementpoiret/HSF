import shutil
from pathlib import Path

import ants
import pytest
import torch
from omegaconf import DictConfig

import hsf.engines
import hsf.factory
import hsf.fetch_models
import hsf.multispectrality
import hsf.roiloc_wrapper
import hsf.segment
import hsf.uncertainty
from hsf import __version__


def test_version():
    assert __version__ == "1.2.2"


# SETUP FIXTURES
@pytest.fixture(scope="session")
def models_path(tmpdir_factory):
    """Setup tmpdir."""
    url = "https://zenodo.org/record/6457484/files/arunet_3.0.0_single.onnx?download=1"
    xxh3 = "71edec9011f7f304"

    tmpdir_path = tmpdir_factory.mktemp("hsf")
    tmpdir_path = Path(tmpdir_path)

    # Copy sample mri
    shutil.copy("tests/mri/sub0_tse.nii.gz", tmpdir_path / "sub0_tse.nii.gz")
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
            "pattern": "sub*_tse.nii.gz",
            "mask_pattern": None,
            "output_dir": "hsf_outputs",
            "overwrite": False,
        },
        "hardware": {
            "engine": "onnxruntime",
            "engine_settings": {
                "execution_providers": [
                    [
                        "CUDAExecutionProvider",
                        {"device_id": 0, "gpu_mem_limit": 2147483648},
                    ],
                    "CPUExecutionProvider",
                ],
                "batch_size": 1,
            },
        },
        "roiloc": {"roi": "hippocampus", "contrast": "t2", "margin": [2, 0, 2]},
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
                "locked_borders": 0,
            },
        },
        "multispectrality": {
            "pattern": None,
            "same_space": True,
            "registration": {"type_of_transform": "AffineFast"},
        },
        "segmentation": {
            "ca_mode": "1/2/3",
            "models_path": str(models_path),
            "models": {
                "model.onnx": {
                    "url": "https://zenodo.org/record/6457484/files/arunet_3.0.0_single.onnx?download=1",
                    "xxh3_64": "71edec9011f7f304",
                }
            },
            "segmentation": {"test_time_augmentation": True, "test_time_num_aug": 5},
        },
    }

    return DictConfig(configuration)


@pytest.fixture(scope="session")
def deepsparse_inference_engines(models_path):
    """Tests that models can be loaded using DeepSparse"""
    settings = DictConfig({"num_cores": 0, "batch_size": 2})

    engines = hsf.engines.get_inference_engines(
        models_path, engine_name="deepsparse", engine_settings=settings
    )

    return list(engines)


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

    hsf.factory.compute_uncertainty(models_path / "sub0_tse.nii.gz", soft_pred)


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
    mris = hsf.roiloc_wrapper.load_from_config(models_path, "sub0_tse.nii.gz")
    assert mris

    mri, mask = hsf.roiloc_wrapper.get_mri(mris[0], mask_pattern="mask.nii.gz")
    assert isinstance(mask, ants.ANTsImage)
    mri, mask = hsf.roiloc_wrapper.get_mri(mris[0], mask_pattern="no_mask.nii.gz")
    assert isinstance(mri, ants.ANTsImage)
    assert mask is None

    _, right, left = hsf.roiloc_wrapper.get_hippocampi(
        mri, {"contrast": "t2", "margin": [2, 0, 2], "roi": "hippocampus"}, mask
    )

    assert isinstance(right, ants.ANTsImage)
    assert isinstance(left, ants.ANTsImage)

    # Saving to {tmpdir}/tse_{side}_hippocampus.nii.gz
    hsf.roiloc_wrapper.save_hippocampi(right, left, models_path, mris[0])


# Segmentation
def test_segment(models_path, config, deepsparse_inference_engines):
    """Tests that we can segment and save a hippocampus."""
    mri = models_path / "sub0_tse_right_hippocampus.nii.gz"
    sub = hsf.segment.mri_to_subject(mri)
    sub = [sub, sub]

    for ca_mode in ["1/23", "123", ""]:
        _, pred = hsf.segment.segment(
            subjects=sub,
            augmentation_cfg=config.augmentation,
            segmentation_cfg=config.segmentation.segmentation,
            n_engines=1,
            engines=deepsparse_inference_engines,
            ca_mode=ca_mode,
            batch_size=2,
        )

    hsf.segment.save_prediction(mri, pred)


def test_multispectrality(models_path):
    """Tests that we can co-locate hippocampi in another contrast."""
    config = DictConfig(
        {
            "files": {"output_dir": str(models_path)},
            "multispectrality": {
                "pattern": "sub0_tse.nii.gz",
                "same_space": False,
                "registration": {"type_of_transform": "AffineFast"},
            },
        }
    )

    mri = hsf.roiloc_wrapper.load_from_config(models_path, "sub0_tse.nii.gz")[0]
    second_contrast = hsf.multispectrality.get_second_contrast(mri, "sub0_tse.nii.gz")

    registered = hsf.multispectrality.register(
        mri, second_contrast, DictConfig({"multispectrality": {"same_space": True}})
    )
    registered = hsf.multispectrality.register(mri, second_contrast, config)

    img = ants.image_read(str(mri), reorient="LPI")
    locator, _, _ = hsf.roiloc_wrapper.get_hippocampi(
        img, {"contrast": "t2", "margin": [2, 0, 2], "roi": "hippocampus"}, None
    )

    _, _ = hsf.multispectrality.get_additional_hippocampi(
        mri, registered, locator, config
    )


def test_uncertainty():
    """Tests that uncertainty can be computed."""
    n_classes = 1
    sample_probs = torch.randn(1, n_classes, 16, 16, 16)

    unc = hsf.uncertainty.voxelwise_uncertainty(sample_probs)

    assert unc.shape == (16, 16, 16)
