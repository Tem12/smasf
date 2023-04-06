"""Module contains Mediator class which can run
whole simulation of selfish mining for Strongchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
import random

from base.miner_base import MinerType
from base.miner_base import SelfishMinerAction as SA
from nakamoto.my_graphs import plot_block_counts
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
        winner.clear_private_strong_chain()
        # clear private weak chain of selfish miner
        self.honest_miner.clear_private_weak_chain()
        # clearing of competitors is performed inside resolve_matches

    def resolve_matches(self) -> None:
        """Resolve matches between honest miner and selfish miners."""
        self.log.info("resolve_matches Strongchain")
        match_objects = self.action_store.get_objects(SA.MATCH)

        if self.ongoing_fork:
            self.ongoing_fork = False

            # random choice of winner
            winner = random.choice(match_objects + [self.honest_miner])
            if winner.miner_type == MinerType.HONEST:
                # nothing to do. Not necessary to override the last block
                pass
            else:
                # winner is one of attackers, so override last block on public blockchain
                self.public_blockchain.override_chain(winner)
                self.resolve_matches_clear(winner)
                # clear private chains of competing attackers
                # and also remove them from action store
                for attacker in match_objects:
                    attacker.clear_private_chain()
                    self.action_store.remove_object(SA.MATCH, attacker)

        elif len(match_objects) == 1:
            # just one attacker in match phase
            match_obj = match_objects[0]

            if self.config.gamma == 1:
                # integrate attacker's last block to the public blockchain
                self.log.info("SM wins")
                self.public_blockchain.override_chain(match_obj)
                match_obj.clear_private_chain()

            else:
                # gamma is 0 or 0.5. If 0 give attacker 1 round chance to mine new block
                # If 0.5 give chance attacker to mine new block and also group of honest
                # miners, which could possibly win the next round
                self.ongoing_fork = True

        else:
            # there is no ongoing fork and multiple attackers with match
            self.ongoing_fork = True

    def resolve_overrides_select_from_multiple_attackers(self, attackers):
        attacker_and_pow = []
        for attacker in attackers:
            chain_strength = attacker.blockchain.chains_pow()
            attacker_and_pow.append((attacker, chain_strength))

        # Find the maximum value
        max_value = max(obj[1] for obj in attacker_and_pow)
        # Filter the attackers with the highest value
        matching_attackers = [obj for obj in attacker_and_pow if obj[1] == max_value]
        # Select a random object among the ones with the highest value
        winner = random.choice(matching_attackers)

        return winner[0]

    def resolve_overrides_clear(self, match_obj):
        print("Resolve matches clear strongchain")
        match_obj.clear_private_strong_chain()
        # need to clear weak blockchain of honest miner
        self.honest_miner.clear_private_weak_chain()
        # clearing of competitors is performed inside resolve_overrides

    # def resolve_overrides(self) -> None:
    # Not necessary -
    #     print("Resolve overrides strongchain")

    def selfish_override(self, leader: SelfishMinerStrategy) -> None:
        # override public blockchain by attacker's private blockchain

        print("Selfish override after mine new block by him in strongchain")
        self.ongoing_fork = False
        self.log.info(
            f"Override by attacker {leader.blockchain.fork_block_id},"
            f" {leader.miner_id} in fork"
        )
        self.public_blockchain.override_chain(leader)
        # cleaning of competing SM is performed via ADOPT
        leader.clear_private_strong_chain()
        # cleaning of competing SM is performed via ADOPT
        # clear just honest miner private weak chain
        self.honest_miner.clear_private_weak_chain()

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

    def clear_sm_weak_headers_if_no_fork(self):
        """Clear weak blocks of selfish miners without fork."""
        for selfish_miner in self.selfish_miners:
            if not selfish_miner.blockchain.fork_block_id:
                selfish_miner.clear_private_weak_headers()

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
                # print(leader.weak_headers)
                # print(json.dumps([x.to_dict() for x in leader.weak_headers]))

            else:
                print(
                    f"Strong header generated in round {blocks_mined} by {leader.miner_type}"
                )

                # # this fulfill the condition, that weak header points to the
                # previously mined strong block in main chain
                # if leader.miner_type == MinerType.HONEST:
                #     self.clear_sm_weak_headers_if_no_fork()

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

        block_counts = {
            "Honest miner 44": 0,
            "Selfish miner 45": 0,
            "Selfish miner 46": 0,
            # "Selfish miner 45": 0,
            # "Selfish miner 46": 0,
            # "Selfish miner 47": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
        }
        # self.log.info(block_counts)

        # self.log.info(block_counts)
        for block in self.public_blockchain.chain:
            # self.log.info(block)
            block_counts[block.miner] += 1

        # import json
        # print(json.dumps(self.public_blockchain.to_dict()))
        # self.log.info(block_counts)
        # self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
