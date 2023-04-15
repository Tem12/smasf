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

    def select_miner_with_strongest_chain(self, selfish_miners, use_hm=None):
        """Select miner among all miners according to his chian power."""
        miner_and_pow = []

        if use_hm:
            sm_fork_id = selfish_miners[0].blockchain.fork_block_id
            chain_strength = self.public_blockchain.chains_pow_from_index(sm_fork_id)
            miner_and_pow.append((self.honest_miner, chain_strength))

        for miner in selfish_miners:
            chain_strength = miner.blockchain.chains_pow()
            miner_and_pow.append((miner, chain_strength))

        print(miner_and_pow)

        # Find the maximum value
        max_value = max(obj[1] for obj in miner_and_pow)
        # Filter the attackers with the highest value
        matching_miners = [obj for obj in miner_and_pow if obj[1] == max_value]
        # Select a random object among the ones with the highest value
        winner = random.choice(matching_miners)

        return winner[0]

    def resolve_overrides_select_from_multiple_attackers(self, attackers):
        return self.select_miner_with_strongest_chain(attackers)

    def resolve_overrides_clear(self, match_obj):
        print("Resolve matches clear strongchain")
        match_obj.clear_private_strong_chain()
        # need to clear weak blockchain of honest miner
        self.honest_miner.clear_private_weak_chain()
        # clearing of competitors is performed inside resolve_overrides

    def selfish_override(self, leader: SelfishMinerStrategy) -> None:
        # override public blockchain by attacker's private blockchain

        print("Selfish override after mine new block by him in strongchain")
        self.ongoing_fork = False
        self.log.info(
            f"Override by attacker {leader.blockchain.fork_block_id},"
            f" {leader.miner_id} in fork"
        )
        self.public_blockchain.override_chain(leader)
        self.public_blockchain.last_block_id = self.public_blockchain.size()
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

    def resolve_overrides(self):
        super().resolve_overrides()
        # update actual last block id
        self.public_blockchain.last_block_id = self.public_blockchain.size()

    def clear_sm_weak_headers_if_no_fork(self):
        """Clear weak blocks of selfish miners without fork."""
        for selfish_miner in self.selfish_miners:
            if not selfish_miner.blockchain.fork_block_id:
                selfish_miner.clear_private_weak_headers()

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""
        self.winns = {42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0}

        self.strong = {44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0}
        self.weak = {44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0}

        total_headers = self.config.weak_to_strong_header_ratio + 1
        weak_header_probability = (
            self.config.weak_to_strong_header_ratio / total_headers
        )
        weak_headers = 0
        strong_headers = 0

        for blocks_mined in range(self.config.simulation_mining_rounds):
            leader = self.choose_leader(self.miners, self.miners_info)
            self.winns[leader.miner_id] += 1

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
                self.weak[leader.miner_id] += 1
                weak_headers += 1
                # print(leader.weak_headers)
                # print(json.dumps([x.to_dict() for x in leader.weak_headers]))

                if leader.miner_type == MinerType.HONEST:
                    while True:
                        # override loop
                        self.action_store.clear()

                        for selfish_miner in self.selfish_miners:
                            action = selfish_miner.decide_next_action_weak(
                                self.public_blockchain
                            )
                            self.action_store.add_object(action, selfish_miner)
                        all_actions = self.action_store.get_actions()

                        # replacement for `do-while` which is not in python
                        condition = SA.OVERRIDE in all_actions
                        if not condition:
                            break

                        self.resolve_overrides()

            else:
                print(
                    f"Strong header generated in round {blocks_mined} by {leader.miner_type}"
                )

                # # this fulfills the condition, that weak header points to the
                # previously mined strong block in main chain
                if leader.miner_type == MinerType.HONEST:
                    self.clear_sm_weak_headers_if_no_fork()

                self.one_round(leader, blocks_mined, is_weak_block=False)
                self.strong[leader.miner_id] += 1
                strong_headers += 1

        print(f"number of weak blocks: {weak_headers}")
        print(
            f"Their probability: {(weak_headers / (weak_headers + strong_headers)) * 100}%"
        )
        print(f"number of strong blocks: {strong_headers}")
        print(
            f"Their probability: {(strong_headers / (weak_headers + strong_headers) * 100)}%"
        )
        print(self.strong)
        print(self.weak)

        # !!! handle extreme case !!!, when any of selfish miner
        # has the longest chain after the end of simulation.
        # This happens only if any of SM has higher mining power than HM
        # Select the selfish miner with the longest chain if any exists
        # or if the length is the same, then random select
        match_attackers = self.action_store.get_objects(SA.WAIT)
        if len(match_attackers) > 0:
            winner = self.select_miner_with_strongest_chain(match_attackers)
            self.public_blockchain.override_chain(winner)

    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Strongchain")
        print(type(self.config))
        print(self.config)

        self.run_simulation()

        block_counts = {
            "Honest miner 44": 0,
            "Selfish miner 45": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
            # "Selfish miner 50": 0,
            # "Selfish miner 51": 0,
        }
        block_counts_same = {
            "Honest miner 44 weak": 0,
            "Honest miner 44 strong": 0,
            "Selfish miner 45 weak": 0,
            "Selfish miner 45 strong": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
            # "Selfish miner 50": 0,
            # "Selfish miner 51": 0,
        }

        # self.log.info(block_counts)

        # self.log.info(block_counts)
        for block in self.public_blockchain.chain:
            # self.log.info(block)
            block_counts[block.miner] += 1
            block_counts_same[block.miner + " strong"] += 1

            for _ in block.weak_headers:
                block_counts[block.miner] += 1 / 100
                block_counts_same[block.miner + " weak"] += 1

        all_blocks_count = 0
        for count in block_counts.values():
            all_blocks_count += count
        print(all_blocks_count)

        def float_with_comma(number):
            return str(number).replace(".", ",")

        print("-------------")
        success_1 = round(block_counts["Selfish miner 45"] / all_blocks_count * 100, 3)
        print(float_with_comma(success_1))
        print(self.winns[45])
        print(float_with_comma(block_counts_same["Selfish miner 45 strong"]))
        print(float_with_comma(block_counts_same["Selfish miner 45 weak"]))

        print(float_with_comma(round(100 - success_1, 3)))
        # print(self.winns)
        print(self.winns[44])
        print(float_with_comma(block_counts_same["Honest miner 44 strong"]))
        print(float_with_comma(block_counts_same["Honest miner 44 weak"]))

        # import json
        # print(json.dumps(self.public_blockchain.to_dict()))
        # self.log.info(block_counts)
        # self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
