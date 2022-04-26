# Hub

In addition to provide an end-to-end solution to Hippocampal Subfields segmentation,
HSF provides a model hub that allows ***anyone*** to distribute their own segmentation ONNX models.

Those models are listed below, and directly accessible from the CLI, as in the example below:

```sh
hsf segmentation=single_accurate
```

**Default model**: `bagging_accurate`

## Built-in Segmentation Models

Those models are coming from our original work on Hippocampal Subfields segmentation.

They are trained on T1w and T2w images coming from multiple public and private datasets.
The population ranges from 4 to 80+ years old, with healthy, epileptic, MCI, Alzheimer and post-mortem patients.
MRI modalities includes MRIs from low-resolution T1s (1mm iso. MPRAGE), to high-resolution coro-T2s (0.125, 0.125, 1.2mm).

MRIs are coming from multiple acquisition sites, and multiple scanners (3T, 4T and 7T).

All the models are using the same `ARUnet` architecture, which will be detailed in a subsequent paper.

??? example "`single_fast` and `single_accurate` models"

    Those are the two most basic models. Inference is done with a single model trained
    on 98% of the full dataset, and tested on the remaining 2%.

    The accurate model does include test-time augmentation, which allows to compute
    more accurate and robust segmentations through a plurality vote.

    Test-time augmentation also allows the computation of an uncertainty map to analyze
    the quality of the resulting segmentation.

??? example "`bagging_fast` and `bagging_accurate` models"

    Those are the two more advanced methods. Inference is done with 5 models trained
    on different subsets of the dataset (random sampling with replacement).

    This allows to have models with different learned properties, offering a better
    segmentation, but a slower inference compared to the classic `single_*` models.

    The accurate method does include test-time augmentation, which allows to compute
    more accurate and robust segmentations through a plurality vote.

    Test-time augmentation also allows the computation of an uncertainty map to analyze
    the quality of the resulting segmentation.

??? example "`single_sq` and `bagging_sq` models"

    Those are the two most advanced methods. Inference is done with 1 or 5 models
    trained on different subsets of the dataset (random sampling with replacement).

    This allows to have models with different learned properties, offering a better
    segmentation, but a slower inference compared to the classic `single_*` models.

    Here, the models are trained with a sparsification method which allows to reduce
    the computational cost of the inference while retaining an optimal sub-model
    following the lottery ticket hypothesis.

    The `sq` method also includes Quantization Aware Training to improve even
    more the efficiency of the inference.

    Those methods are appropriate for recent hardware supporting efficient computations
    on sparse vectors. Int8 Quantization is better used on hardware supporting fast
    int8 matrix computations. For example, on a CPU supporting the AVX512-VNNI vector
    instruction set, your best bet is to use the `bagging_sq` segmentation method.

    Test-time augmentation also allows the computation of an uncertainty map to analyze
    the quality of the resulting segmentation.

## Third-party Segmentation Models

To date, there is no third-party segmentation model available :pensive:.

If you are a researcher and you want to contribute to the model hub, please check the [contributing guide](contributing.md).
Basically, all you need to do is to export your model in ONNX format, upload it, and make a pull request with a simple YAML file defining how to download your models.
