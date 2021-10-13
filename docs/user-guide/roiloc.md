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

??? info "Supported ROIs"

    - Caudal Anterior Cingulate,
    - Caudal Middle Frontal,
    - Cuneus,
    - Entorhinal,
    - Fusiform,
    - Inferior Parietal,
    - Inferior temporal,
    - Isthmus Cingulate,
    - Lateral Occipital,
    - Lateral Orbitofrontal,
    - Lingual,
    - Medial Orbitofrontal,
    - Middle Temporal,
    - Parahippocampal,
    - Paracentral,
    - Pars Opercularis,
    - Pars Orbitalis,
    - Pars Triangularis,
    - Pericalcarine,
    - Postcentral,
    - Posterior Cingulate,
    - Precentral,
    - Precuneus,
    - Rostral Anterior Cingulate,
    - Rostral Middle Frontal,
    - Superior Frontal,
    - Superior Parietal,
    - Superior Temporal,
    - Supramarginal,
    - Transverse Temporal,
    - Insula,
    - Brainstem,
    - Third Ventricle,
    - Fourth Ventricle,
    - Optic Chiasm,
    - Lateral Ventricle,
    - Inferior Lateral Ventricle,
    - Cerebellum Gray Matter,
    - Cerebellum White Matter,
    - Thalamus,
    - Caudate,
    - Putamen,
    - Pallidum,
    - Hippocampus,
    - Amygdala,
    - Accumbens Area,
    - Ventral Diencephalon,
    - Basal Forebrain,
    - Vermal lobules I-V,
    - Vermal lobules VI-VII,
    - Vermal lobules VIII-X.


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

??? info "Supported transform types"

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

As stated above, ROILoc can be used as a standalone preprocessing tool, either through CLI or via a Python API.


#### CLI

Here is an example of a standalone CLI use equivalent to HSF's default behavior:

```
roiloc -p "~/Datasets/MemoDev/ManualSegmentation/" -i "**/tse.nii.gz" -r "hippocampus" -c "t2" -t "AffineFast" -m 16 4 16
```

usage: roiloc [-h] -p PATH -i INPUTPATTERN [-r ROI [ROI ...]] -c CONTRAST [-b]
[-t TRANSFORM] [-m MARGIN [MARGIN ...]] [--rightoffset RIGHTOFFSET [RIGHTOFFSET ...]] [--leftoffset LEFTOFFSET [LEFTOFFSET ...]] [--mask MASK] [--extracrops EXTRACROPS [EXTRACROPS ...]] [--savesteps]


```
-h, --help            show this help message and exit
-p PATH, --path PATH  <Required> Input images path.
-i INPUTPATTERN, --inputpattern INPUTPATTERN
                      <Required> Pattern to find input images in input path
                      (e.g.: `**/*t1*.nii.gz`).
-r ROI [ROI ...], --roi ROI [ROI ...]
                      ROI included in CerebrA. See
                      `roiloc/MNI/cerebra/CerebrA_LabelDetails.csv` for more
                      details. Default: 'Hippocampus'.
-c CONTRAST, --contrast CONTRAST
                      <Required> Contrast of the input MRI. Can be `t1` or
                      `t2`.
-b, --bet             Flag use the BET version of the MNI152 template.
-t TRANSFORM, --transform TRANSFORM
                      Type of registration. See `https://antspy.readthedocs.
                      io/en/latest/registration.html` for the complete list
                      of options. Default: `AffineFast`
-m MARGIN [MARGIN ...], --margin MARGIN [MARGIN ...]
                      Margin to add around the bounding box in voxels. It
                      has to be a list of 3 integers, to control the margin
                      in the three axis (0: left/right margin, 1: post/ant
                      margin, 2: inf/sup margin). Default: [8,8,8]
--rightoffset RIGHTOFFSET [RIGHTOFFSET ...]
                      Offset to add to the bounding box of the right ROI in
                      voxels. It has to be a list of 3 integers, to control
                      the offset in the three axis (0: from left to right,
                      1: from post to ant, 2: from inf to sup).
                      Default: [0,0,0]
--leftoffset LEFTOFFSET [LEFTOFFSET ...]
                      Offset to add to the bounding box of the left ROI in
                      voxels. It has to be a list of 3 integers, to control
                      the offset in the three axis (0: from left to right,
                      1: from post to ant, 2: from inf to sup).
                      Default: [0,0,0]
--mask MASK           Pattern for brain tissue mask to improve registration
                      (e.g.: `sub_*bet_mask.nii.gz`). If providing a BET
                      mask, please also pass `-b` to use a BET MNI template.
--extracrops EXTRACROPS [EXTRACROPS ...]
                      Pattern for other files to crop (e.g. manual
                      segmentation: '*manual_segmentation_left*.nii.gz').
--savesteps           Flag to save intermediate files (e.g. registered
                      atlas).
```


#### Python API

Even if the CLI interface is the main use case, a Python API is also available since `v0.2.0`.

The API syntax retakes sklearn's API syntax, with a `RoiLocator` class, having `fit`, `transform`, `fit_transform` and `inverse_transform` methods as seen below.

!!! example

    ```python
    import ants
    from roiloc.locator import RoiLocator

    image = ants.image_read("./sub00_t2w.nii.gz",
                            reorient="LPI")

    locator = RoiLocator(contrast="t2", roi="hippocampus", bet=False)

    # Fit the locator and get the transformed MRIs
    right, left = locator.fit_transform(image)
    # Coordinates can be obtained through the `coords` attribute
    print(locator.get_coords())

    # Let 'model' be a segmentation model of the hippocampus
    right_seg = model(right)
    left_seg = model(left)

    # Transform the segmentation back to the original image
    right_seg = locator.inverse_transform(right_seg)
    left_seg = locator.inverse_transform(left_seg)

    # Save the resulting segmentations in the original space
    ants.image_write(right_seg, "./sub00_hippocampus_right.nii.gz")
    ants.image_write(left_seg, "./sub00_hippocampus_left.nii.gz")
    ```
