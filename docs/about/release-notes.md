# Upgrading

Use pip to upgrade HSF:

```sh
pip install -U hsf["your_hardware"]
```

# Maintenance Team

Current maintainers:

[@clementpoiret](https://github.com/clementpoiret)

# Changelogs

## HSF

### Version 1.2.1 (2024-03-29)

* Added an option to override already segmented mris.
* Minor fixes and optimizations.

### Version 1.2.0 (2024-02-06)

* Released finetuning scripts,
* New models trained on more data,
* Models are now hosted on HuggingFace,
* Bug fixes and optimizations.

### Version 1.1.1 (2022-04-27)

* Added whole-hippocampus segmentation

### Version 1.1.0 (2022-04-25)

* New optional multispectral mode de segment from both T1 AND T2 images
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

### Version 4.0.0 (2024-02-06)

* New models trained on more data,
* Models integrate architecture improvements,
* Models are now hosted on HuggingFace.

### Version 3.0.0 (2022-04-24)

* More data (coming from the Human Connectome Project),
* New sparse and int8-quantized models.

### Version 2.1.1 (2022-03-03)

* Fixed some tails in 3T CoroT2w images (MemoDev)

### Version 2.1.0 (N/A)

* Corrected incorrect T1w labels used for training,
* Trained on slightly more data (T1w @1.5T & 3T, T2w; Healthy, Epilepsy & Alzheimer)

### Version 2.0.0 (2021-11-12)

* Trained with more T1w and T2w MRIs,
* Trained on more hippocampal sclerosis and Alzheimer's disease cases,
* Updated training pipeline (hyperparameter tuning),
* `single` models are now independant from bags.

### Version 1.0.0 (2021-09-24)

* Initial release
