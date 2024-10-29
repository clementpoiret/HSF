======================================
Hippocampal Segmentation Factory (HSF)
======================================

Exhaustive documentation available at: `hsf.rtfd.io <https://hsf.rtfd.io/>`_

**Current Models version:** 4.0.0

.. list-table::
    :header-rows: 1

    * - Python Package
      - Code Quality
      - Misc
    * - .. image:: https://github.com/clementpoiret/HSF/actions/workflows/python-app.yml/badge.svg?branch=master
        .. image:: https://badge.fury.io/py/hsf.svg
           :target: https://badge.fury.io/py/hsf
        .. image:: https://img.shields.io/pypi/dm/hsf
           :alt: PyPI - Downloads
      - .. image:: https://app.codacy.com/project/badge/Grade/cf02d1f84739401ba695e24f333c23b7
           :target: https://www.codacy.com/gh/clementpoiret/HSF/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=clementpoiret/HSF&amp;utm_campaign=Badge_Grade
        .. image:: https://app.codacy.com/project/badge/Coverage/cf02d1f84739401ba695e24f333c23b7
           :target: https://www.codacy.com/gh/clementpoiret/HSF/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=clementpoiret/HSF&amp;utm_campaign=Badge_Grade
        .. image:: https://api.codeclimate.com/v1/badges/e0bf481dcbf3eecebefd/maintainability
           :target: https://codeclimate.com/github/clementpoiret/HSF/maintainability
           :alt: Maintainability
      - .. image:: https://readthedocs.org/projects/hsf/badge/?version=latest
           :target: https://hsf.readthedocs.io/en/latest/?badge=latest
           :alt: Documentation Status
        .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5527122.svg
           :target: https://doi.org/10.5281/zenodo.5527122


The Hippocampal Segmentation Factory (HSF) is a Python package for
the segmentation of the hippocampal subfields in raw MRI volumes.

.. image:: https://raw.githubusercontent.com/clementpoiret/HSF/master/docs/resources/header.svg

The main idea is to have a one-liner tool that allows the user to
segment the hippocampal subfields in a given raw image (T1w or T2w), while keeping
as much modularity and customization options as possible.

HSF will be able to segment the following subfields:

- Dentate gyrus (DG),
- Cornu Ammonis (CA1, CA2 & CA3) in a flexible way (e.g. you can ask to combine CA2 and CA3),
- Subiculum (SUB).

HSF will segment the hippocampus from head to tail: it will produce
an homogeneous segmentation from the anterior hippocampus (head), to
the posterior hippocampus (tail), without assigning a specific head
or tail class.

HSF results from a collaborative effort:

1. We are continuously working on improving the segmentation of the subfields,
   mainly by adding new manually segmented MRIs (feel free to send us yours if you can, thanks!)
2. HSF proposes a "Model Hub", meaning that anyone can distribute their own ONNX segmentation
   model. Just send us a small `*.yaml` config file, and the end-user will effortlessly be able to
   use HSF with your model.

Please note that the tool is still under development and is not yet
ready for production use. It uses multiple expert deep learning models
trained on 700+ manually segmented hippocampi which are not yet fully polished.

HSF uses inference sessions provided by `ONNXRuntime <https://onnxruntime.ai>`_,
which means that it can be used *theoretically* on Windows, MacOS and Linux,
and the following hardware accelerations: CPU, CUDA, DirectML, OneDNN,
OpenVINO, TensorRT, NUPHAR, Vitis AI, ACL, ArmNN, MIGraphX, and Rockchip NPU.
Please be aware that we do not tested all possible configurations, as HSF
has been tested only on CPU and CUDA on Linux (Debian-based and Arch-based distros).

Since v1.0.0, HSF also provides a `DeepSparse backend <https://neuralmagic.com/technology/>`_
which can be used in conjunction with pruned and int8 quantized models
to deliver a much faster CPU inference speed (see [Hardware Acceleration](user-guide/configuration.md)
section).


Table of Contents...
====================

.. contents:: ...To guide you in the challenging world of hippocampal subfields segmentation :)

Development Environment
=======================

ROILoc relies on Nix_ and Devenv_.

.. _Nix: https://nixos.org/download/
.. _Devenv: https://devenv.sh

**Step 1**: Install Nix_:
::

    sh <(curl -L https://nixos.org/nix/install) --daemon

**Step 2**: Install Devenv_:
::

    nix-env -iA devenv -f https://github.com/NixOS/nixpkgs/tarball/nixpkgs-unstable

**Step 3**: 
::

    devenv shell

That's it :)

If you want something even easier, install direnv_ and
allow it to automatically activate the current env (``direnv allow``).

.. _direnv: https://direnv.net/

Installation
============

To install the package, first setup an environment suitable for your backend (e.g. `ONNX Runtime <https://onnxruntime.ai>`_).

If the environment isn't properly configured, you might be stuck running inference sessions on CPU, which is not optimal unless you use the DeepSparse backend.

Then, simply run:

``pip install hsf["your_hardware"]``.

You should always specify the hardware you want to use, as it will install the proper dependencies, supported choices are ``cpu``, ``gpu`` and ``sparse``.

So for example, if you want to use the GPU backend, run:

``pip install hsf["gpu"]``.


Quick start
===========

Once installed, HSF can be used simply by running the ``hsf`` command.

For example, to segment a set of T2w MRIs of 0.3*0.3*1.2, run:

``hsf files.path="~/Dataset/MRIs/" files.pattern="*T2w.nii" roiloc.contrast="t2" roiloc.margin=[10,2,10] segmentation=bagging_accurate segmentation.ca_mode="1/2/3"``

Now, let's dive into the details.

``files.path`` and ``files.pattern`` are mandatory parameters.
They specify the path to the dataset (or MRI) and the pattern to find the files.

All parameters starting with ``roiloc.`` are directly linked to our home-made ROI location algorithm.
You can find more information about it in the `related GitHub repository <https://github.com/clementpoiret/ROILoc>`_.

To date, we propose 4 different segmentation algorithms (from the fastest to the most accurate):

- ``single_fast``: a segmentation is performed on the whole volume by only one model,
- ``single_accurate``: a single model segments the same volume that has been augmented 20 times through TTA,
- ``single_sq``: like ``single_accurate``, but using int8-quantized sparse models for a fast and efficient inference,
- ``bagging_fast``: a bagging ensemble of 5 models is used to segment the volume without TTA,
- ``bagging_accurate``: a bagging ensemble of 5 models is used to segment the volume with TTA,
- ``bagging_sq``: like ``bagging_accurate``, but using int8-quantized sparse models for a fast and efficient inference.

Finally, ``segmentation.ca_mode`` is a parameter that allows to combine CA1, CA2 and CA3 subfields.
It is particularly useful when you want to segment low-resolution images where it makes no sense to
distinguish between CA's subfields.


Configuration
=============

As HSF is pretty modular, you can easily configure it to your needs thanks to Hydra.

Compose your configuration from those groups (group=option)

* augmentation: default
* files: default
* hardware: deepsparse, onnxruntime
* multispectrality: default
* roiloc: default_corot2, default_t2iso
* segmentation: bagging_accurate, bagging_fast, bagging_sq, single_accurate, single_fast, single_sq

Override anything in the config (e.g. hsf roiloc.margin=[16,2,16])

You can also add specific configs absent from the default yaml files
(e.g. hsf +augmentation.elastic.image_interpolation=sitkBSpline)

Fields set with ??? are mandatory.

   files:

   * path: ???
   * pattern: ???
   * mask_pattern: ``*mask.nii.gz``
   * output_dir: hsf_outputs

   roiloc:

   * contrast: t2
   * roi: hippocampus
   * bet: false
   * transform_type: AffineFast
   * margin: [8, 8, 8]
   * rightoffset: [0, 0, 0]
   * leftoffset: [0, 0, 0]

   segmentation:

   * ca_mode: 1/2/3
   * models_path: ~/.hsf/models
   * models:
      *  arunet_bag_0.onnx:
      *  url: https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1
      *  xxh3_64: d0de65baa81d9382
      * segmentation:
         * test_time_augmentation: true
         * test_time_num_aug: 20

   augmentation:

   * flip:
      * axes:
         * LR
      * flip_probability: 0.5
      * affine_probability: 0.75
      * affine:
         * scales: 0.2
         * degrees: 15
         * translation: 3
         * isotropic: false
      * elastic_probability: 0.25
      * elastic:
         * num_control_points: 4
         * max_displacement: 4
         * locked_borders: 0

   multispectrality:
   
   * pattern: null
   * same_space: true
   * registration:
     * type_of_transform: Affine

   hardware:
  
   * engine: onnxruntime
   * engine_settings:
     * execution_providers: ["CUDAExecutionProvider","CPUExecutionProvider"]
     * batch_size: 1


Changelogs
==========

HSF
---

**Version 1.2.2**

* Updated ROILoc to v0.4.1 (latest ANTs version),
* Updated dependencies,
* Added a proper dev env using Nix,
* Switched from poetry to uv.

**Version 1.2.1**

* Option to override already segmented mris.
* Minor fixes and optimizations.

**Version 1.2.0**

* Released finetuning scripts,
* New models trained on more data,
* Models are now hosted on HuggingFace,
* Bug fixes and optimizations.

**Version 1.1.3**

* Lower onnxruntime dependency to min 1.8.0

**Version 1.1.2**

* ***BREAKING CHANGE***: HSF needs to be installed using extra dependencies depending on the backend you want to use.
  See the [installation guide](https://hsf.readthedocs.io/en/latest/user-guide/installation/) for more details.
* Updated dependencies
* Fixed installation on MacOS
 
**Version 1.1.1**

* Added whole-hippocampus segmentation

**Version 1.1.0**

* New optional multispectral mode de segment from both T1 AND T2 images
* Bug fixes and optimizations

**Version 1.0.1**

* Fix batch size issue

**Version 1.0.0**

* Added Uncertainty Maps for post-hoc analysis of segmentation results,
* Support for DeepSparse backend (CPU inference only),
* Introduced **HSF's Model Hub**,
* Support for batch inference (all backends),
* Check for updates at startup,
* Bug fixes and optimizations.

**Version 0.1.2**

* Added build-in support for offsets to recenter the hippocampus in ROILoc,
* Added support for the customization of Hardware Execution Providers.

**Version 0.1.1**

* Fixed CUDA Execution Provider.

**Version 0.1.0**

* Initial release.


Models
------

**Version 4.0.0**

* Models trained on hippocampal subfields from Clark et al. (2023) dataset (https://doi.org/10.1038/s41597-023-02449-9),
* Models are now hosted on HuggingFace,
* Bug fixes and optimizations.

**Version 3.0.0**

* More data (coming from the Human Connectome Project),
* New sparse and int8-quantized models.

**Version 2.1.1**

* Fixed some tails in 3T CoroT2w images (MemoDev)

**Version 2.1.0**

* Corrected incorrect T1w labels used for training,
* Trained on slightly more data (T1w @1.5T & 3T, T2w; Healthy, Epilepsy & Alzheimer)

**Version 2.0.0**

* Trained with more T1w and T2w MRIs,
* Trained on more hippocampal sclerosis and Alzheimer's disease cases,
* Updated training pipeline (hyperparameter tuning),
* `single` models are now independant from bags.

**Version 1.0.0**

* Initial release.


Documentation
==========================

For more details about HSF's configuration and internal parameters, please refer to
our `documentation <https://hsf.rtfd.io/>`_.


Authorship, Affiliations and Citations
======================================

Authorship:

* C Poiret, UNIACT-NeuroSpin, CEA, Saclay University, France,
* A Bouyeure, UNIACT-NeuroSpin, CEA, Saclay University, France,
* S Patil, UNIACT-NeuroSpin, CEA, Saclay University, France,
* C Boniteau, UNIACT-NeuroSpin, CEA, Saclay University, France,
* M Noulhiane, UNIACT-NeuroSpin, CEA, Saclay University, France.

If you use this work, please cite it as follows:

```
@ARTICLE{10.3389/fninf.2023.1130845,
AUTHOR={Poiret, Clement and Bouyeure, Antoine and Patil, Sandesh and Grigis, Antoine and Duchesnay, Edouard and Faillot, Matthieu and Bottlaender, Michel and Lemaitre, Frederic and Noulhiane, Marion},
TITLE={A fast and robust hippocampal subfields segmentation: HSF revealing lifespan volumetric dynamics},	
JOURNAL={Frontiers in Neuroinformatics},
VOLUME={17},
YEAR={2023},
URL={https://www.frontiersin.org/articles/10.3389/fninf.2023.1130845},
DOI={10.3389/fninf.2023.1130845},
ISSN={1662-5196},
ABSTRACT={The hippocampal subfields, pivotal to episodic memory, are distinct both in terms of cyto- and myeloarchitectony. Studying the structure of hippocampal subfields in vivo is crucial to understand volumetric trajectories across the lifespan, from the emergence of episodic memory during early childhood to memory impairments found in older adults. However, segmenting hippocampal subfields on conventional MRI sequences is challenging because of their small size. Furthermore, there is to date no unified segmentation protocol for the hippocampal subfields, which limits comparisons between studies. Therefore, we introduced a novel segmentation tool called HSF short for hippocampal segmentation factory, which leverages an end-to-end deep learning pipeline. First, we validated HSF against currently used tools (ASHS, HIPS, and HippUnfold). Then, we used HSF on 3,750 subjects from the HCP development, young adults, and aging datasets to study the effect of age and sex on hippocampal subfields volumes. Firstly, we showed HSF to be closer to manual segmentation than other currently used tools (p < 0.001), regarding the Dice Coefficient, Hausdorff Distance, and Volumetric Similarity. Then, we showed differential maturation and aging across subfields, with the dentate gyrus being the most affected by age. We also found faster growth and decay in men than in women for most hippocampal subfields. Thus, while we introduced a new, fast and robust end-to-end segmentation tool, our neuroanatomical results concerning the lifespan trajectories of the hippocampal subfields reconcile previous conflicting results.}
}
```

This work licensed under MIT license was supported in part by the Fondation de France and the IDRIS/GENCI for the HPE Supercomputer Jean Zay.
