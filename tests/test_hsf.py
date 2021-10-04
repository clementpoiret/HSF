from hsf import __version__, fetch_models


def test_version():
    assert __version__ == '0.1.2'


# Models getters
def test_fetching():
    fetch_models.test(
        "https://zenodo.org/record/5524594/files/arunet_bag0.onnx?download=1",
        "d0de65baa81d9382")
