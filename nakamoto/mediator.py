"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""

from base.mediator_base import MediatorBase
from nakamoto.honest_miner import HonestMinerStrategy
from nakamoto.selfish_miner import SelfishMinerStrategy


class Mediator(MediatorBase):
    """Mediator class for Nakamoto consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(simulation_config, blockchain)
        self.honest_miner = HonestMinerStrategy(mining_power=60)
        self.selfish_miner = SelfishMinerStrategy(mining_power=40)

    def run(self):
        """Entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Nakamoto")
        self.validate_blockchain_config()
        self.honest_miner.run()
        self.selfish_miner.run()

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Nakamoto parse config method")
        return simulation_config

    def validate_blockchain_config(self):
        """General validation of parsed simulation config."""
        self.log.info("validating simulation config")
        print(type(self.config))
        print(self.config)
