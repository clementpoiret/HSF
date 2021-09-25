======================================
Hippocampal Segmentation Factory (HSF)
======================================

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5527122.svg
   :target: https://doi.org/10.5281/zenodo.5527122

The Hippocampal Segmentation Factory (HSF) is a Python package for
the segmentation of the hippocampal subfields in raw MRI volumes.

.. image:: https://raw.githubusercontent.com/clementpoiret/HSF/0537a69c6390d497157e0e6c95398610b6447ace/res/header.svg

The main idea is to have a click-button tool that allows the user to
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

Please note that the tool is still under development and is not yet
ready for production use. It uses multiple expert deep learning models
trained on 600+ manually segmented hippocampi (see `Which MRI modalities are usable in HSF?`_)
which are not yet fully trained.

HSF uses inference sessions provided by `ONNXRuntime <https://onnxruntime.ai>`_,
which means that it can be used *theoretically* on Windows, MacOS and Linux,
and the following hardware accelerations: CPU, CUDA, DirectML, OneDNN,
OpenVINO, TensorRT, NUPHAR, Vitis AI, ACL, ArmNN, MIGraphX, and Rockchip NPU.
Please be aware that we do not tested all possible configurations, as HSF
has been tested only on CPU and CUDA on Linux (Debian-based and Arch-based distros).


Installation
************

To install the package, first setup an environment suitable for `ONNX Runtime <https://onnxruntime.ai>`_.

If the ONNX Runtime isn't properly configured, you might be stuck running inference sessions on CPU, which is not optimal.

Then, simply run:

``pip install hsf``.

Quick start
***********

Once installed, HSF can be used simply by running the ``hsf`` command.

For example, to segment a set of T2w MRIs of 0.3*0.3*1.2, run:

``hsf files.path="~/Dataset/MRIs/" files.pattern="*T2w.nii" roiloc.contrast="t2" roiloc.margin=\[10,2,10\] segmentation=bagging_accurate segmentation.ca_mode="1/2/3"``

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
*************

As HSF is pretty modular, you can easily configure it to your needs thanks to Hydra.

Compose your configuration from those groups (group=option)

* augmentation: default
* files: default
* roiloc: default_t2iso
* segmentation: bagging_accurate, bagging_fast, single_accurate, single_fast

Override anything in the config (e.g. hsf roiloc.margin=[16, 2, 16])
You can also add specific configs absent from the default yaml files (e.g. hsf +augmentation.elastic.image_interpolation=sitkBSpline)
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

segmentation:

* ca_mode: 1/2/3
* models_path: ~/.hsf/models
* models:
   *  arunet_bag_0.onnx:
   *  url: https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1
   *  md5: 10026a4ef697871b7d49c08a4f16b6ae
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


How to improve segmentation quality?
************************************

If the segmentation is not good enough, you can try to improve it with the following steps:
- Try to augment the number of TTAs,
- Try to use a different ONNX model (by adding its ONNX to ``~/.hsf/models``),

If the segmentation is clearly absent or outside the hippocampus, it is because ROILoc failed.
This is caused by ANTs having troubles to perform registration, leading to a wrong bounding box.

Generally, performing a brain extraction step, our using another ``transform_type`` (e.g. ``SyN``)
solves this problem.

Also check that the margins are high engough, otherwise you might be missing some subfields
(crop effect).


Which MRI modalities are usable in HSF?
***************************************

We trained HSF using T1 (MPRAGE & MP2RAGE) and T2 (mostly TSE) modalities.

HSF should work with isotropic and non-isotropic images, but we do not encourage the segmentation
on 1mm iso images as the resolution is too low to distinguish between subfields.

We trained on CoroT2 with resolutions as low as 0.125*0.125*1.2mm.

You can of course try with other settings, feel free to report your results :)


Custom models
*************

You can use your own ONNX models by placing them in ``~/.hsf/models``, and providing the correct configuration (path & md5).

You can also just place your models there, and use our ``bagging*`` presets, they will be included in the plurality votes.


Performance tunning
*******************

Please refer to ONNXRuntime's documentation for setting-up the correct environment,
to benefit from the performance and scalability of hardware accelerations.


Authorship, Affiliations and Citations
**************************************

Authorship:

* C Poiret, UNIACT-NeuroSpin, CEA, Saclay University, France,
* A Bouyeure, UNIACT-NeuroSpin, CEA, Saclay University, France,
* S Patil, UNIACT-NeuroSpin, CEA, Saclay University, France,
* C Boniteau, UNIACT-NeuroSpin, CEA, Saclay University, France,
* M Noulhiane, UNIACT-NeuroSpin, CEA, Saclay University, France.

If you use this work, please cite it as follows:

``C. Poiret, et al. (2021). clementpoiret/HSF. Zenodo. https://doi.org/10.5281/zenodo.5527122``

This work licensed under MIT license was supported in part by the Fondation de France and the IDRIS/GENCI for the HPE Supercomputer Jean Zay.
