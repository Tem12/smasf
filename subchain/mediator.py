"""Module contains Mediator class which can run
whole simulation of selfish mining for Subchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""

import json

from base.blockchain import Blockchain
from nakamoto.mediator import Mediator as NakamotoMediator
from nakamoto.my_graphs import plot_block_counts
from subchain.honest_miner import HonestMinerStrategy
from subchain.selfish_miner import SelfishMinerStrategy
from subchain.sim_config import SimulationConfig


class Mediator(NakamotoMediator):
    """Mediator class for Subchain consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(
            simulation_config, blockchain
        )  # create everything necessary from Nakamoto

        self.honest_miner = HonestMinerStrategy(mining_power=self.config.honest_miner)
        self.selfish_miners = [
            SelfishMinerStrategy(mining_power=sm_power)
            for sm_power in self.config.selfish_miners
        ]
        self.miners = [self.honest_miner] + self.selfish_miners
        self.miners_info = [self.honest_miner.mining_power] + [
            sm.mining_power for sm in self.selfish_miners
        ]

        self.public_blockchain_strong = Blockchain(owner="public blockchain strong")

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Subchain parse config method")

        sim_config = self.general_config_validations(
            simulation_config, ["weak_to_strong_block_ratio"]
        )
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=sim_config["miners"]["honest"]["mining_power"],
            selfish_miners=[
                sm["mining_power"] for sm in sim_config["miners"]["selfish"]
            ],
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
            weak_to_strong_block_ratio=sim_config["weak_to_strong_block_ratio"],
        )

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""
        print("TODO")

    def run(self):
        self.log.info("Mediator in Subchain")

        self.run_simulation()
        # exit()

        block_counts = {
            "Honest miner 44": 0,
            "Selfish miner 45": 0,
            # "Selfish miner 44": 0,
            # "Selfish miner 45": 0,
            # "Selfish miner 46": 0,
            # "Selfish miner 47": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
        }
        self.log.info(block_counts)

        self.log.info(block_counts)

        print(json.dumps(self.public_blockchain_strong.to_dict()))
        for block in self.public_blockchain_strong.chain:
            block_counts[block.miner] += 1

        self.log.info(block_counts)
        self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
