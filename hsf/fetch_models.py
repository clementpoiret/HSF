import hashlib
from pathlib import Path
from re import L

import wget
from icecream import ic
from omegaconf import DictConfig


def get_md5(fname: str) -> str:
    """ Get md5sum of a file

    Args:
        fname (str): Path to file

    Returns:
        str: md5sum of file
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def fetch(dir: str, filename: str, url: str, md5: str) -> None:
    """ Fetch a model from a url

    Args:
        dir (str): Directory to save model
        filename (str): Filename of model
        url (str): Url to download model from
        md5 (str): md5sum of model
    """
    p = Path(dir).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    outfile = p / filename

    if outfile.exists():
        if get_md5(str(outfile)) == md5:
            model = f"{filename} already exists and is up to date"
            ic(model)
            return
        else:
            model = f"{filename} already exists but is not up to date"
            ic(model)
            outfile.unlink()

    log = "Fetching {}".format(url)
    ic(log)
    wget.download(url, out=str(outfile))
    print("\n")

    if not md5 == get_md5(str(outfile)):
        ic("MD5 checksum failed")
        outfile.unlink()
        raise Exception("MD5 checksum failed")


def fetch_models(dir: str, models: DictConfig) -> None:
    """ Fetch all models

    Args:
        dir (str): Directory to save models
        models (DictConfig): Models to fetch
    """
    for model in models:
        fetch(dir, filename=str(model), **models[model])


# def test():
#     dir = "~/.hsf/models"
