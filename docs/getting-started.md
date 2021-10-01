# Getting Started

The main purpose of this page is to show you how to quickly start
segmenting new MRIs using HSF.

## Installation

This is a quick getting-started guide. For in-depth details, please check
the [page dedicated to installation details](user-guide/installation.md).

### Setting up a new environment

We encourage you to use the [`conda`](https://conda.io/) environment manager
to use HSF.

To create a new environment, run the following commant:

`conda create -n hsf python=3.9`

Then, activate the new environment:

`source activate hsf`

### Basic installation

Once the environment is set up, you can install HSF using the following command:

`pip install hsf`

!!! warning "Hardware acceleration"
    By doing so, HSF will certainly be limited to your CPU.
    If you want to use a different hardware acceleration, please refer to the
    [page dedicated to installation details](user-guide/installation.md).

You can now check the installation and default parameters of HSF using

`hsf -h`

## Say hello to your new segmentation!

Now, let's say you want to segment a database of MRIs, comprising CoroT2 images
of anisotropic resolution 0.3x1.0x0.3.

We do not impose any specific constraints on the database structure, but
please take in consideration that file names should be unambiguous and easily recognizable
through a glob.

Here is an example of a database structure:

```
Database
│   README.md
│   CHANGELOG.txt    
│
└───sub-00C
│   │   sub-00C_tse.nii.gz
|   |   sub-00C_t1w.nii.gz
│   
└───sub-01C
    │   sub-01C_tse.nii.gz
    |   sub-01C_t1w.nii.gz
```

To segment the whole database, you can just run the following command:

`hsf files.path="~/Database" files.pattern="**/*tse.nii.gz" roiloc.margin=[16,4,16]`

And that's it! :smile:

`files.path` and `files.pattern` are the only mandatory parameters. They are used to
determine the list of files to segment.

The parameter `roiloc.margin` is not mandatory, but one of the most important parameters
of HSF. It defines the size of the margin around each hippocampi.

A too small margin will likely result in incorrect crops of the hippocampi, thus leading
to a truncated segmentation. It will also decrease the accuracy of the segmentation as
it is removing context in the image. A large margin however, is likely to increase the
accuracy of the segmentation, but it will greatly increase the computational requirements.

Keep the box centered around the hippocampus, but not too close to it.

Here is a good example:

![Sample hippocampus](docs/resources/sample_hippocampus.png)

For more details, please check the [dedicated page](user-guide/usage.md).
