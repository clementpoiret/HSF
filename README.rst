======================================
Hippocampal Segmentation Factory (HSF)
======================================

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5507086.svg
   :target: https://doi.org/10.5281/zenodo.5507086

The Hippocampal Segmentation Factory (HSF) is a Python package for
the segmentation of the hippocampal subfields in raw MRI volumes.

.. image:: res/header.svg

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

To date, the package **IS NEITHER RELEASED nor READY FOR USE**.

Once the package is ready for use, it will be released to PyPI, and
you'll be able to install it simply by running ``pip install hsf``.

Quick start
***********

Configuration
*************

How to improve segmentation quality?
************************************

Which MRI modalities are usable in HSF?
***************************************

Custom models
*************

Performance tunning
*******************
