import logging
from pathlib import PosixPath
from typing import Optional

import ants
from omegaconf import DictConfig
from rich.logging import RichHandler
from roiloc._cache import handle_cache
from roiloc.template import get_mni

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET",
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

log = logging.getLogger(__name__)


@handle_cache
def to_mni(mri: PosixPath,
           cfg: DictConfig,
           outprefix: Optional[str] = None) -> PosixPath:
    """
    Register a given MRI to MNI space.

    Args:
        mri (PosixPath): Path to the MRI.
        cfg (DictConfig): Configuration.
        outprefix (str, optional): Prefix for the output.

    Returns:
        PosixPath: Path to the registered MRI.
    """
    registration_params = dict(cfg.preprocessing.to_mni.params)
    if not registration_params.get("outprefix"):
        registration_params["outprefix"] = outprefix

    fixed = get_mni(cfg.roiloc.contrast, cfg.roiloc.bet)
    moving = ants.image_read(str(mri), reorient="LPI")

    log.info(f"Registering {str(mri)} to the MNI space")
    transformation = ants.registration(fixed=fixed,
                                       moving=moving,
                                       **registration_params)

    registered = ants.apply_transforms(
        fixed=fixed,
        moving=moving,
        transformlist=transformation["fwdtransforms"])

    extensions = "".join(mri.suffixes)
    fname = mri.name.replace(extensions, "") + "_MNI.nii.gz"
    output_dir = mri.parent

    ants.image_write(registered, str(output_dir / fname))

    return output_dir / fname


def resample(mri: PosixPath, cfg: DictConfig) -> PosixPath:
    """
    Resample a given MRI to a given resolution.

    Args:
        mri (PosixPath): Path to the MRI.
        cfg (DictConfig): Configuration.

    Returns:
        PosixPath: Path to the resampled MRI.
    """
    resampling_params = dict(cfg.preprocessing.resample.params)

    img = ants.image_read(str(mri), reorient="LPI")

    log.info(f"Resampling {str(mri)}")
    resampled = ants.resample_image(img, **resampling_params)

    extensions = "".join(mri.suffixes)
    fname = mri.name.replace(extensions, "") + "_resampled.nii.gz"
    output_dir = mri.parent

    ants.image_write(resampled, str(output_dir / fname))

    return output_dir / fname
