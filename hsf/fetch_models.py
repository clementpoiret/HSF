from pathlib import Path

import wget
import xxhash
from icecream import ic
from omegaconf import DictConfig


def get_hash(fname: str) -> str:
    """Get xxHash3 of a file

    Args:
        fname (str): Path to file

    Returns:
        str: xxHash3 of file
    """
    xxh = xxhash.xxh3_64()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            xxh.update(chunk)
    return xxh.hexdigest()


def fetch(directory: str, filename: str, url: str, xxh3_64: str) -> None:
    """Fetch a model from a url

    Args:
        directory (str): Directory to save model
        filename (str): Filename of model
        url (str): Url to download model from
        xxh3_64 (str): xxh3_64 of model
    """
    p = Path(directory).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    outfile = p / filename

    if outfile.exists():
        if get_hash(str(outfile)) == xxh3_64:
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

    if not xxh3_64 == get_hash(str(outfile)):
        ic("xxh3_64 checksum failed")
        outfile.unlink()
        raise Exception("xxh3_64 checksum failed")


def fetch_models(directory: str, models: DictConfig) -> None:
    """Fetch all models

    Args:
        directory (str): Directory to save models
        models (DictConfig): Models to fetch
    """
    for model in models:
        fetch(directory, filename=str(model), **models[model])
