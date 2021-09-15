from pathlib import PosixPath
import ants
import hydra
# from hydra import compose, initialize
from icecream import ic
from omegaconf import DictConfig
from rich import print

from hsf.fetch_models import fetch_models
from hsf.mri_getter import (get_hippocampi, get_mri, load_from_config,
                            save_hippocampi)
from hsf.welcome import welcome

# initialize(config_path="hsf/conf")
# cfg = compose(config_name="config")


def get_lr_hippocampi(mri: PosixPath, cfg: DictConfig) -> tuple:
    image, bet_mask = get_mri(mri, cfg.files.mask_pattern)
    print(image)
    original_orientation = image.orientation

    if original_orientation != "LPI":
        print(
            "[bold orange3]WARNING: image is not in LPI orientation, we encourage you to save it in LPI."
        )
        image = ants.reorient_image2(image, orientation="LPI")

    ic("Started locating left and right hippocampi...")
    locator, right_mri, left_mri = get_hippocampi(mri=image,
                                                  roiloc_cfg=cfg.roiloc,
                                                  mask=bet_mask)

    ic("Saving left and right hippocampi (LPI orientation)...")
    return original_orientation, save_hippocampi(right_mri=right_mri,
                                                 left_mri=left_mri,
                                                 dir_name=cfg.files.output_dir,
                                                 original_mri_path=mri)


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    fetch_models(cfg.segmentation.models_path, cfg.segmentation.models)

    mris = load_from_config(cfg.files.path, cfg.files.pattern)

    for mri in mris:
        orientation, (right_mri, left_mri) = get_lr_hippocampi(mri, cfg)


def start():
    welcome()
    main()
