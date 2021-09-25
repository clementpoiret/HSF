from pathlib import Path, PosixPath

import ants
import hydra
# from hydra import compose, initialize
from icecream import ic
from omegaconf import DictConfig
from rich import print

from hsf.fetch_models import fetch_models
from hsf.roiloc_wrapper import (get_hippocampi, get_mri, load_from_config,
                                save_hippocampi)
from hsf.segment import (get_inference_sessions, mri_to_subject,
                         save_prediction, segment)
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
    return locator, original_orientation, save_hippocampi(
        right_mri=right_mri,
        left_mri=left_mri,
        dir_name=cfg.files.output_dir,
        original_mri_path=mri)


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    fetch_models(cfg.segmentation.models_path, cfg.segmentation.models)

    sessions = get_inference_sessions(cfg.segmentation.models_path)
    ic("Successfully loaded segmentation models in memory.")

    mris = load_from_config(cfg.files.path, cfg.files.pattern)

    print(
        "Please be aware that the segmentation is highly dependant on ROILoc to locate both hippocampi.\nROILoc will be run using the following configuration.\nIf the segmentation is of bad quality, please tune your ROILoc settings (e.g. ``margin``)."
    )
    ic(cfg.roiloc)
    print(
        "For additional details about ROILoc, please see https://github.com/clementpoiret/ROILoc"
    )

    N = len(mris)
    print(f"HSF found {N} MRIs to segment following to your configuration.")

    for i, mri in enumerate(mris):
        locator, orientation, hippocampi = get_lr_hippocampi(mri, cfg)

        for j, hippocampus in enumerate(hippocampi):
            print(f"Subject {i}/{N}, side {j}/1")
            hippocampus = Path(hippocampus)
            subject = mri_to_subject(hippocampus)

            ic("Starting segmentation...")
            prediction = segment(
                subject=subject,
                augmentation_cfg=cfg.augmentation,
                segmentation_cfg=cfg.segmentation.segmentation,
                sessions=sessions,
                ca_mode=str(cfg.segmentation.ca_mode),
            )

            ic("Saving cropped segmentation in LPI orientation.")
            segmentation = save_prediction(mri=hippocampus,
                                           prediction=prediction,
                                           suffix="seg_crop")

            native_segmentation = locator.inverse_transform(segmentation)

            if orientation != "LPI":
                ic("Reorienting segmentation to original orientation...")
                native_segmentation = ants.reorient_image2(
                    native_segmentation, orientation=orientation)

            extensions = "".join(hippocampus.suffixes)
            fname = hippocampus.name.replace(extensions, "") + "_seg.nii.gz"
            output_path = mri.parent / fname

            ants.image_write(native_segmentation, str(output_path))

            output = f"Saved segmentation in native space to {str(output_path)}"
            ic(output)


def start():
    welcome()
    main()
