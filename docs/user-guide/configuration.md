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

### Inputs & Outputs

### Preprocessing pipeline

### Segmentation Models

### Test-time Augmentation

### Hardware Acceleration
