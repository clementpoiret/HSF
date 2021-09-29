# Welcome to the Hippocampal Segmentation Factory (HSF) Documentation

**Current HSF version:** 0.1.2

**Current Models version:** 1.0.0

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5527122.svg)](https://doi.org/10.5281/zenodo.5527122)
[![Documentation Status](https://readthedocs.org/projects/hsf/badge/?version=latest)](https://hsf.readthedocs.io/en/latest/?badge=latest)

The Hippocampal Segmentation Factory (HSF) is a Python package for
the segmentation of the hippocampal subfields in raw MRI volumes.

![Header](https://raw.githubusercontent.com/clementpoiret/HSF/0537a69c6390d497157e0e6c95398610b6447ace/res/header.svg)

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
trained on 600+ manually segmented hippocampi (see the [F.A.Q. section](faq.md))
which are not yet fully polished.

HSF uses inference sessions provided by [ONNXRuntime](https://onnxruntime.ai),
which means that it can be used *theoretically* on Windows, MacOS and Linux,
and the following hardware accelerations: CPU, CUDA, DirectML, OneDNN,
OpenVINO, TensorRT, NUPHAR, Vitis AI, ACL, ArmNN, MIGraphX, and Rockchip NPU.
Please be aware that we do not tested all possible configurations, as HSF
has been tested only on CPU and CUDA on Linux (Debian-based and Arch-based distros).
