"""Main module of whole program.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""
import argparse

import yaml

from base.logs import create_logger
from fruitchain.mediator import run as fruitchain_run
from nakamoto.mediator import run as nakamoto_run
from strongchain.mediator import run as strongchain_run
from subchain.mediator import run as subchain_run


def parse_args():
    """Parse all program arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate selfish mining on different blockchains."
    )
    parser.add_argument(
        "blockchain",
        choices=["nakamoto", "subchain", "strongchain", "fruitchain"],
        type=str.lower,
        help="Select blockchain network where you want to simulate selfish mining",
    )

    return parser.parse_args()


def load_simulations_config(config_path: str) -> dict:
    """Load config from yaml file.

    :param config_path: path to yaml config for loading
    :return: config: loaded config
    """
    with open(config_path, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    return config


def main():
    """Main function of whole program."""
    args = parse_args()
    if args.blockchain == "nakamoto":
        simulations_config = load_simulations_config("nakamoto/config.yaml")
        for simulation_config in simulations_config:
            nakamoto_run(simulation_config)

    elif args.blockchain == "subchain":
        simulations_config = load_simulations_config("subchain/config.yaml")
        for simulation_config in simulations_config:
            subchain_run(simulation_config)

    elif args.blockchain == "strongchain":
        simulations_config = load_simulations_config("strongchain/config.yaml")
        for simulation_config in simulations_config:
            strongchain_run(simulation_config)

    else:
        simulations_config = load_simulations_config("fruitchain/config.yaml")
        for simulation_config in simulations_config:
            fruitchain_run(simulation_config)

    # try how is working nested logging

    log = create_logger("main")
    log.info("logging")
    print(log)


if __name__ == "__main__":
    main()
