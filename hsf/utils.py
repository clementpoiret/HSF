import logging
from pathlib import PosixPath
from typing import Generator, Optional

import ants
import torch
from omegaconf import DictConfig
from rich.logging import RichHandler
from roiloc.locator import RoiLocator

from hsf.segment import mri_to_subject, save_prediction, segment
from hsf.uncertainty import voxelwise_uncertainty

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET",
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

log = logging.getLogger(__name__)


def predict(mri: PosixPath, second_mri: Optional[PosixPath], engines: Generator,
            cfg: DictConfig) -> tuple:
    """
    Predict the hippocampal segmentation for a given MRI.

    Args:
        mri (PosixPath): Path to the MRI.
        second_mri (PosixPath): Path to the second MRI.
        engines (Generator): Generator of InferenceEngines.
        cfg (DictConfig): Configuration.

    Returns:
        tuple: Tuple containing soft and hard segmentations.
    """
    if second_mri:
        subjects = [mri_to_subject(mri), mri_to_subject(second_mri)]
    else:
        subjects = [mri_to_subject(mri)]

    log.info("Starting segmentation...")
    return segment(subjects=subjects,
                   augmentation_cfg=cfg.augmentation,
                   segmentation_cfg=cfg.segmentation.segmentation,
                   n_engines=len(cfg.segmentation.models),
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
    log.info(f"Saving voxel-wise uncertainty map in {str(mri.parent)}")
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
    log.info("Saving cropped segmentation in LPI orientation.")
    segmentation = save_prediction(mri=hippocampus,
                                   prediction=hard_pred,
                                   suffix="seg_crop")

    native_segmentation = locator.inverse_transform(segmentation)

    if orientation != "LPI":
        log.info("Reorienting segmentation to original orientation...")
        native_segmentation = ants.reorient_image2(native_segmentation,
                                                   orientation=orientation)

    extensions = "".join(hippocampus.suffixes)
    fname = hippocampus.name.replace(extensions, "") + "_seg.nii.gz"
    output_path = mri.parent / fname

    ants.image_write(native_segmentation, str(output_path))

    log.info(f"Saved segmentation in native space to {str(output_path)}")
