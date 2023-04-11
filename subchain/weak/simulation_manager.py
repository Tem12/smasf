"""Module contains Mediator class which can run
whole simulation of selfish mining for Subchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""

import json
import random

from base.blockchain import Blockchain
from base.miner_base import MinerType
from base.miner_base import SelfishMinerAction as SA
from nakamoto.my_graphs import plot_block_counts
from nakamoto.simulation_manager import SimulationManager as NakamotoSimulationManager
from subchain.sim_config import SimulationConfig
from subchain.weak.honest_miner import HonestMinerStrategy
from subchain.weak.selfish_miner import SelfishMinerStrategy


class SimulationManager(NakamotoSimulationManager):
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
        total_blocks = self.config.weak_to_strong_block_ratio + 1
        weak_block_probability = self.config.weak_to_strong_block_ratio / total_blocks
        weak_blocks = 0
        strong_blocks = 0

        for blocks_mined in range(self.config.simulation_mining_rounds):
            leader = self.choose_leader(self.miners, self.miners_info)

            # Check if it's time to generate a weak block
            random_number = random.random()
            if random_number <= weak_block_probability:
                print(f"Weak block generated in round {blocks_mined}")
                weak_blocks += 1

                self.one_round(leader, blocks_mined, is_weak_block=True)

            # Check if it's time to generate a strong block
            else:
                print(f"Strong block generated in round {blocks_mined}")
                strong_blocks += 1

                if leader.miner_type == MinerType.SELFISH:
                    continue

                competitors = self.action_store.get_objects(SA.MATCH)
                competitors_blockchain = [
                    competitor.blockchain for competitor in competitors
                ]
                selected_subchain = leader.select_subchain(
                    self.ongoing_fork, competitors_blockchain, self.public_blockchain
                )

                self.public_blockchain_strong.chain.extend(selected_subchain)
                self.public_blockchain_strong.add_block(
                    data=f"Block {blocks_mined} data",
                    miner=f"{'Honest' if leader.miner_type == MinerType.HONEST else 'Selfish'} "
                    f"miner {leader.miner_id}",
                    miner_id=leader.miner_id,
                    is_weak=False,
                )
                self.action_store.clear()
                self.ongoing_fork = False

                # clear public blockchain of weak blocks
                self.public_blockchain.chain = []
                self.public_blockchain.last_block_id = 0
                self.public_blockchain.fork_block_id = None

                # clear private weak blockchains of attackers
                for selfish_miner in self.selfish_miners:
                    selfish_miner.blockchain.chain = []
                    selfish_miner.blockchain.last_block_id = 0
                    selfish_miner.blockchain.fork_block_id = None

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
