import hydra
# from hydra import compose, initialize
from omegaconf import DictConfig

from .fetch_models import fetch_models
from .welcome import welcome

# initialize(config_path="hsf/conf")
# cfg = compose(config_name="config")


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    fetch_models(cfg.segmentation.models_path, cfg.segmentation.models)


def start():
    welcome()
    main()
