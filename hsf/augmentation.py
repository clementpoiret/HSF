import torchio as tio
from omegaconf.dictconfig import DictConfig


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


def get_augmented_subject(subject: tio.Subject, augmentation_cfg: DictConfig,
                          segmentation_cfg: DictConfig) -> tuple:
    """
    Returns the augmented subject.

    Args:
        subject (tio.Subject): The subject to augment.
        augmentation_cfg (DictConfig): Augmentation configuration.
        segmentation_cfg (DictConfig): Segmentation configuration.

    Returns:
        subjects (List[tio.Subject]): Augmented tio subject.
    """
    if segmentation_cfg.test_time_augmentation:
        augmentation_pipeline = get_augmentation_pipeline(augmentation_cfg)
        n_aug = segmentation_cfg.test_time_num_aug
    else:
        n_aug = 1

    subjects = []

    for i in range(n_aug):
        if i == 0:
            augmented = subject
        else:
            augmented = augmentation_pipeline(subject)

        subjects.append(augmented)

    return subjects
