import hydra
from omegaconf import DictConfig


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    print(cfg)


def start():
    main()
