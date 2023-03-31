"""Main module of whole program.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
import importlib

from base.logs import create_logger
from sm_utils import load_simulations_config, parse_args


def run_simulations(blockchain: str):
    """Run selfish mining simulations.
    Run selfish mining simulations according to yaml config for selected consensus protocol.

    :param blockchain: blockchain name for simulation
    """
    mediator_module = importlib.import_module(blockchain + "." + "simulation_manager")
    simulations_config = load_simulations_config(blockchain + "/" + "config.yaml")
    for simulation_config in simulations_config:
        sim_manager = mediator_module.SimulationManager(
            simulation_config=simulation_config, blockchain=blockchain
        )
        sim_manager.run()


def main():
    """Main function of whole program."""
    args = parse_args()
    run_simulations(args.blockchain)
    log = create_logger("main")
    log.info("logging")
    print(log)


if __name__ == "__main__":
    main()
