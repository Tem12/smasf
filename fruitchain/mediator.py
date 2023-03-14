"""Module contains Mediator class which can run
whole simulation of selfish mining for Fruitchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""

from base.mediator_base import MediatorBase


class Mediator(MediatorBase):
    """Mediator class for Fruitchain consensus for running whole simulation."""

    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Fruitchain")
        print(type(self.config))
        print(self.config)

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Fruitchain parse config method")
        return simulation_config
