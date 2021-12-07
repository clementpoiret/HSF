from pathlib import Path, PosixPath

import ants
import hydra
import torch
# from hydra import compose, initialize
from omegaconf import DictConfig
from rich import print as pprint
from roiloc.locator import RoiLocator

from hsf.engines import get_inference_engines
from hsf.fetch_models import fetch_models
from hsf.roiloc_wrapper import (get_hippocampi, get_mri, load_from_config,
                                save_hippocampi)
from hsf.segment import mri_to_subject, save_prediction, segment
from hsf.uncertainty import voxelwise_uncertainty
from hsf.welcome import welcome

# initialize(config_path="hsf/conf")
# cfg = compose(config_name="config")
PREFIX = "[italic white]FACTORY >"


def get_lr_hippocampi(mri: PosixPath, cfg: DictConfig) -> tuple:
    """
    Get left and right hippocampi from a given MRI.

    Args:
        mri (PosixPath): Path to the MRI.
        cfg (DictConfig): Configuration.

    Returns:
        tuple: Tuple containing locator, orientation, left and right hippocampi.
    """
    image, bet_mask = get_mri(mri, cfg.files.mask_pattern)
    pprint(image)
    original_orientation = image.orientation

    if original_orientation != "LPI":
        pprint(
            f"{PREFIX} [bold orange3]WARNING: image is not in LPI orientation, we encourage you to save it in LPI."
        )
        image = ants.reorient_image2(image, orientation="LPI")

    pprint(f"{PREFIX} Started locating left and right hippocampi...")
    locator, right_mri, left_mri = get_hippocampi(mri=image,
                                                  roiloc_cfg=cfg.roiloc,
                                                  mask=bet_mask)

    pprint(f"{PREFIX} Saving left and right hippocampi (LPI orientation)...")
    return locator, original_orientation, save_hippocampi(
        right_mri=right_mri,
        left_mri=left_mri,
        dir_name=cfg.files.output_dir,
        original_mri_path=mri)


def predict(mri: PosixPath, engines: list, cfg: DictConfig) -> tuple:
    """
    Predict the hippocampal segmentation for a given MRI.

    Args:
        mri (PosixPath): Path to the MRI.
        engines (list): List of ONNX Runtime engines.
        cfg (DictConfig): Configuration.

    Returns:
        tuple: Tuple containing soft and hard segmentations.
    """
    subject = mri_to_subject(mri)

    pprint(f"{PREFIX} Starting segmentation...")
    return segment(subject=subject,
                   augmentation_cfg=cfg.augmentation,
                   segmentation_cfg=cfg.segmentation.segmentation,
                   engines=engines,
                   ca_mode=str(cfg.segmentation.ca_mode),
                   batch_size=cfg.hardware.engine_settings.batch_size)


def compute_uncertainty(mri: PosixPath, soft_pred: torch.Tensor) -> None:
    """
    Compute uncertainty for a given set of segmentations.

    Args:
        mri (PosixPath): Path to the MRI.
        soft_pred (torch.Tensor): Soft segmentations.
    """
    uncertainty = voxelwise_uncertainty(soft_pred)
    pprint(f"{PREFIX} Saving voxel-wise uncertainty map in {str(mri.parent)}")
    _ = save_prediction(mri=mri,
                        prediction=uncertainty,
                        suffix="unc_crop",
                        astype="float64")


def save(mri: PosixPath, hippocampus: PosixPath, hard_pred: torch.Tensor,
         locator: RoiLocator, orientation: str) -> None:
    """
    Save segmentations.

    Args:
        mri (PosixPath): Path to the MRI.
        hippocampus (PosixPath): Path to the hippocampus.
        hard_pred (torch.Tensor): Hard segmentations.
        locator (RoiLocator): RoiLocator.
        orientation (str): Orientation of the original MRI.
    """
    pprint(f"{PREFIX} Saving cropped segmentation in LPI orientation.")
    segmentation = save_prediction(mri=hippocampus,
                                   prediction=hard_pred,
                                   suffix="seg_crop")

    native_segmentation = locator.inverse_transform(segmentation)

    if orientation != "LPI":
        pprint(f"{PREFIX} Reorienting segmentation to original orientation...")
        native_segmentation = ants.reorient_image2(native_segmentation,
                                                   orientation=orientation)

    extensions = "".join(mri.suffixes)
    fname = hippocampus.name.replace(extensions, "") + "_seg.nii.gz"
    output_path = mri.parent / fname

    ants.image_write(native_segmentation, str(output_path))

    pprint(f"{PREFIX} Saved segmentation in native space to {str(output_path)}")


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    fetch_models(cfg.segmentation.models_path, cfg.segmentation.models)

    if cfg.hardware.engine == "deepsparse":
        assert cfg.segmentation.test_time_num_aug % cfg.hardware.engine_settings.batch_size == 0, "test_time_num_aug must be a multiple of batch_size for deepsparse"

    engines = get_inference_engines(
        cfg.segmentation.models_path,
        engine_name=cfg.hardware.engine,
        engine_settings=cfg.hardware.engine_settings)
    pprint(f"{PREFIX} Successfully loaded segmentation models in memory.")

    mris = load_from_config(cfg.files.path, cfg.files.pattern)

    pprint(
        "Please be aware that the segmentation is highly dependant on ROILoc to locate both hippocampi.\nROILoc will be run using the following configuration.\nIf the segmentation is of bad quality, please tune your ROILoc settings (e.g. ``margin``)."
    )
    pprint(cfg.roiloc)
    pprint(
        "For additional details about ROILoc, please see https://github.com/clementpoiret/ROILoc"
    )

    N = len(mris)
    pprint(
        f"{PREFIX} HSF found {N} MRIs to segment following to your configuration."
    )

    for i, mri in enumerate(mris):
        locator, orientation, hippocampi = get_lr_hippocampi(mri, cfg)

        for j, hippocampus in enumerate(hippocampi):
            hippocampus = Path(hippocampus)

            pprint(f"{PREFIX} Subject {i+1}/{N}, side {j+1}/2")
            soft_pred, hard_pred = predict(hippocampus, engines, cfg)

            if soft_pred.shape[0] > 1:
                compute_uncertainty(hippocampus, soft_pred)

            save(mri, hippocampus, hard_pred, locator, orientation)


def start():
    welcome()
    main()
