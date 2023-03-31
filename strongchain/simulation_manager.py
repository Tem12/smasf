"""Module contains Mediator class which can run
whole simulation of selfish mining for Strongchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""

from base.simulation_manager_base import SimulationManagerBase


class SimulationManager(SimulationManagerBase):
    """Mediator class for Strongchain consensus for running whole simulation."""

    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Strongchain")
        print(type(self.config))
        print(self.config)

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Strongchain parse config method")
        return simulation_config
