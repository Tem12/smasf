"""Main module of whole program.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""
import argparse
import importlib

import yaml

from base.logs import create_logger


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


def run_simulations(blockchain: str):
    """Run selfish mining simulations.
    Run selfish mining simulations according to yaml config for selected consensus protocol.

    :param blockchain: blockchain name for simulation
    """
    mediator = importlib.import_module(blockchain + "." + "mediator")
    simulations_config = load_simulations_config(blockchain + "/" + "config.yaml")
    for simulation_config in simulations_config:
        mediator.run(simulation_config)


def main():
    """Main function of whole program."""
    args = parse_args()
    run_simulations(args.blockchain)

    # try how is working nested logging

    log = create_logger("main")
    log.info("logging")
    print(log)


if __name__ == "__main__":
    main()
