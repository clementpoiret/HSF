from pathlib import Path, PosixPath

import ants
import onnxruntime as ort
import torch
import torchio as tio
from omegaconf.dictconfig import DictConfig


def mri_to_subject(mri: PosixPath) -> tio.Subject:
    """ Loads the MRI data from the given path and returns
    the preprocessed torchio subject.

    Args:
        mri (PosixPath): Path to the MRI data.

    Returns:
        tio.Subject: The preprocessed MRI data.
    """
    subject = tio.Subject(mri=tio.ScalarImage(mri))

    preprocessing_pipeline = tio.Compose([
        tio.ToCanonical(),
        tio.ZNormalization(),
        tio.EnsureShapeMultiple(8),
    ])

    return preprocessing_pipeline(subject)


def get_augmentation_pipeline(augmentation_cfg: DictConfig) -> tio.Compose:
    """ Returns the augmentation pipeline.

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


def get_inference_sessions(models_path: PosixPath) -> list:
    """ Returns ONNX runtime sessions.

    Args:
        models_path (PosixPath): Path to the models.

    Returns:
        List[ort.InferenceSession]: ONNX runtime sessions.
    """
    p = Path(models_path).expanduser()
    models = list(p.glob("*.onnx"))

    return [ort.InferenceSession(str(model_path)) for model_path in models]


def segment(subject: tio.Subject, augmentation_cfg: DictConfig,
            segmentation_cfg: DictConfig, sessions: list) -> torch.Tensor:
    """ Segments the given subject.

    Args:
        subject (tio.Subject): The subject to segment.
        augmentation_cfg (DictConfig): Augmentation configuration.
        segmentation_cfg (DictConfig): Segmentation configuration.
        sessions (List[ort.InferenceSession]): ONNX runtime sessions.

    Returns:
        torch.Tensor: The segmented subject.
    """
    if segmentation_cfg.test_time_augmentation:
        augmentation_pipeline = get_augmentation_pipeline(augmentation_cfg)
        n_aug = segmentation_cfg.test_time_num_aug
    else:
        n_aug = 1

    # to try: 20 augmentation for 5 models, or 20 augmentations PER model
    results = []
    for i in range(n_aug):
        if i == 0:
            augmented = subject
        else:
            augmented = augmentation_pipeline(subject)

        input_tensor = augmented.mri.data[None]

        sessions_predictions = []
        for session in sessions:
            logits = session.run(None, {"input": input_tensor.numpy()})
            output_tensor = torch.tensor(logits[0]).argmax(dim=1, keepdim=True)
            lm_temp = tio.LabelMap(tensor=torch.rand(1, 1, 1, 1),
                                   affine=augmented.mri.affine)
            augmented.add_image(lm_temp, 'label')
            augmented.label.set_data(output_tensor[0])
            back = augmented.apply_inverse_transform(warn=True)
            sessions_predictions.append(back.label.data)

        aug_sessions_predictions = torch.stack(sessions_predictions).long()
        sessions_result_tensor = aug_sessions_predictions.mode(dim=0).values
        results.append(sessions_result_tensor)

    if segmentation_cfg.test_time_augmentation:
        result_tensor = torch.stack(results).long().mode(dim=0).values
    else:
        result_tensor = results[0]

    return result_tensor


def save_prediction(mri: PosixPath,
                    prediction: torch.Tensor,
                    suffix: str = "seg") -> ants.ANTsImage:
    """ Saves the prediction to the given path.

    Args:
        mri (PosixPath): Path to the MRI data.
        prediction (torch.Tensor): The prediction.
        suffix (str): The suffix of the output file.
    
    Returns:
        ants.ANTsImage: The predicted segmentation.
    """
    raw_img = ants.image_read(str(mri))
    array = prediction.numpy() * 1.
    raw_segmentation = raw_img.new_image_like(array.squeeze())

    extensions = "".join(mri.suffixes)
    fname = mri.name.replace(extensions, "") + "_" + suffix + ".nii.gz"

    output_path = mri.parent / fname

    segmentation = raw_segmentation.astype("uint8")
    ants.image_write(segmentation, str(output_path))

    return segmentation
