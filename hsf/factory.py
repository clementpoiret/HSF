import logging
from pathlib import Path, PosixPath
from typing import Generator, List, Optional

import ants
import hydra
import torch
from omegaconf import DictConfig
from rich.logging import RichHandler
from roiloc.locator import RoiLocator

from hsf.engines import get_inference_engines
from hsf.fetch_models import fetch_models
from hsf.multispectrality import (get_additional_hippocampi,
                                  get_second_contrast, register)
from hsf.roiloc_wrapper import (get_hippocampi, get_mri, load_from_config,
                                save_hippocampi)
from hsf.segment import mri_to_subject, save_prediction, segment
from hsf.uncertainty import voxelwise_uncertainty
from hsf.welcome import welcome

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

log = logging.getLogger(__name__)


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
    log.info(image)
    original_orientation = image.orientation

    if original_orientation != "LPI":
        log.warning(
            "The image is not in LPI orientation, we encourage you to save it in LPI."
        )
        image = ants.reorient_image2(image, orientation="LPI")

    log.info("Started locating left and right hippocampi...")
    locator, right_mri, left_mri = get_hippocampi(mri=image,
                                                  roiloc_cfg=cfg.roiloc,
                                                  mask=bet_mask)

    log.info("Saving left and right hippocampi (LPI orientation)...")
    return locator, original_orientation, save_hippocampi(
        right_mri=right_mri,
        left_mri=left_mri,
        dir_name=cfg.files.output_dir,
        original_mri_path=mri)


def predict(mri: PosixPath, second_mri: Optional[PosixPath],
            engines: Generator, cfg: DictConfig) -> tuple:
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


def filter_mris(mris: List[PosixPath], overwrite: bool) -> List[PosixPath]:
    """
    Filter mris.

    Args:
        mris (List[PosixPath]): List of MRI paths.
        overwrite (bool): Overwrite existing segmentations.

    Returns:
        List[PosixPath]: List of filtered MRI paths.
    """

    def _get_segmentations(mri: PosixPath) -> List[PosixPath]:
        extensions = "".join(mri.suffixes)
        stem = mri.name.replace(extensions, "")
        segmentations = list(
            mri.parent.glob(f"{stem}*_hippocampus_seg.nii.gz"))

        if len(segmentations) > 2:
            log.warning(
                f"Found {len(segmentations)} segmentations for {mri}. "
                "As HSF produces only two files per MRI, this might indicate a misconfiguration."
            )

        if len(segmentations) > 0:
            log.info(
                f"Found {len(segmentations)} segmentations for {mri}. "
                "Skipping segmentation. If you want to overwrite, set overwrite=True."
            )

        return segmentations

    mris = [mri for mri in mris if not mri.name.endswith("_seg.nii.gz")]
    if overwrite:
        return mris

    mris = [mri for mri in mris if len(_get_segmentations(mri)) == 0]
    return mris


@hydra.main(config_path="conf", config_name="config", version_base="1.1")
def main(cfg: DictConfig) -> None:
    fetch_models(cfg.segmentation.models_path, cfg.segmentation.models)

    if cfg.hardware.engine == "deepsparse":
        tta = cfg.segmentation.segmentation.test_time_num_aug
        bs = cfg.hardware.engine_settings.batch_size
        multispectral = 2 if cfg.multispectrality.pattern else 1

        if multispectral * (tta + 1) % bs != 0:
            raise AssertionError(
                "test_time_num_aug+1 must be a multiple of batch_size for deepsparse"
            )

    mris = load_from_config(cfg.files.path, cfg.files.pattern)
    _n = len(mris)

    mris = filter_mris(mris, cfg.files.overwrite)

    if len(mris) == 0 and _n > 0:
        log.info("No new MRI found. Skipping segmentation.")
        return

    log.warning(
        "Please be aware that the segmentation is highly dependant on ROILoc to locate both hippocampi.\nROILoc will be run using the following configuration.\nIf the segmentation is of bad quality, please tune your ROILoc settings (e.g. ``margin``)."
    )
    log.info(cfg.roiloc)
    log.info(
        "For additional details about ROILoc, please see https://github.com/clementpoiret/ROILoc"
    )

    N = len(mris)
    log.info(f"HSF found {N} MRIs to segment following to your configuration.")

    pattern = cfg.multispectrality.pattern
    if pattern:
        log.warning("Multispectrality is currently in beta stage.")

    for i, mri in enumerate(mris):
        second_contrast = get_second_contrast(mri, pattern)

        locator, orientation, hippocampi = get_lr_hippocampi(mri, cfg)

        if second_contrast:
            second_contrast = register(mri, second_contrast, cfg)
            additional_hippocampi = get_additional_hippocampi(
                mri, second_contrast, locator, cfg)
        else:
            additional_hippocampi = [None, None]

        for j, hippocampus in enumerate(zip(hippocampi,
                                            additional_hippocampi)):
            engines = get_inference_engines(
                cfg.segmentation.models_path,
                engine_name=cfg.hardware.engine,
                engine_settings=cfg.hardware.engine_settings)

            first_hippocampus = Path(hippocampus[0])
            second_hippocampus = Path(
                hippocampus[1]) if second_contrast else None

            log.info(f"Subject {i+1}/{N}, side {j+1}/2")
            soft_pred, hard_pred = predict(first_hippocampus,
                                           second_hippocampus, engines, cfg)

            if soft_pred.shape[0] > 1:
                compute_uncertainty(first_hippocampus, soft_pred)

            save(mri, first_hippocampus, hard_pred, locator, orientation)


def start():
    welcome()
    main()
