======================================
Hippocampal Segmentation Factory (HSF)
======================================

Exhaustive documentation available at: `hsf.rtfd.io <https://hsf.rtfd.io/>`_

**Current Models version:** 2.0.0

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


Installation
============

To install the package, first setup an environment suitable for your backend (e.g. `ONNX Runtime <https://onnxruntime.ai>`_).

If the environment isn't properly configured, you might be stuck running inference sessions on CPU, which is not optimal unless you use the DeepSparse backend.

Then, simply run:

``pip install hsf``.


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
- ``bagging_fast``: a bagging ensemble of 5 models is used to segment the volume without TTA,
- ``bagging_accurate``: a bagging ensemble of 5 models is used to segment the volume with TTA.

Finally, ``segmentation.ca_mode`` is a parameter that allows to combine CA1, CA2 and CA3 subfields.
It is particularly useful when you want to segment low-resolution images where it makes no sense to
distinguish between CA's subfields.


Configuration
=============

As HSF is pretty modular, you can easily configure it to your needs thanks to Hydra.

Compose your configuration from those groups (group=option)

* augmentation: default
* files: default
* roiloc: default_t2iso
* segmentation: bagging_accurate, bagging_fast, single_accurate, single_fast

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


Changelogs
==========

HSF
---

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

``C. Poiret, et al. (2021). clementpoiret/HSF. Zenodo. https://doi.org/10.5281/zenodo.5527122``

This work licensed under MIT license was supported in part by the Fondation de France and the IDRIS/GENCI for the HPE Supercomputer Jean Zay.
