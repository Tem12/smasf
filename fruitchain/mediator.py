"""Module contains Mediator class which can run
whole simulation of selfish mining for Fruitchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""
from base.logs import create_logger


def run():
    """Run function."""
    log = create_logger("fruitchain")
    log.info("Mediator in Fruitchain")
