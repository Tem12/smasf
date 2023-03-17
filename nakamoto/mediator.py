"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
from base.mediator_base import MediatorBase
from base.sim_config_base import SimulationConfigBase as SimulationConfig
from nakamoto.honest_miner import HonestMinerStrategy
from nakamoto.selfish_miner import SelfishMinerStrategy


class Mediator(MediatorBase):
    """Mediator class for Nakamoto consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(simulation_config, blockchain)
        self.honest_miner = HonestMinerStrategy(mining_power=self.config.honest_miner)
        self.selfish_miners = [
            SelfishMinerStrategy(mining_power=sm_power)
            for sm_power in self.config.selfish_miners
        ]

    def run(self):
        """Entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Nakamoto")

        print(self.honest_miner)
        print(self.honest_miner.__dict__)
        print(self.selfish_miners[0].__dict__)

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Nakamoto parse config method")

        # check main keys
        expected_keys = {"consensus_name", "miners", "gamma"}
        sim_config = list(simulation_config.values())[0]
        self.validate_blockchain_config_keys(sim_config, expected_keys)

        print(sim_config)
        gama = sim_config["gamma"]
        consensus_name = sim_config["consensus_name"]
        miners = sim_config["miners"]
        if len(list(miners["honest"])) != 1:
            raise ValueError("You must setup exactly 1 honest miner")
        if len(list(miners["selfish"])) == 0:
            raise ValueError("You must setup at least 1 selfish miner")

        honest_miner = miners["honest"]["mining_power"]
        selfish_miners = [sm["mining_power"] for sm in miners["selfish"]]
        return SimulationConfig(
            consensus_name=consensus_name,
            honest_miner=honest_miner,
            selfish_miners=selfish_miners,
            gamma=gama,
        )
