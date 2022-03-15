# Upgrading

Use pip to upgrade HSF:

```sh
pip install -U hsf
```

# Maintenance Team

Current maintainers:

[@clementpoiret](https://github.com/clementpoiret)

# Changelogs

## HSF

### Version 1.1.0 (N/A)

* Bug fixes and optimizations

### Version 1.0.1 (2021-12-07)

* Fixed batch size issue

### Version 1.0.0 (2021-11-12)

* Added Uncertainty Maps for post-hoc analysis of segmentation results,
* Support for DeepSparse backend (CPU inference only),
* Introduced **HSF's Model Hub**,
* Support for batch inference (all backends),
* Check for updates at startup,
* Bug fixes and optimizations.

### Version 0.1.2 (2021-09-27)

* Added the possibility to add an offset to the initial bounding box detected by ROILoc,
* Added the possibility to customize Hardware Execution Providers (defaults to `CUDAExecutionProvider` and `CPUExecutionProvider`).

### Version 0.1.1 (2021-09-25)

* Fixed CUDA Execution Provider

### Version 0.1.0 (2021-09-24)

* Initial release

## Models

### Version 2.1.1 (2022-03-03)

* Fixed some tails in 3T CoroT2w images (MemoDev)

### Version 2.1.0 (N/A)

* Corrected incorrect T1w labels used for training,
* Trained on slightly more data (T1w @1.5T & 3T, T2w; Healthy, Epilepsy & Alzheimer)

### Version 2.0.0 (2021-11-12)

* Trained with more T1w and T2w MRIs,
* Trained on more hippocampal sclerosis and Alzheimer's disease cases,
* Updated training pipeline (hyperparameter tuning),
* `single` models are now independant from bags,
* `bagging` have `sparse` and `sparseqat` versions for sparsification and Quantization Aware Training.

### Version 1.0.0 (2021-09-24)

* Initial release
