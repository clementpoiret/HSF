# Finetuning

## Overview

Since v1.2.0, the complete training code is available at [hsf_train](https://github.com/clementpoiret/hsf_train).
The `hsf_train` repository also contains easy to use scripts to train OR **finetune your own models**.

## Purpose & Use Cases

The goal of HSF is to provide foundational models that can be used as a starting point for further development and customization in Hippocampal Subfields segmentation.

We are aware that the provided models may not be perfect for every use case, and that's why we provide the training code and the possibility to finetune the models.

If you want to use HSF on MRIs that are very different from the ones used for training, or if you want to segment the hippocampal subfields in a specific way, you are at the right place.

## Configuration

The `hsf_train` repository contains a `conf` directory, analogous to the `conf` directory in the `hsf` repository. This directory contains the configuration files for the training and finetuning scripts.

Here is the default configuration file for the finetuning script:

```yaml
mode: decoder  # encoder or decoder, defines which part of the model to finetune (see below)
depth: -1  # -1 for all layers, 0 for the first layer, 1 for the second layer, etc.
unfreeze_frequency: 4  # how often to unfreeze a layer
out_channels: 6  # number of output channels (subfields) in case you want to segment a different number of subfields
```

## Getting Started

### Installation

You will need to clone the repository, install PyTorch, and install the required packages:

```bash
git clone https://github.com/clementpoiret/hsf_train.git
cd hsf_train
conda create -n hsf_train python=3.10
conda activate hsf_train
conda install pytorch torchvision torchaudio cudatoolkit=12.1 -c pytorch -c nvidia
pip install -r requirements.txt
```

### Custom Dataset

Whoever wants to finetune the models will need to provide their own dataset. The heavier the changes are between the training dataset and the custom dataset, the more data you will need.

You will need to adapt the example `custom_dataset.yaml` file to suit your needs, such as:

```yaml
main_path: "/mnt/data/hsf/"
output_path: "/mnt/hsf/models/"
batch_size: 1
num_workers: 16
pin_memory: True
train_ratio: .9
replace: False
k_sample: Null  # i.e. k = train_ratio * num_samples
train_val_test_idx: Null
train_on_all: False

datasets:
  clark:
    path: "hippocampus_clark_3T"
    ca_type: "1/23"
    patterns:
      right_t2:
        mri: "**/t2w_Hippocampus_right_ElasticSyN_crop.nii.gz"
        label: "t2w_Hippocampus_right_ElasticSyN_seg_crop.nii.gz"
      left_t2:
        mri: "**/t2w_Hippocampus_left_ElasticSyN_crop.nii.gz"
        label: "t2w_Hippocampus_left_ElasticSyN_seg_crop.nii.gz"
      averaged_right_t2:
        mri: "**/averaged_t2w_Hippocampus_right_ElasticSyN_crop.nii.gz"
        label: "averaged_t2w_Hippocampus_right_ElasticSyN_seg_crop.nii.gz"
      averaged_left_t2:
        mri: "**/averaged_t2w_Hippocampus_left_ElasticSyN_crop.nii.gz"
        label: "averaged_t2w_Hippocampus_left_ElasticSyN_seg_crop.nii.gz"
    labels:
      1: 1
      2: 2
      3: 3
      4: 4
      5: 5
      6: 6
      7: 7
    labels_names:
      1: "DG"
      2: "CA2/3"
      3: "CA1"
      4: "PRESUB"
      5: "UNCUS"
      6: "PARASUB"
      7: "KYST"
```

??? info "Comment on the `out_channels` parameter"
    You can see in the example above that we have 7 subfields. However, the `out_channels` parameter also includes the background (class 0), so you should set it to 8.
    
### Finetuning

Then, you can run the finetuning script:

```bash
python finetune.py \
  datasets=custom_dataset \
  finetuning.out_channels=8 \
  models.lr=1e-3 \
  models.use_forgiving_loss=False
```

## Training Tips

Numerous factors can influence the quality of the finetuned model. Here are some tips to help you get the best results:

- **Number of manual segmentations**: The more manual segmentations you have, the better. The more subtle the differences between our original dataset and your custom dataset, the less data you will need,
- **Learning rate**: We recommend starting with a learning rate of 1e-3,
- **Depth**: We recommend starting with a depth of -1, which means that all layers will be finetuned. If your changes are small, you can finetune less layers, or even only the final layer (depth = 0),
- **Number of epochs**: We recommend starting with 16 epochs if the depth is -1, otherwise a rule of thumb might be `epochs = (depth + 1) * unfreeze_frequency`,
- **Mode**: It depends on the type of changes you want to make. If you change the image modality (e.g. another contrast than T1w or T2w, a magnetic field intensity larger than 7T, etc.), you might want to finetune the encoder. If you want to segment a different number of subfields or use another segmentation guideline, you might want to finetune the decoder.
- **Unfreeze frequency**: We recommend starting with an unfreeze frequency of 4. Check the learning curves, you should reach a plateau before unfreezing the next layer,
