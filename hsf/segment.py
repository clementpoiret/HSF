from pathlib import PosixPath

import ants
import torch
import torchio as tio
from omegaconf.dictconfig import DictConfig
from rich.progress import track

from hsf.engines import InferenceEngine


def mri_to_subject(mri: PosixPath) -> tio.Subject:
    """
    Loads the MRI data from the given path and returns the preprocessed subject.

    Args:
        mri (PosixPath): Path to the MRI data.

    Returns:
        tio.Subject: The preprocessed MRI data.
    """
    subject = tio.Subject(mri=tio.ScalarImage(mri))

    preprocessing_pipeline = tio.Compose([
        # tio.ToCanonical(),
        tio.ZNormalization(),
        tio.EnsureShapeMultiple(8),
    ])

    return preprocessing_pipeline(subject)


def get_augmentation_pipeline(augmentation_cfg: DictConfig) -> tio.Compose:
    """
    Returns the augmentation pipeline.

    Args:
        augmentation_cfg (DictConfig): Augmentation configuration.

    Returns:
        tio.Compose: The augmentation pipeline.
    """
    flip = tio.RandomFlip(**augmentation_cfg.flip)
    resample = tio.OneOf({
        tio.RandomAffine(**augmentation_cfg.affine):
            augmentation_cfg.affine_probability,
        tio.RandomElasticDeformation(**augmentation_cfg.elastic):
            augmentation_cfg.elastic_probability
    })

    return tio.Compose((flip, resample))


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
    if ca_mode == "1/2/3":
        # identity
        return logits
    elif ca_mode == "1/23":
        # ca1; ca2+ca3
        _pre = logits[:, :3, :, :, :]
        _in = logits[:, 3:4, :, :, :] + logits[:, 4:5, :, :, :]
        _post = logits[:, 5:, :, :, :]

        return torch.cat([_pre, _in, _post], dim=1)
    elif ca_mode == "123":
        # ca1+ca2+ca3
        _pre = logits[:, :2, :, :, :]
        _in = logits[:,
                     2:3, :, :, :] + logits[:,
                                            3:4, :, :, :] + logits[:,
                                                                   4:5, :, :, :]
        _post = logits[:, 5:, :, :, :]

        return torch.cat([_pre, _in, _post], dim=1)
    else:
        raise ValueError(
            f"Unknown `ca_mode` ({ca_mode}). `ca_mode` must be 1/2/3, 1/23 or 123"
        )


def predict(subject: tio.Subject,
            engine: InferenceEngine,
            ca_mode: str = "1/2/3") -> torch.Tensor:
    """
    Predict a segmentation from a subject.

    Args:
        subject (tio.Subject): Loaded torchio subject.
        engine (InferenceEngine): HSF's Inference Engine.
        ca_mode (str, optional): The cornu ammoni division mode.
            Defaults to "1/2/3".

    Returns:
        torch.Tensor: Segmentation.
    """
    logits = engine(subject.mri.data[None].numpy())
    logits = to_ca_mode(torch.tensor(logits[0]), ca_mode)

    lm_temp = tio.LabelMap(tensor=torch.rand(1, 1, 1, 1),
                           affine=subject.mri.affine)
    subject.add_image(lm_temp, 'label')
    subject.label.set_data(logits[0])

    back = subject.apply_inverse_transform(warn=True)

    return back.label.data


def segment(subject: tio.Subject,
            augmentation_cfg: DictConfig,
            segmentation_cfg: DictConfig,
            engines: list,
            ca_mode: str = "1/2/3") -> tuple:
    """
    Segments the given subject.

    Args:
        subject (tio.Subject): The subject to segment.
        augmentation_cfg (DictConfig): Augmentation configuration.
        segmentation_cfg (DictConfig): Segmentation configuration.
        engines (List[InferenceEnging]): Inference Engines.
        ca_mode (str): The cornu ammoni division mode. Defaults to "1/2/3".

    Returns:
        torch.Tensor: The segmented subject.
    """
    if segmentation_cfg.test_time_augmentation:
        augmentation_pipeline = get_augmentation_pipeline(augmentation_cfg)
        n_aug = segmentation_cfg.test_time_num_aug
    else:
        n_aug = 1

    results = []
    for i in track(
            range(n_aug),
            description=f"Segmenting (TTA: {n_aug} | {len(engines)} MODELS)..."
    ):
        augmented = augmentation_pipeline(subject) if i > 0 else subject

        engines_predictions = [
            predict(augmented, engine, ca_mode) for engine in engines
        ]

        results.extend(engines_predictions)

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
