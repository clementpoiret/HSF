import itertools
from pathlib import PosixPath
from typing import Generator, List

import ants
import numpy as np
import torch
import torchio as tio
from omegaconf.dictconfig import DictConfig
from rich.progress import track

from hsf.augmentation import get_augmented_subject
from hsf.engines import InferenceEngine


def mri_to_subject(mri: PosixPath) -> tio.Subject:
    """
    Loads the MRI data from the given path and returns the preprocessed subject.

    Args:
        mri (PosixPath): Path to the MRI data.
        second_mri (Optional[PosixPath]): Path to the second MRI data.

    Returns:
        tio.Subject: The preprocessed MRI data.
    """
    subject = tio.Subject(mri=tio.ScalarImage(mri))

    preprocessing_pipeline = tio.Compose([
        tio.ZNormalization(),
        tio.EnsureShapeMultiple(8),
    ])

    return preprocessing_pipeline(subject)


def to_ca_mode(logits: torch.Tensor, ca_mode: str = "1/2/3") -> torch.Tensor:
    """
    Converts the logits to the ca_mode.

    Args:
        logits (torch.Tensor): The logits.
        ca_mode (str): The cornu ammoni division mode.

    Returns:
        torch.Tensor: The corrected logits.
    """
    # 0: bg, 1: dg, 2: ca1, 3: ca2, 4: ca3, 5: sub
    if not ca_mode:
        # Whole hippocampus
        _pre = logits[:, :1, :, :, :]
        _in = torch.sum(logits[:, 1:, :, :, :], dim=1, keepdim=True)

        return torch.cat([_pre, _in], dim=1)
    if ca_mode == "1/2/3":
        # identity
        return logits
    if ca_mode == "1/23":
        # ca1; ca2+ca3
        _pre = logits[:, :3, :, :, :]
        _in = logits[:, 3:4, :, :, :] + logits[:, 4:5, :, :, :]
        _post = logits[:, 5:, :, :, :]

        return torch.cat([_pre, _in, _post], dim=1)
    if ca_mode == "123":
        # ca1+ca2+ca3
        _pre = logits[:, :2, :, :, :]
        _in = logits[:,
                     2:3, :, :, :] + logits[:,
                                            3:4, :, :, :] + logits[:, 4:
                                                                   5, :, :, :]
        _post = logits[:, 5:, :, :, :]

        return torch.cat([_pre, _in, _post], dim=1)
    raise ValueError(
        f"Unknown `ca_mode` ({ca_mode}). `ca_mode` must be 1/2/3, 1/23 or 123")


def predict(mris: list,
            engine: InferenceEngine,
            ca_mode: str = "1/2/3") -> torch.Tensor:
    """
    Predict a segmentation from a subject.

    Args:
        mris (List[tio.Subject]): List of loaded torchio mris.
        engine (InferenceEngine): HSF's Inference Engine.
        ca_mode (str, optional): The cornu ammoni division mode.
            Defaults to "1/2/3".

    Returns:
        torch.Tensor: Segmentations.
    """
    inp = np.stack([mri.mri.data.numpy() for mri in mris])

    logits = engine(inp)
    logits = to_ca_mode(torch.tensor(logits[0]), ca_mode)

    results = []
    for lab, aug in zip(logits, mris):
        lm_temp = tio.LabelMap(tensor=torch.rand(1, 1, 1, 1),
                               affine=aug.mri.affine)
        aug.add_image(lm_temp, 'label')
        aug.label.set_data(lab)
        back = aug.apply_inverse_transform(warn=False)
        results.append(back.label.data)

    return results


def segment(subjects: List[tio.Subject],
            augmentation_cfg: DictConfig,
            segmentation_cfg: DictConfig,
            n_engines: int,
            engines: Generator,
            ca_mode: str = "1/2/3",
            batch_size: int = 1) -> tuple:
    """
    Segments the given subject.

    Args:
        subjects (List): List of the subject to segment.
        augmentation_cfg (DictConfig): Augmentation configuration.
        segmentation_cfg (DictConfig): Segmentation configuration.
        engines (Generator[InferenceEngine]): Inference Engines.
        ca_mode (str): The cornu ammoni division mode. Defaults to "1/2/3".
        batch_size (int): Batch size. Defaults to 1.

    Returns:
        torch.Tensor: The segmented subject.
    """
    subjects = list(
        itertools.chain(*[
            get_augmented_subject(subject, augmentation_cfg, segmentation_cfg)
            for subject in subjects
        ]))

    batched_subjects = [
        subjects[x:x + batch_size] for x in range(0, len(subjects), batch_size)
    ]

    results = []
    n = 0
    for engine in engines:
        n += 1
        for sub in track(
                batched_subjects,
                description=
                f"Segmenting (TTA: {len(subjects)} | MODEL {n}/{n_engines})..."
        ):
            results.extend(predict(sub, engine, ca_mode))
    soft_predictions = torch.stack(results, dim=0)
    hard_prediction = soft_predictions.argmax(dim=1).long().mode(dim=0).values

    return soft_predictions, hard_prediction


def save_prediction(mri: PosixPath,
                    prediction: torch.Tensor,
                    suffix: str = "seg",
                    astype: str = "uint8") -> ants.ANTsImage:
    """
    Saves the prediction to the given path.

    Args:
        mri (PosixPath): Path to the MRI data.
        prediction (torch.Tensor): The prediction.
        suffix (str): The suffix of the output file.
        astype (str): The type of the output file.

    Returns:
        ants.ANTsImage: The predicted segmentation.
    """
    raw_img = ants.image_read(str(mri))
    array = prediction.numpy() * 1.
    raw_segmentation = raw_img.new_image_like(array.squeeze())

    extensions = "".join(mri.suffixes)
    fname = mri.name.replace(extensions, "") + "_" + suffix + ".nii.gz"

    output_path = mri.parent / fname

    segmentation = raw_segmentation.astype(astype)
    ants.image_write(segmentation, str(output_path))

    return segmentation
