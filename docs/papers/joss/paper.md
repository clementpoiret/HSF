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
    affiliation: 1
  - name: Edouard Duchesnay
    affiliation: 1
  - name: Frédéric Lemaître
    orcid: 0000-0003-4424-0981
    affiliation: "3, 4"
  - name: Marion Noulhiane^[corresponding author]
    orcid: 0000-0003-2832-0332
    affiliation: "1, 2"
affiliations:
 - name: NeuroSpin, CEA - Université Paris-Saclay, France
   index: 1
 - name: Inserm U1141 - Université de Paris, France
   index: 2
 - name: CETAPS EA n°3832, Université de Rouen, France
   index: 3
 - name: CRIOBE, UAR 3278, CNRS-EPHE-UPVD, Mooréa, Polynésie Française
   index: 4
date: 17 January 2022
bibliography: paper.bib


---

# Summary

The hippocampus is organized by distinct hippocampal subfields which are differently involved in learning and memory processes and widely implicated in neurological pathologies at different ages of life, such as neonatal hypoxia, temporal lobe epilepsy, or Alzheimer’s disease. Studying the anatomo-functional properties of the hippocampus and its subfields is a mandatory path to understand such conditions and requires reliable and robust segmentation of MRI data. Moreover, the growing size of publicly available datasets calls for faster and more efficient segmentation algorithms. As the current methodologies are shown to be either imprecise, slow or inconvenient, we developed a novel tool called the Hippocampal Segmentation Factory (`HSF`) to automatically segment the hippocampal subfields in T1w or T2w MRIs.

`HSF` is designed to be a fully customizable end-to-end pipeline, handling tasks from the preprocessing of raw anatomical images, to the segmentation of the hippocampal subfields through specialized and highly efficient Deep Learning models comprised in a "Model Hub" on any hardware acceleration platform such as CUDA, TensorRT or OpenVINO. `HSF` also supports the DeepSparse compute engine to benefit from the AVX512(VNNI) vector instruction set.

Our rolling-release Model Hub aims at facilitating the transition from lab-trained models to the end-user. While our built-in models are regularly retrained with more manually labeled MRIs, other independent researchers can codelessly test and distribute their ONNX models to the end-user through a simple CLI argument.

# Statement of Need

The hippocampus is organized by distinct hippocampal subfields, namely Cornus Ammonis (CA1-3), Dentate Gyrus, and Subiculum which are differently involved in learning and memory processes and widely implicated in neurological pathologies at different ages of life, such as neonatal hypoxia, temporal lobe epilepsy, or Alzheimer’s disease [@todaRoleAdultHippocampal2019].

Obtaining a precise and accurate delineation of the hippocampal subfields in order to study both healthy and pathological conditions is a methodological challenge in neuroimagery, because these are small and complex structures [@duvernoyHumanHippocampus2013]. Even the very time-consuming manual segmentation, still considered a gold-standard method, is an error-prone process due to inconsistent guidelines and the need for high-definition MRIs.

To date, there exist (semi-)automated methods for the segmentation of the hippocampal subfields (e.g. @yushkevichAutomatedVolumetryRegional2015, @iglesiasComputationalAtlasHippocampal2015, @romeroHIPSNewHippocampus2017), but those are either slow (e.g.: 8~12 hours to segment a new MRI with `FreeSurfer`) or producing noisy and approximative segmentations, making them unsuited for research or clinical applications. While those methodologies are considered as "legacy methods" with respect to the current literature of semantic segmentation, Deep Learning models have been validated on this complex task [@qiuFeasibilityAutomaticSegmentation2019; @zhuDilatedDenseUNet2019], but are still reserved to specific populations of researchers/engineers because implementations are either not public (e.g. @zhuDilatedDenseUNet2019), pre-trained models are not made available, or because they are trained on specific and uniform datasets, thus causing generalization issues on images acquired with different parameters like resolution or contrast.

This lack of uniformity and ease of use of hippocampal segmentation models leaves a gap in the range of technical options available to researchers and clinicians. By releasing `HSF`, we aim to fill this gap and contribute with the scientific community's further study of the hippocampal subfields.

# Segmentation Pipeline

The `HSF` pipeline is constituted of 3 main steps: 1/ a preprocessing step handled by ROILoc to extract the hippocampi from a given MRI, 2/ an augmentation pipeline, and 3/ a segmentation by multiple expert models in order to produce both the segmentation and an uncertainty map (figure \ref{HSF}).

![Overview of the Hippocampal Segmentation Factory segmentation pipeline.\label{HSF}](figures/hsf.png)

## 1. Hippocampal Localization and Preprocessing

In order to limit the computational impact of `HSF`, we used a preprocessing step to extract the hippocampi from the MRI. This step is performed by a pipeline called `ROILoc` (for ROI localization).

To do so, ROILoc registers the `MNI152 09c Sym` template [@fonovUnbiasedNonlinearAverage2009] to the T1w or T2w input MRI. Knowing the coordinates of the hippocampi in the MNI space thanks to the CerebrA atlas [@maneraCerebrARegistrationManual2020], this registration process allows infering rough coordinates of the hippocampus in native space. `ROILoc` then crops the MRI into two volumes corresponding to the right and left hippocampi (figure \ref{ROILoc}).

![ROILoc pipeline. The pipeline is a registration based pipeline to locate a specific region of interest (ROI) like the hippocampus, and crop a given MRI around its bounding boxes.\label{ROILoc}](figures/roiloc.png)

To finish the preprocessing, the resulting crops are Z-Normalized, and padded to obtain shapes which are multiple of 8 to satisfy hardware acceleration constraints.

## 2. Hippocampal Subfields Segmentation

In addition to a feed-forward inference mode, `HSF` supports bootstrap aggregation and test-time augmentation strategies (figure \ref{HSF}), offering robust segmentations of which an example is depicted in figure \ref{sample}. Prior to the segmentation, cropped hippocampi are going through a customizable augmentation pipeline comprising random lateral flips, affine transformations, and elastic deformations.

`HSF` proposes a "Model Hub" offering multiple pre-trained models. Our built-in models are based on a Residual UNet architecture with a self-attention mechanism similar to the one introduced in by @oktayAttentionUNetLearning2018. In order to provide highly generalizable segmentation models, we gathered and uniformized 4 private and 8 public datasets of manually segmented subfields in T1w and T2w MRIs coming from different acquisition centers, at different resolutions and different magnetic fields:

* 3 Teslas (@winterburnNovelVivoAtlas2013, @kulaga-yoskovitzMulticontrastSubmillimetricTesla2015; @yushkevichAutomatedVolumetryRegional2015; @hindyLinkingPatternCompletion2016; @bouyeureHippocampalSubfieldVolumes2021),
* 4 Teslas [@yushkevichNearlyAutomaticSegmentation2010],
* and 7 Teslas (HiPlay7[^1]; @wisseAutomatedHippocampalSubfield2016; @berronProtocolManualSegmentation2017; @haegerImagingAgingBrain2020; @shawOptimisingMRICharacterisation2020; @lagardeDistinctAmyloidTau2021).

[^1]: ANR-16-NEUC-0001-01; Manual Segmentation on 23 controls and 4 Temporal Lobe Epilepsies; 1mm T1w and 0.125\*0.125\*1.2mm T2w MRIs.

Contrary to other automated segmentation tools constituting the state-of-the-art, `HSF` learned to segment from more than 700 manually annotated hippocampi of individuals from 4 to 84 years old, either healthy, with temporal lobe epilepsy, mild cognitive impairment, or Alzheimer's disease.

![Example of hippocampal subfields segmentation from HSF's segmentation models on a test observation.\label{sample}](figures/sample.png){width=800px}

To conclude, our "Model Hub" is proposed with a rolling release policy, which means that we will continuously update our models with new datasets, either collected internally or provided by independent researchers, and new state-of-the-art training techniques (e.g. sparsification and `int8` quantization). Moreover, anyone can contribute to the Model Hub by exporting their ONNX models and submitting a corresponding configuration file to the `HSF` repository. Newly proposed models will then be directly available to the end-user through CLI.

## 3. Postprocessing and Uncertainty Estimation

As the default inference mode uses bootstrap aggregation and test-time augmentation, passing a single hippocampus through the pipeline produces multiple probabilistic segmentations, which are combined with a plurality voting strategy to produce a final segmentation. Having multiple probabilistic segmentations allows us to estimate the statistical uncertainty of the segmentation (figure \ref{uncertainty}) which can help to analyze the segmentation quality *a posteriori*.

Given a set $Y$ of $i$ predictions, in HSF, the voxel-wise Aleatoric Uncertainty [@wangAleatoricUncertaintyEstimation2019] $H(Y^i|X)$ is defined as:

$$
H(Y^i|X) \approx - \sum^M_{m=1}{\hat{p}^i_m \ln \hat{p}^i_m}
$$

where $\hat{p}^i_m$ is the frequency of the $m$th unique value in $Y^i$.

![Example voxel-wise aleatoric uncertainty. Intensity of red voxels represents the the uncertainty given probabilistic segmentations outputted by HSF on a test observation.\label{uncertainty}](figures/uncertainty.png){width=800px}

# Acknowledgements

We thank the IDRIS and the Genci who allowed us to access the HPE Jean Zay supercomputer. We also thank M. Bottlaender for giving us access to T1w and T2w MRI from the SENIOR cohort, and M. Faillot for helping us manually segment the hippocampus.

The research leading to these results has received funding from the Fondation de France, and the joint NSF/NIH/ANR program "Collaborative Research in Computational Neuroscience" (project HIPLAY7, grant number ANR-16-NEUC-0001-01).

Clément Poiret obtained doctoral funding from the University of Paris.

# References
