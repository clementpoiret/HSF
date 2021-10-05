# Configuration

HSF uses [`Hydra`](https://hydra.cc) to manage its configuration.

> Hydra is an open-source Python framework that simplifies the development of research and other complex applications. The key feature is the ability to dynamically create a hierarchical configuration by composition and override it through config files and the command line. The name Hydra comes from its ability to run multiple similar jobs - much like a Hydra with multiple heads.


## How to use Hydra?

HSF is configured using the following config groups:

```
conf
│   config.yaml   
│
└───augmentation
│   │   default.yaml
│   
└───files
│   │   default.yaml
│
└───hardware
│   │   default.yaml
│
└───roiloc
│   │   default_corot2.yaml
│   │   default_t2iso.yaml
│
└───segmentation
    │   single_fast.yaml
    │   single_accurate.yaml
    │   bagging_fast.yaml
    │   bagging_accurate.yaml
```

Groups can be selected with `group=option`. For example: `hsf segmentation=bagging_fast`

Each individual option can be overriden, e.g. `hsf roiloc.margin=[16,8,16]`

You can also add specific configs absent from the default yaml files (e.g. `hsf +augmentation.elastic.image_interpolation=sitkBSpline`)


## Configuration details

Every `*.yaml` file defines a set of parameters influencing the segmentation, as detailed below.


### Inputs & Outputs

I/O are managed through the `files.*` arguments. Default parameters are defined in [`conf/files/default.yaml`](https://github.com/clementpoiret/HSF/blob/master/hsf/conf/files/default.yaml).

- `files.path` and `files.pattern` are mandatory arguments and respectively define where to search for MRIs, and how to find them through a `glob()` pattern.
- `files.mask_pattern` defines how to find brain extraction masks for registration purposes (see [ROILoc documentation](user-guide/roiloc.md)).
- `files.output_dir` defines where to store temporary files in a relative subject directory.

The following example will recursively search all `*T2w.nii.gz` files in the `~Datasets/MRI/` folder, for search a `*T2w_bet_mask.nii.gz` located next to each T2w images:

```
hsf files.path="~/Datasets/MRI/" files.pattern="**/*T2w.nii.gz" files.mask_pattern="*T2w_bet_mask.nii.gz
```


### Preprocessing pipeline

The preprocessing pipeline is kept as minimal as possible.

```mermaid
sequenceDiagram
  "MNI Template"->>"MRI Native Space": Registration
  "MNI Template"---"Hippocampi Bounding Boxes"
  "Hippocampi Bounding Boxes"->>"MRI Native Space": Registration
```

<!-- Alice->>John: Hello John, how are you?
loop Healthcheck
    John->>John: Fight against hypochondria
end
Note right of John: Rational thoughts!
John--Alice: Great!
John->>Bob: How about you?
Bob--John: Jolly good! -->



### Segmentation Models

### Test-time Augmentation

### Hardware Acceleration
