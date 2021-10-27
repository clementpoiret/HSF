---
title: 'HSF as a Future-Proof Solution to Hippocampal Subfields Segmentation in MRI'
tags:
  - python
  - mri
  - brain
  - medical-imaging
  - deep-learning
authors:
  - name: Clement Poiret
    orcid: 0000-0002-1571-2161
    affiliation: "1, 2"
  - name: Antoine Bouyeure
    affiliation: "1, 2"
  - name: Sandesh Patil
    affiliation: "1, 2"
  - name: Cécile Boniteau
    affiliation: "1, 2"
  - name: Antoine Grigis
    affiliation: 3
  - name: Edouard Duchesnay
    affiliation: 3
  - name: Frédéric Lemaître
    affiliation: 4
  - name: Marion Noulhiane^[corresponding author]
    affiliation: "1, 2"
affiliations:
 - name: NeuroSpin, UNIACT, CEA Saclay, France
   index: 1
 - name: Inserm U1141, Paris University, France
   index: 2
 - name: NeuroSpin, BAOBAB, CEA Saclay, France
   index: 3
 - name: CETAPS EA n°3832, Université de Rouen, France
   index: 4  
date: 02 October 2021
bibliography: paper.bib


---

# Summary

The hippocampus is a key player of mnesic functions and has been shown to be implied in diverse pathologies such as mild cognitive impairment or Alzheimer's disease. Studying the anatomo-functional properties of the hippocampus and its subfields is a mandatory path to understand such conditions and requires reliable and robust segmentations of MRI data. Moreover, the growing size of publicly available datasets calls for faster and more efficient segmentation algorithms. As the current methodologies are shown to be either imprecise, slow or inconvenient, we propose a novel tool called the Hippocampal Segmentation Factory (`HSF`) to segment the hippocampal subfields in T1w or T2w MRIs.

`HSF` is designed to be a fully customizable end-to-end pipeline, handling tasks from the preprocessing of raw anatomical images, to the segmentation of the subfields through specialized and highly efficient Deep Learning models on any hardware acceleration platform such as CUDA, TensorRT or OpenVINO. `HSF` also supports the state-of-the-art DeepSparse compute engine, providing GPU-class performances on CPU.

Even if we use ever-improving models regularly trained with SotA methods with an increasing amount of manually labeled MRIs, we propose `HSF` as a future-proof tool where researchers can codelessly test and use their own ONNX models through a simple CLI argument.

# Statement of Need

The hippocampus plays a major role in specific functions of the brain like the episodic memory, the memory containing specific spatio-temporal details. Divided in hippocampal subfields - namely the Cornu Ammonis, the Dentate Gyrus and the Subiculum - it is actively involved in episodic memory, learning, and decision making. Thus, those substructures are determining an important part of one's behavior during his whole lifespan from the emergence of episofic memory in children to age-dependant cognitive decline. Hippocampal subfields have been shown to be implied in pathological conditions such as Alzheimer's disease, or Temporal lobe epilepsy [@todaRoleAdultHippocampal2019].

Therefore, their exist a need for a precise and accurate delineation of those subfields in order to study both healthy and pathological conditions. This delineation process appears to be challenging as the hippocampus is a small and complex structure. Even manual segmentation, still considered as a gold-standard method, is an error-prone process due to inconsistant guidelines and the need for high-definition MRIs.

To date, there exists (semi-)automated methods for the segmentation of the hippocampal subfields (e.g. @yushkevichAutomatedVolumetryRegional2015, @iglesiasComputationalAtlasHippocampal2015, @romeroHIPSNewHippocampus2017), but they are either slow (e.g.: up to a day to segment a new MRI with `FreeSurfer`) or innacurate, making them unsuited for research or clinical applications. While those methodologies are actually considered as "legacy methods" with respect to the actual literature of semantic segmentation, Deep Learning models have been validated on this complex task [@qiuFeasibilityAutomaticSegmentation2019; @zhuDilatedDenseUNet2019], but they are still reserved to specific populations of researchers / engineers because either models are not public and need to be reimplemented from scratch (e.g. @zhuDilatedDenseUNet2019), or need to be re-trained because pretrained models are not made available, or because they are trained on a specific and uniform dataset, thus causing generalization issues on images acquired with different acquisition parameters (e.g. resolution, contrast, scanner).

This lack of uniformity and ease of use of hippocampal segmentation models leaves a gap in the range of technical options available to researchers and cliniciants. By developing and published our Hippocampal Segmentation Factory (`HSF`), we hope to fill this gap and help the scientific community to better study the hippocampal subfields.

# Segmentation Pipeline

The `HSF` pipeline is constituted of 3 main steps: 1/ a preprocessing step handled by ROILoc to extract the hippocampi from a given MRI, 2/ an augmentation pipeline, and 3/ a segmentation by multiple expert models in order to produce both a segmentation and an uncertainty map (figure \ref{HSF}).

![Overview of the Hippocampal Segmentation Factory segmentation pipeline.\label{HSF}](figures/hsf.png)

## Hippocampal Localization and Preprocessing

In order to limit the computational impact of `HSF`, we use a preprocessing step to extract the hippocampi from the MRI. This step is performed by a pipeline we called `ROILoc` (for ROI localization).

To do so, ROILoc registers the `MNI152 09c Sym` template [@fonovUnbiasedNonlinearAverage2009] to the T1w or T2w input MRI. As we know the coordinates of the hippocampus in the MNI space thanks to the CerebrA atlas [@maneraCerebrARegistrationManual2020], this registration process allows us to infer rough coordinates of the hippocampus in native space. `ROILoc` then crops the MRI into two volumes corresponding to the right and left hippocampi (figure \ref{ROILoc}).

![ROILoc pipeline. The pipeline is a registration based pipeline to locate a specific region of interest (ROI) like the hippocampus, and crop a given MRI around its bounding boxes.\label{ROILoc}](figures/roiloc.png)

To finish the preprocessing, the resulting crops are Z-Normalized, and padded to obtain shapes which are multiple of 8.

## Hippocampal Subfields Segmentation

ARUNet, unstructured pruning, SWA, big databases (mix public, private), T1, T2, multi acquisition center, multi res
TTA Bagging

SENIOR [@haegerImagingAgingBrain2020]
SHATAU [@lagardeDistinctAmyloidTau2021]

## Postprocessing and Uncertainty Estimation

TTA vote, aleatoric uncertainty

# Acknowledgements

We would like to thanks the IDRIS and the Genci who allowed us to access the HPE Jean Zay supercomputer.

# References
