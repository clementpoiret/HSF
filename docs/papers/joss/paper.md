---
title: 'HSF for a Fast, Robust, and Automated Segmentation of Hippocampal Subfields in MRI'
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

# Statement of Need

- Hippocampus
  - Pathologies
  - Development
- Need accurate segmentation
  - ASHS / FreeSurfer
    - Slow (ref), innacurate (ref)
  - DL models
    - No pretrained model
    - Seems OK but no working OOB pipeline
- Need accurate segmentation -> HSF providing end-to-end pipeline, native space, fast, robust, automated


# Segmentation Pipeline

## Hippocampal Localization and Preprocessing

ROILoc, ZNorm, Shape

## Hippocampal Subfields Segmentation

ARUNet, unstructured pruning, SWA, big databases (mix public, private), T1, T2, multi acquisition center, multi res
TTA Bagging


## Postprocessing and Uncertainty Estimation

TTA vote, aleatoric uncertainty


# Acknowledgements

IDRIS Genci


# References
