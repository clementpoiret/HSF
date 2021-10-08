# The code contained in this file is licensed under the MIT license,
# and is borrowed from the ivadomed repository:
# https://raw.githubusercontent.com/ivadomed/ivadomed/ac29c7cbe299e6478854823ed6bd818c0e5f9642/ivadomed/uncertainty.py
# Copyright (c) 2019 Polytechnique Montreal, Université de Montréal
import ants
import torch


def voxelwise_uncertainty(samples_prob: torch.Tensor,
                          eps: float = 1e-5) -> torch.Tensor:
    """
    Computes the voxelwise uncertainty of a list of samples as entropy.

    Args:
        samples_prob (torch.Tensor): Softmaxed predictions.
        eps (float): Epsilon factor to avoid log(0).

    Returns:
        torch.Tensor: The voxelwise uncertainty map.
    """
    unc = samples_prob.permute(0, 2, 3, 4, 1)
    unc = -torch.sum(
        torch.mean(unc, 0) * torch.log(torch.mean(unc, 0) + eps), -1)
    unc[unc < 0] = 0

    return unc


def structural_uncertainty(samples: list) -> ants.ANTsImage:
    """
    Compute the structural uncertainty of a list of samples.

    Args:
        samples (list): List of predictions.

    Returns:
        ants.ANTsImage: Average voxel-wise uncertainty within the structure.
    """
    raise NotImplementedError("Structural Uncertainty not yet implemented.")
