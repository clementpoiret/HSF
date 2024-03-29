import logging
from pathlib import Path, PosixPath
from typing import Optional

import ants
from omegaconf.dictconfig import DictConfig
from rich.logging import RichHandler
from roiloc.locator import RoiLocator

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

log = logging.getLogger(__name__)


def load_from_config(path: str, pattern: str) -> list:
    """
    Loads all mris from a given path with a given pattern.

    Args:
        path (str): Path to the mris.
        pattern (str): Pattern to search for.

    Returns:
        list: List of mris.
    """
    p = Path(path).expanduser()
    return list(p.glob(pattern))


def get_mri(mri: PosixPath, mask_pattern: Optional[str] = None) -> tuple:
    """
    Loads an mri from a given path.

    Args:
        mri (PosixPath): Path to the mri.
        mask_pattern (str, optional): Pattern to search for.

    Returns:
        ants.ANTsImage: Loaded mri.
        ants.ANTsImage: Loaded mask or None.
    """
    if mask_pattern:
        mask = list(mri.parent.glob(mask_pattern))
        if mask:
            mask = ants.image_read(str(mask[0]), pixeltype="unsigned int")
        else:
            mask = None
            log.warning(
                "Couldn't find brain extraction mask for the provided pattern."
            )
    else:
        mask = None

    log.info(f"Loading mri from {mri}")
    return ants.image_read(str(mri)), mask


def get_hippocampi(mri: ants.ANTsImage,
                   roiloc_cfg: DictConfig,
                   mask: Optional[ants.ANTsImage] = None) -> tuple:
    """
    Locate right and left hippocampi from a given mri.

    Args:
        mri (ants.ANTsImage): Loaded mri.
        roiloc_cfg (DictConfig): Roiloc configuration.
            See `github.com/clementpoiret/ROILoc` for more information.
        mask (ants.ANTsImage, optional): Loaded mask.

    Returns:
        RoiLocator: fitted roilocator.
        right_mri (ants.ANTsImage): Right hippocampus.
        left_mri (ants.ANTsImage): Left hippocampus.
    """
    locator = RoiLocator(**roiloc_cfg, mask=mask)

    right_mri, left_mri = locator.fit_transform(mri)

    return locator, right_mri, left_mri


def save_hippocampi(right_mri: ants.ANTsImage, left_mri: ants.ANTsImage,
                    dir_name: str, original_mri_path: PosixPath) -> tuple:
    """
    Saves right and left hippocampus from a given mri.

    Args:
        right_mri (ants.ANTsImage): Right hippocampus.
        left_mri (ants.ANTsImage): Left hippocampus.
        dir_name (str): Name of the directory to save the hippocampus.
        original_mri_path (PosixPath): Path to the original mri.

    Returns:
        tuple: Path to the right & left hippocampi.
    """
    output_path = original_mri_path.parent / dir_name
    output_path.mkdir(parents=True, exist_ok=True)

    extensions = "".join(original_mri_path.suffixes)
    fname = original_mri_path.name.replace(extensions, "")

    output_pattern = str(output_path / (fname + "_{}_hippocampus.nii.gz"))

    right_output_path = output_pattern.format("right")
    left_output_path = output_pattern.format("left")
    ants.image_write(right_mri, right_output_path)
    ants.image_write(left_mri, left_output_path)

    return right_output_path, left_output_path
