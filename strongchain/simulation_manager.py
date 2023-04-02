"""Module contains Mediator class which can run
whole simulation of selfish mining for Strongchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
# import json
import random

from base.miner_base import MinerType
from nakamoto.simulation_manager import SimulationManager as NakamotoSimulationManager
from strongchain.blockchain import Blockchain
from strongchain.honest_miner import HonestMinerStrategy
from strongchain.selfish_miner import SelfishMinerStrategy
from strongchain.sim_config import SimulationConfig


class SimulationManager(NakamotoSimulationManager):
    """Mediator class for Strongchain consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(
            simulation_config, blockchain
        )  # create everything necessary from Nakamoto

        # Instantiate everything necessary for Strongchain
        self.honest_miner = HonestMinerStrategy(mining_power=self.config.honest_miner)
        self.selfish_miners = [
            SelfishMinerStrategy(
                mining_power=sm_power, ratio=self.config.weak_to_strong_header_ratio
            )
            for sm_power in self.config.selfish_miners
        ]
        self.miners = [self.honest_miner] + self.selfish_miners
        self.miners_info = [self.honest_miner.mining_power] + [
            sm.mining_power for sm in self.selfish_miners
        ]

        self.public_blockchain = Blockchain(
            owner="public blockchain",
            weak_to_strong_header_ratio=self.config.weak_to_strong_header_ratio,
        )

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Strongchain parse config method")

        sim_config = self.general_config_validations(
            simulation_config, ["weak_to_strong_header_ratio"]
        )
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=sim_config["miners"]["honest"]["mining_power"],
            selfish_miners=[
                sm["mining_power"] for sm in sim_config["miners"]["selfish"]
            ],
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
            weak_to_strong_header_ratio=sim_config["weak_to_strong_header_ratio"],
        )

    def resolve_matches_clear(self, winner):
        print("Resolve matches clear strongchain")

    def resolve_overrides(self) -> None:
        print("Resolve overrides strongchain")

    def resolve_matches(self) -> None:
        print("Resolve matches strongchain")

    def resolve_overrides_clear(self, match_obj):
        print("Resolve matches clear strongchain")

    def resolve_overrides(self) -> None:
        print("Resolve overrides strongchain")

    def selfish_override(self, leader: SelfishMinerStrategy) -> None:
        """Override public blockchain with attacker's private blockchain.

        Args:
            leader (SelfishMinerStrategy): The selfish miner with the longest chain.
        """
        print("Selfish override after mine new block by him in strongchain")

    def add_honest_block(self, round_id, honest_miner, is_weak_block):
        # add new honest block
        self.public_blockchain.add_block(
            data=f"Block {round_id} data",
            miner=f"Honest miner {honest_miner.miner_id}",
            miner_id=honest_miner.miner_id,
            is_weak=is_weak_block,
        )

        # add weak headers to currently mined last block
        self.public_blockchain.chain[-1].setup_weak_headers(
            self.honest_miner.weak_headers
        )
        self.honest_miner.clear_private_weak_chain()

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""
        total_headers = self.config.weak_to_strong_header_ratio + 1
        weak_header_probability = (
            self.config.weak_to_strong_header_ratio / total_headers
        )
        weak_headers = 0
        strong_headers = 0

        for blocks_mined in range(self.config.simulation_mining_rounds):
            leader = self.choose_leader(self.miners, self.miners_info)

            random_number = random.random()
            if random_number <= weak_header_probability:
                print(
                    f"Weak header generated in round {blocks_mined} by {leader.miner_type}"
                )
                miner_str = (
                    "Honest" if leader.miner_type == MinerType.HONEST else "Selfish"
                )
                leader.add_weak_header(
                    data=f"Weak header {blocks_mined} data",
                    miner=f"{miner_str} miner {leader.miner_id}",
                    miner_id=leader.miner_id,
                )
                weak_headers += 1
                print(leader.weak_headers)
                # print(json.dumps([x.to_dict() for x in leader.weak_headers]))

            else:
                print(
                    f"Strong header generated in round {blocks_mined} by {leader.miner_type}"
                )
                self.one_round(leader, blocks_mined, is_weak_block=False)
                strong_headers += 1

        print(f"number of weak blocks: {weak_headers}")
        print(
            f"Their probability: {(weak_headers / (weak_headers + strong_headers)) * 100}%"
        )
        print(f"number of strong blocks: {strong_headers}")
        print(
            f"Their probability: {(strong_headers / (weak_headers + strong_headers) * 100)}%"
        )

    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Strongchain")
        print(type(self.config))
        print(self.config)

        self.run_simulation()
