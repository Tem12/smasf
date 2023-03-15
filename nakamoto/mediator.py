"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""

from base.mediator_base import MediatorBase


class Mediator(MediatorBase):
    """Mediator class for Nakamoto consensus for running whole simulation."""

    def validate_blockchain_config(self):
        self.log.info("validating simulation config")
        print(type(self.config))
        print(self.config)

    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Nakamoto")
        self.validate_blockchain_config()

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Nakamoto parse config method")
        return simulation_config
