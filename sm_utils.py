"""Module with helper functions.

Author: Jan Jakub Kubik (xkubik32)
Date: 13.3.2023
"""
from argparse import ArgumentParser

import yaml


def parse_args():
    """Parse all program arguments."""
    parser = ArgumentParser(
        description="Simulate selfish mining on different blockchains."
    )

    subparsers = parser.add_subparsers(dest="blockchain", help="sub-command help")

    # Create the parser for the first choice
    subchain = subparsers.add_parser("subchain", help="Subchain blockchain simulation")
    subchain.add_argument(
        "option",
        choices=["weak", "strong"],
        type=str.lower,
        help="Selfish mining simulation for Subchain on WEAK or STRONG headers",
    )

    # Create the parser for the second choice
    subparsers.add_parser("nakamoto", help="Nakamoto blockchain simulation")

    # Create the parser for the third choice
    subparsers.add_parser("strongchain", help="Strongchain blockchain simulation")

    return parser.parse_args()


def load_simulations_config(config_path: str) -> dict:
    """Load config from yaml file.

    :param config_path: path to yaml config for loading
    :return: config: loaded config
    """
    with open(config_path, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    return config
