import logging
from pathlib import Path

import hydra
# from hydra import compose, initialize
from omegaconf import DictConfig
from rich.logging import RichHandler

from hsf.engines import check_config, get_inference_engines
from hsf.fetch_models import fetch_models
from hsf.multispectrality import (get_additional_hippocampi,
                                  get_second_contrast, register)
from hsf.roiloc_wrapper import get_lr_hippocampi, load_from_config
from hsf.utils import compute_uncertainty, predict, save
from hsf.welcome import welcome

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET",
                    format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler()])

log = logging.getLogger(__name__)

# initialize(config_path="hsf/conf")
# cfg = compose(config_name="config")


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    fetch_models(cfg.segmentation.models_path, cfg.segmentation.models)

    check_config(cfg)

    mris = load_from_config(cfg.files.path, cfg.files.pattern)

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

        for j, hippocampus in enumerate(zip(hippocampi, additional_hippocampi)):
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
