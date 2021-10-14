# What's Next for HSF?

Here are some ideas for what is yet to be included in the next major version of HSF:

- [x] Complete the documentation
- [ ] Improve the models
    * [x] `Single` shouldn't be part of the bag because it hasn't seen all the data 
    * [ ] Increase the amount of training data
    * [x] Enhance data augmentation
- [ ] Optimize the models
    * [ ] Float16-int8 / Quantization (*delayed*)
    * [ ] Quantization Aware Training (*delayed*)
    * [ ] Pruning (WIP)
- [ ] Provide a way to QC segmentations
    * [x] Voxel-wise aleatoric uncertainty,
    * [ ] Structure-wise uncertainty.

Please note that this list 1/ is not exhaustive, 2/ is not a guarantee that the mentioned features will be included in the next major version.
