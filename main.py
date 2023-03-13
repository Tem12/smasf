"""Main module of whole program.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""
import importlib

from base.logs import create_logger
from sm_utils import load_simulations_config, parse_args


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
