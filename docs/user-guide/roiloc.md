# ROILoc

![ROILoc Preview](https://raw.githubusercontent.com/clementpoiret/ROILoc/main/example.png)

## Overview

ROILoc is a registration-based ROI locator, based on the MNI152 09c Sym template, and the CerebrA Atlas.
It'll center and crop T1 or T2 MRIs around a given ROI. Results are saved in "LPI-" (or "RAS+") format.

HSF internally call ROILoc to locate hippocampi in T1w and T2w MRIs. ROILoc is a key part of HSF because it
allow to segment only a small subpart of a given image instead of the whole MRI. It is crucial to use ROILoc
with the correct set of parameters, because if the hippocampus is not located correctly, the segmentation
will obviously fail.

ROILoc is provided as a standalone toolbox, not as a part of HSF. We decided to keep it as a separate project,
because it is generic enough to be used in other projects, where there are regions of interest (ROIs) to locate
in T1w or T2w MRIs.

ROILoc sources are located at [https://github.com/clementpoiret/ROILoc](https://github.com/clementpoiret/ROILoc).


## Configuration for HSF

The default behaviors of ROILoc are defined in the files `conf/roiloc/*.yml`. As an example, here is the default
configuration:

```yaml
contrast: "t2"
roi: "hippocampus"
bet: False
transform_type: "AffineFast"
margin: [16, 4, 16]
rightoffset: [0, 0, 0]
leftoffset: [0, 0, 0]
```

- `contrast` can accept both `t1` or `t2` as values, and will determine which MNI template to use.
- `bet` will determine which MNI template to use: if `True`, it'll use a brain-extracted MNI template.
- `transform_type` can accept any registration type supported by the
[`ANTs` package](https://antspyx.readthedocs.io/en/latest/registration.html). By default, we use `AffineFast`,
which will work most of the time. Difficult cases where most of the time solved by using `ElasticSyN` or `SyN`.
- `margin` is a key parameter. It'll define the space to keep around the ROI. Bigger margins means less potential
errors, but will increase the computation time. If you think the box is big enough to include the whole hippocampus,
but see that it is too much off-centered, please use the `offset` parameters.
- `{side}offset` will translate the bounding boxes by a given amount of voxels. This is useful if the ROI is off-centered,
and will avoid computational overhead due to a too big bounding box.

??? info "Supported transform type"

    - `Translation`: Translation transformation.
    - `Rigid`: Rigid transformation: Only rotation and translation.
    - `Similarity`: Similarity transformation: scaling, rotation and translation.
    - `QuickRigid`: Rigid transformation: Only rotation and translation. May be useful for quick visualization fixes.
    - `DenseRigid`: Rigid transformation: Only rotation and translation. Employs dense sampling during metric estimation.
    - `BOLDRigid`: Rigid transformation: Parameters typical for BOLD to BOLD intrasubject registration.
    - `Affine`: Affine transformation: Rigid + scaling.
    - `AffineFast`: Fast version of Affine.
    - `BOLDAffine`: Affine transformation: Parameters typical for BOLD to BOLD intrasubject registration.
    - `TRSAA`: translation, rigid, similarity, affine (twice). please set regIterations if using this option. this would be used in cases where you want a really high quality affine mapping (perhaps with mask).
    - `ElasticSyN`: Symmetric normalization: Affine + deformable transformation, with mutual information as optimization metric and elastic regularization.
    - `SyN`: Symmetric normalization: Affine + deformable transformation, with mutual information as optimization metric.
    - `SyNRA`: Symmetric normalization: Rigid + Affine + deformable transformation, with mutual information as optimization metric.
    - `SyNOnly`: Symmetric normalization: no initial transformation, with mutual information as optimization metric. Assumes images are aligned by an inital transformation. Can be useful if you want to run an unmasked affine followed by masked deformable registration.
    - `SyNCC`: SyN, but with cross-correlation as the metric.
    - `SyNabp`: SyN optimized for abpBrainExtraction.
    - `SyNBold`: SyN, but optimized for registrations between BOLD and T1 images.
    - `SyNBoldAff`: SyN, but optimized for registrations between BOLD and T1 images, with additional affine step.
    - `SyNAggro`: SyN, but with more aggressive registration (fine-scale matching and more deformation). Takes more time than SyN.
    - `TVMSQ`: time-varying diffeomorphism with mean square metric
    - `TVMSQC`: time-varying diffeomorphism with mean square metric for very large deformation


### Usage as Standalone Application

#### CLI

#### Python API
