"""Main module of whole program.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
import importlib
from argparse import Namespace

from base.logs import create_logger
from sm_utils import load_simulations_config, parse_args


def run_simulations(parsed_args: Namespace) -> None:
    """Run selfish mining simulations.
    Run selfish mining simulations according to yaml config for selected consensus protocol.

    :param parsed_args: valid parsed program arguments
    """
    if parsed_args.blockchain == "subchain":
        module_path = parsed_args.blockchain + "." + parsed_args.option
        config_path = parsed_args.blockchain + "/" + parsed_args.option
    else:
        module_path = config_path = parsed_args.blockchain

    mediator_module = importlib.import_module(module_path + "." + "simulation_manager")
    simulations_config = load_simulations_config(config_path + "/" + "config.yaml")
    for simulation_config in simulations_config:
        sim_manager = mediator_module.SimulationManager(
            simulation_config=simulation_config, blockchain=parsed_args
        )
        sim_manager.run()


def main():
    """Main function of whole program."""
    args = parse_args()
    run_simulations(args)
    log = create_logger("main")
    log.info("logging")
    print(log)


if __name__ == "__main__":
    main()
