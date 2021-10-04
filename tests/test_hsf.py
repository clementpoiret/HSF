import shutil
import tempfile

import ants
import hsf.fetch_models
import hsf.roiloc_wrapper
from hsf import __version__

tmpdir = tempfile.mkdtemp()


def test_version():
    assert __version__ == '0.1.2'


# Models getters
def test_fetching():
    url = "https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1"
    xxh3 = "d0de65baa81d9382"

    hsf.fetch_models.fetch(tmpdir, "model.onnx", url, xxh3)

    assert xxh3 == hsf.fetch_models.get_hash(tmpdir + "/model.onnx")


def test_roiloc():
    mris = hsf.roiloc_wrapper.load_from_config("tests/mri", "*.nii.gz")
    assert mris

    mri, mask = hsf.roiloc_wrapper.get_mri(mris[0])
    assert isinstance(mri, ants.ANTsImage)

    _, right, left = hsf.roiloc_wrapper.get_hippocampi(mri, {
        "contrast": "t2",
        "margin": [16, 8, 16],
        "roi": "hippocampus"
    }, mask)

    assert isinstance(right, ants.ANTsImage)
    assert isinstance(left, ants.ANTsImage)

    # Saving to {tmpdir}/tse_{side}_hippocampus.nii.gz
    hsf.roiloc_wrapper.save_hippocampi(right, left, tmpdir, mris[0])


shutil.rmtree(tmpdir)
