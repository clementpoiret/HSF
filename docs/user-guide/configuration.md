# Configuration

HSF uses [`Hydra`](https://hydra.cc) to manage its configuration.

> Hydra is an open-source Python framework that simplifies the development of research and other complex applications. The key feature is the ability to dynamically create a hierarchical configuration by composition and override it through config files and the command line. The name Hydra comes from its ability to run multiple similar jobs - much like a Hydra with multiple heads.


## How to use Hydra?

HSF is configured using the following config groups:

```
conf
│   config.yaml   
│
└───augmentation
│   │   default.yaml
│   
└───files
│   │   default.yaml
│
└───hardware
│   │   default.yaml
│
└───roiloc
│   │   default_corot2.yaml
│   │   default_t2iso.yaml
│
└───segmentation
    │   single_fast.yaml
    │   single_accurate.yaml
    │   bagging_fast.yaml
    │   bagging_accurate.yaml
```

Groups can be selected with `group=option`. For example: `hsf segmentation=bagging_fast`

Each individual option can be overriden, e.g. `hsf roiloc.margin=[16,8,16]`

You can also add specific configs absent from the default yaml files (e.g. `hsf +augmentation.elastic.image_interpolation=sitkBSpline`)


## Configuration details

Every `*.yaml` file defines a set of parameters influencing the segmentation, as detailed below.


### Inputs & Outputs

I/O are managed through the `files.*` arguments. Default parameters are defined in [`conf/files/default.yaml`](https://github.com/clementpoiret/HSF/blob/master/hsf/conf/files/default.yaml).

- `files.path` and `files.pattern` are mandatory arguments and respectively define where to search for MRIs, and how to find them through a `glob()` pattern.
- `files.mask_pattern` defines how to find brain extraction masks for registration purposes (see [ROILoc documentation](user-guide/roiloc.md)).
- `files.output_dir` defines where to store temporary files in a relative subject directory.

The following example will recursively search all `*T2w.nii.gz` files in the `~Datasets/MRI/` folder, for search a `*T2w_bet_mask.nii.gz` located next to each T2w images:

```
hsf files.path="~/Datasets/MRI/" files.pattern="**/*T2w.nii.gz" files.mask_pattern="*T2w_bet_mask.nii.gz
```


### Preprocessing pipeline

The preprocessing pipeline is kept as minimal as possible.

First, it is cropped according to the following pipeline using [`ROILoc`](roiloc.md), by registering an MNI template to the image.
As we already know the locations of the hippocampi in the MNI, we can infer the locations of the hippocampi in the subject's space.

As the process is error-prone / imprecise by construction, we also apply margins and offsets to the bounding boxes.

![ROILoc](../resources/roiloc.svg)

To customize ROILoc parameters, please refer to its dedicated [`ROILoc` page](roiloc.md).

Each crop is then Z-Normalized, and padded to ensure the shape is a multiple of 8.


### Segmentation Models

Our segmentation models need to be downloaded prior to running the HSF pipeline.

By default, they are stored in `~/HSF/models/*`. This folder is set by the argument `segmentation.models_path`.
For example, you can override this path by running:

```
hsf segmentation.models_path="/mnt/models/"
```

In the config files, the models are hardcoded by two parameters: an URL, and an xxHash3_64 hash to ensure the correct model is loaded.
We opted for xxHash bacause it is fast and has a very low collision rate. We removed MD5 checksum because of its known security risks.

If needed, you can even use your own models by running the following example:

```
hsf segmentation=single_accurate segmentation.models={"custom_model.onnx":{"url":"https://url.to/your/model.onnx","xxh3_64":"f0f0f0f0f0f0f0f0"}}
```

!!! warning "Note on ONNX models"
    All versions of ONNX Runtime will support ONNX opsets all the way back to (and including) opset version 7.
    To date, ONNX Runtime 1.10.0 supports models with `7 <= opset <= 15`.

    Please also be aware that input sizes aren't fixed. Therefore, please set dynamic dimensions when you export your models.

    For example:

    ```python
    import torch

    model = SegmentationModel()
    model.eval()

    dummy_input = torch.randn(1, 1, 16, 16, 16)
    torch.onnx.export(model,
                      dummy_input,
                      "custom_model.onnx",
                      input_names=["input"],
                      output_names=["output"],
                      dynamic_axes={
                          "input": {
                              0: "batch",
                              2: "x",
                              3: "y",
                              4: "z"
                          },
                          "output": {
                              0: "batch",
                              2: "x",
                              3: "y",
                              4: "z"
                          }
                      },
                      opset_version=13)
    ```

### Test-time Augmentation

### Hardware Acceleration
