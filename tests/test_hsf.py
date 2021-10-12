from pathlib import Path

import ants
import hsf.fetch_models
import hsf.roiloc_wrapper
import hsf.segment
import hsf.uncertainty
import pytest
import torch
from hsf import __version__
from omegaconf import DictConfig, ListConfig


def test_version():
    assert __version__ == '0.1.2'


# Models getters
@pytest.fixture(scope="session")
def models_path(tmpdir_factory):
    """Setup tmpdir."""
    url = "https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1"
    xxh3 = "d0de65baa81d9382"

    tmpdir_path = tmpdir_factory.mktemp("hsf")

    hsf.fetch_models.fetch(tmpdir_path, "model.onnx", url, xxh3)

    assert xxh3 == hsf.fetch_models.get_hash(tmpdir_path / "model.onnx")

    return Path(tmpdir_path)


@pytest.fixture(scope="session")
def config():
    """Setup DictConfig."""
    configuration = {
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
            "test_time_augmentation": False,
            "test_time_num_aug": 1
        }
    }

    return DictConfig(configuration)


@pytest.fixture(scope="session")
def inference_sessions(models_path):
    """Tests that models can be loaded"""
    providers = [["CPUExecutionProvider"], ListConfig(["CPUExecutionProvider"])]

    sessions = [
        hsf.segment.get_inference_sessions(models_path, providers=p)[0]
        for p in providers
    ]

    return sessions


# ROILoc
def test_roiloc(models_path):
    """Tests that we can locate and save hippocampi."""
    mris = hsf.roiloc_wrapper.load_from_config("tests/mri", "*.nii.gz")
    assert mris

    mri, mask = hsf.roiloc_wrapper.get_mri(mris[0])
    assert isinstance(mri, ants.ANTsImage)

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
def test_segment(models_path, config, inference_sessions):
    """Tests that we can segment and save a hippocampus."""
    mri = models_path / "tse_right_hippocampus.nii.gz"
    sub = hsf.segment.mri_to_subject(mri)

    for ca_mode in ["1/2/3", "1/23", "123"]:
        _, pred = hsf.segment.segment(sub, config.augmentation,
                                      config.segmentation, inference_sessions,
                                      ca_mode)

    hsf.segment.save_prediction(mri, pred)


def test_uncertainty():
    """Tests that uncertainty can be computed."""
    for n_classes in [1, 3]:
        sample_probs = torch.randn(1, n_classes, 16, 16, 16)
        sample_probs = torch.softmax(sample_probs, dim=1)

        unc = hsf.uncertainty.voxelwise_uncertainty(sample_probs)

        assert unc.shape == (16, 16, 16)
