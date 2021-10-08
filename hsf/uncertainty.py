# The code contained in this file is licensed under the MIT license,
# and is borrowed from the ivadomed repository:
# https://raw.githubusercontent.com/ivadomed/ivadomed/ac29c7cbe299e6478854823ed6bd818c0e5f9642/ivadomed/uncertainty.py
# Copyright (c) 2019 Polytechnique Montreal, Université de Montréal
import ants


def voxelwise_uncertainty(samples: list) -> ants.ANTsImage:
    """
    Compute the voxelwise uncertainty of a list of samples.

    Voxel-wise uncertainty is estimated as entropy over all probability maps.

    Args:
        samples (list): List of predictions.

    Returns:
        ants.ANTsImage: The voxelwise uncertainty map.
    """
    raise NotImplementedError("Voxelwise Uncertainty not yet implemented.")


def structural_uncertainty(samples: list) -> ants.ANTsImage:
    """
    Compute the structural uncertainty of a list of samples.

    Structure-wise uncertainty from N probability maps.

    Args:
        samples (list): List of predictions.

    Returns:
        ants.ANTsImage: Average voxel-wise uncertainty within the structure.
    """
    raise NotImplementedError("Structural Uncertainty not yet implemented.")
