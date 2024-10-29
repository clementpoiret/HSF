# HSF - Documentation

<p align="center">
    <img src="https://raw.githubusercontent.com/clementpoiret/HSF/master/docs/resources/hsf_logo.svg" width="200">
    <br>
    <font size="+2"><b>Hippocampal</b> <i>Segmentation</i> Factory</font>
    <br>
    <b>Current HSF version:</b> 1.2.2<br>
    <b>Built-in Models version:</b> 4.0.0<br>
    <b>Models in the Hub:</b> 4
</p>

____

<p align="center">
    <font size="-1"><i>Propulsed by</i></font>
    <br>
    <img id="cea" src="resources/logos/cea.svg" width=40/>
    <img id="neurospin" src="resources/logos/neurospin.png" width=110/>
    <img id="up" src="resources/logos/up.png" width=110/>
    <img id="ups" src="resources/logos/ups.png" width=110/>
    <img id="idris" src="resources/logos/idris.png" width=70/>
    <img id="genci" src="resources/logos/genci.png" width=35/>
    <img id="hydra" src="resources/logos/hydra.png" width=55/>
    <img id="onnx" src="resources/logos/onnx.png" width=35/>
    <img id="neuralmagic" src="resources/logos/neuralmagic.png" width=35/>
</p>
____

<br>

| Package                                                                                                                                                                                                                                               | Code Quality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Misc                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![Python Package](https://github.com/clementpoiret/HSF/actions/workflows/python-app.yml/badge.svg?branch=master) [![Version](https://badge.fury.io/py/hsf.svg)](https://badge.fury.io/py/hsf) ![PyPI - Downloads](https://img.shields.io/pypi/dm/hsf) | [![Code Quality](https://app.codacy.com/project/badge/Grade/cf02d1f84739401ba695e24f333c23b7)](https://www.codacy.com/gh/clementpoiret/HSF/dashboard?utm_source=github.com&utm_medium=referral&utm_content=clementpoiret/HSF&utm_campaign=Badge_Grade) [![Codacy Coverage Badge](https://app.codacy.com/project/badge/Coverage/cf02d1f84739401ba695e24f333c23b7)](https://www.codacy.com/gh/clementpoiret/HSF/dashboard?utm_source=github.com&utm_medium=referral&utm_content=clementpoiret/HSF&utm_campaign=Badge_Coverage) [![Maintainability](https://api.codeclimate.com/v1/badges/e0bf481dcbf3eecebefd/maintainability)](https://codeclimate.com/github/clementpoiret/HSF/maintainability) | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5527122.svg)](https://doi.org/10.5281/zenodo.5527122) [![Documentation Status](https://readthedocs.org/projects/hsf/badge/?version=latest)](https://hsf.readthedocs.io/en/latest/?badge=latest) |

The Hippocampal Segmentation Factory (HSF) is a Python package for
the segmentation of the hippocampal subfields in raw MRI volumes.

![Header](resources/header.svg)

## Purpose & Use Cases

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

HSF results from a collaborative effort:

1. We are continuously working on improving the segmentation of the subfields,
   mainly by adding new manually segmented MRIs (feel free to send us yours if you can, thanks!)
2. HSF proposes a "Model Hub", meaning that anyone can distribute their own ONNX segmentation
   model. Just send us a small `*.yaml` config file, and the end-user will effortlessly be able to
   use HSF with your model.

Please note that the tool is still under development and is not yet
ready for production use. It uses multiple expert deep learning models
trained on 600+ manually segmented hippocampi (see the [F.A.Q. section](faq.md))
which are not yet fully polished.

## Technical Features

HSF uses inference sessions provided by [ONNXRuntime](https://onnxruntime.ai),
which means that it can be used *theoretically* on Windows, MacOS and Linux,
and the following hardware accelerations: CPU, CUDA, DirectML, OneDNN,
OpenVINO, TensorRT, NUPHAR, Vitis AI, ACL, ArmNN, MIGraphX, and Rockchip NPU.
Please be aware that we do not tested all possible configurations, as HSF
has been tested only on CPU and CUDA on Linux (Debian-based and Arch-based distros).

Since v1.0.0, HSF also provides a [DeepSparse backend](https://neuralmagic.com/technology/)
which can be used in conjunction with pruned and int8 quantized models
to deliver a much faster CPU inference speed (see [Hardware Acceleration](user-guide/configuration.md)
section).

Since v1.2.0, the complete training code is available at [hsf_train](https://github.com/clementpoiret/hsf_train).
The `hsf_train` repository also contains easy to use scripts to train OR **finetune your own models**.

____

HSF is distributed under the [MIT license](about/license.md):

| Permissions                                                   | Conditions                                                  | Limitations           |
| ------------------------------------------------------------- | ----------------------------------------------------------- | --------------------- |
| Commercial use<br>Distribution<br>Modification<br>Private use | A copy of the license and copyright notice must be included | Liability<br>Warranty |

!!! note ""
    This work has been partly founded by the Fondation de France.
    HSF has been made possible by the IDRIS/GENCI with the HPE Jean Zay Supercomputer.
    Latest models have been trained with the help of [Scaleway](https://www.scaleway.com/) and [Hugging Face](https://huggingface.co/).

    CEA Saclay | NeuroSpin | UNIACT-Inserm U1141
