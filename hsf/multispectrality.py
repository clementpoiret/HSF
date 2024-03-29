import logging
from pathlib import PosixPath
from typing import Optional, Tuple

import ants
from omegaconf import DictConfig
from rich.logging import RichHandler
from roiloc._cache import handle_cache
from roiloc.locator import RoiLocator

from hsf.roiloc_wrapper import save_hippocampi

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

log = logging.getLogger(__name__)


def get_second_contrast(mri: PosixPath, pattern: str) -> Optional[PosixPath]:
    """
    Get the second contrast of a given MRI.

    Args:
        mri (PosixPath): Path to the MRI.
        pattern (str): Pattern to search for.

    Returns:
        Optional[PosixPath]: Path to the second contrast.
    """
    if pattern:
        second_contrast = list(mri.parent.glob(pattern))
        assert len(
            second_contrast
        ) == 1, f"Invalid file pattern: {pattern}. No or multiple files found."

        return second_contrast[0]
    return None


@handle_cache
def register(mri: PosixPath,
             second_contrast: PosixPath,
             cfg: DictConfig,
             outprefix: Optional[str] = None) -> PosixPath:
    """
    Register the second contrast to the first one.

    Args:
        mri (PosixPath): Path to the first MRI.
        second_contrast (PosixPath): Path to the second MRI.
        cfg (DictConfig): Configuration.
        outprefix (str, optional): Prefix for the output.

    Returns:
        PosixPath: Path to the registered MRI.
    """
    if cfg.multispectrality.same_space:
        return second_contrast
    registration_params = dict(cfg.multispectrality.registration)
    if not registration_params.get("outprefix"):
        registration_params["outprefix"] = outprefix

    fixed = ants.image_read(str(mri))
    moving = ants.image_read(str(second_contrast))

    log.info(f"Registering {str(second_contrast)} to {str(mri)}")
    transformation = ants.registration(fixed=fixed,
                                       moving=moving,
                                       **registration_params)

    registered = ants.apply_transforms(
        fixed=fixed,
        moving=moving,
        transformlist=transformation["fwdtransforms"])

    extensions = "".join(second_contrast.suffixes)
    fname = second_contrast.name.replace(extensions, "") + "_registered.nii.gz"
    output_dir = mri.parent / cfg.files.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    ants.image_write(registered, str(output_dir / fname))

    return output_dir / fname


def get_additional_hippocampi(mri: PosixPath, second_contrast: PosixPath,
                              locator: RoiLocator,
                              cfg: DictConfig) -> Tuple[PosixPath]:
    """
    Get the additional hippocampi from a given mri.

    Args:
        mri (PosixPath): Path to the MRI.
        second_contrast (PosixPath): Path to the second MRI.
        locator (RoiLocator): RoiLocator instance.
        cfg (DictConfig): Configuration.

    Returns:
        Tuple[PosixPath]: Paths to the additional hippocampi.
    """
    image = ants.image_read(str(second_contrast), reorient="LPI")

    right_mri, left_mri = locator.transform(image)

    extensions = "".join(second_contrast.suffixes)
    fname = mri.name.replace(extensions, "") + "_second-contrast.nii.gz"

    return save_hippocampi(right_mri=right_mri,
                           left_mri=left_mri,
                           dir_name=cfg.files.output_dir,
                           original_mri_path=mri.parent / fname)
