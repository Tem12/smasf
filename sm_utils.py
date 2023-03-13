"""Module with helper functions.

Author: Jan Jakub Kubik (xkubik32)
Date: 13.3.2023
"""
import argparse

import yaml


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
