# Contributing

If you found a way to improve our segmentation quality (e.g. by tweaking TTA), please open
an issue or make a PR on GitHub.

Additionally data is the new gold. If you have incorrect segmentations, feel free to
correct them, and then send them to us. The data will be kept private,
stored in secured infrastructures, and will be used in the next training iteration of HSF.
We would be very grateful.

Please open an issue on GitHub so we can agree on how to transfer the segmentations.

We always seek for new datasets, so if you have a dataset with manual segmentations of
hippocampi, or heared about a new released dataset, please let us know.

As soon as we obtained a relatively good amount of new segmentations (maybe 10 to 20 new
hippocampi), we will retrain our models, and we will release a new version of HSF. You
will then be able to benefit from the improved segmentation by running
`pip install -U hsf` as soon as the new version is released.
