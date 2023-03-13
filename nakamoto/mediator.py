"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 13.3.2023
"""
from base.logs import create_logger


def run(simulation_config: dict):
    """Run function."""
    log = create_logger("nakamoto")
    log.info("Mediator in Nakamoto")
    print(type(simulation_config))
    print(simulation_config)
