# Uncertainty Estimations

When HSF is used in `bagging` mode or with test-time augmentation (see the [configuration page](configuration.md)),
it is possible to estimate the uncertainty of the predicted segmentation, notably through the *Aleatoric Uncertainty*
which depends on noise or randomness in the input testing image.

## Aleatoric Uncertainty

Aleatoric uncertainty is also known as statistical uncertainty, and is representative of unknowns that differ each time we run the same experiment[^1].

> The uncertainty is estimated by measuring how diverse the predictions for a given image are.
> Wang et al., 2019.

Given a set $Y$ of $i$ predictions, in HSF the voxel-wise Aleatoric Uncertainty $H(Y^i|X)$ is defined as[^2]:

$$
H(Y^i|X) \approx - \sum^M_{m=1}{\hat{p}^i_m \ln \hat{p}^i_m}
$$

where $\hat{p}^i_m$ is the frequency of the $m$th unique value in $Y^i$.


[^1]: https://www.wikiwand.com/en/Uncertainty_quantification

[^2]: Wang, G., Li, W., Aertsen, M., Deprest, J., Ourselin, S., & Vercauteren, T. (2019). Aleatoric
uncertainty estimation with test-time augmentation for medical image segmentation with
convolutional neural networks. Neurocomputing, 338, 34–45.
[https://doi.org/10.1016/j.neucom.2019.01.103](https://doi.org/10.1016/j.neucom.2019.01.103)
