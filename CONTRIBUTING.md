# How to contribute

As a PhD student, all my time cannot be dedicated to improving and maintaining this project, so any contribution is very welcome,
from suggestions to bug reports, feature requests, and even code contributions.

`HSF` is designed to be your last tool needed for hippocampal segmentation, we want it fully customizable, and we want you to be able
to use it as a tool for your own research, even on your own segmentation models. Feel free to make `HSF` it a way it is useful for you.

## Improving `HSF`

### Coding conventions

Internally, we use [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html).

Please try to stick to it. To make it easier for you, try YAPF :)

### Documentation

Every new function should be documented. In the code docstrings are mandatory as in the example below:

```python
def load_from_config(path: str, pattern: str) -> list:
    """
    Loads all mris from a given path with a given pattern.

    Args:
        path (str): Path to the mris.
        pattern (str): Pattern to search for.

    Returns:
        list: List of mris.
    """
    p = Path(path).expanduser()
    return list(p.glob(pattern))
```

Every top-level functionality directly accessible to the end-user has to be documented in the [`HSF` doc](https://hsf.rtfd.io/)

### Configurability

It is very important to us that all settings are configurable through Hydra. This is why we have a `config.yaml` file defining all parameters
used in `HSF`.

### Testing

`HSF` is automatically tested with `pytest`. Please be sure that your code is tested properly.

## Improving Segmentation Models

If you found a way to improve our segmentation quality (e.g. by tweaking TTA's default parameters), please open an issue or make a PR.

Additionally data is the new gold. If you have incorrect segmentations, feel free to correct them, and then send them to us.
The data will be kept private, stored in secured infrastructures, and will be used in the next training iteration of HSF.

We would be very grateful.

We always seek for new datasets, so if you have a dataset with manual segmentations of hippocampi, or heard about a new released dataset, please let us know.

As soon as we have obtained a relatively good amount of new segmentations (maybe 10 to 20 new hippocampi), we will retrain our models, and we will release a new version of HSF.
You will then be able to benefit from the improved segmentation by running `pip install -U hsf` as soon as the new version is released.

Additionaly, if you trained your own models and you want to share them with the community, please consider making a pull request with
a configuration file like the ones in `hsf/conf/segmentation/*.yaml`.

For example, you can submit `hsf/conf/segmentation/johndoe2021.yaml`:

```yaml
# Configuration file implementing the segmentation models of
# John Doe, et al., 2021.

ca_mode: "1/2/3"
models_path: "~/.hsf/models/bagging/"
models:
  johndoe_etal_2021_0.onnx:
    url: "https://url-to-your-trained-model/model0.onnx"
    xxh3_64: "f0f0f0f0f0f0f0f0"
  johndoe_etal_2021_1.onnx:
    url: "https://url-to-your-trained-model/model1.onnx"
    xxh3_64: "f1f1f1f1f1f1f1f1"

segmentation:
  test_time_augmentation: True
  test_time_num_aug: 42
```

By doing so, future users will be able to use your models by running `hsf segmentation=johndoe2021`.
