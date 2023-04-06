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

            # select winner according to his chain power
            winner = self.select_miner_with_strongest_chain(
                selfish_miners=match_objects, use_hm=True
            )

            if winner.miner_type == MinerType.HONEST:
                # clear competing sm chains
                for attacker in match_objects:
                    attacker.clear_private_chain()
                    self.action_store.remove_object(SA.MATCH, attacker)
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
            sm_pow = match_obj.blockchain.chains_pow()
            hm_pow = self.public_blockchain.chains_pow_from_index(
                match_obj.blockchain.fork_block_id
            )

            if sm_pow > hm_pow:
                # SM has stronher chain -> override public chain and clear everything necessary
                self.log.info("Selfish is stronger than honest miner")
                self.public_blockchain.override_chain(match_obj)
                self.resolve_matches_clear(match_obj)

            elif sm_pow < hm_pow:
                # HM has stronger chain -> nothing to do just clearing competing sm chains
                self.log.info("Honest miner is stronger than selfish miner")
                match_obj.clear_private_chain()
                self.action_store.remove_object(SA.MATCH, match_obj)

            # the chains have totally the same strength - so behave as for Nakamoto
            else:
                self.log.info("Selfish miner has the same chain power as honest miner")
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

            # TODO: Also check power and do things according to it

            self.ongoing_fork = True

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
        strong = {44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0}
        weak = {44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0}

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
                weak[leader.miner_id] += 1
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
                strong[leader.miner_id] += 1
                strong_headers += 1

        print(f"number of weak blocks: {weak_headers}")
        print(
            f"Their probability: {(weak_headers / (weak_headers + strong_headers)) * 100}%"
        )
        print(f"number of strong blocks: {strong_headers}")
        print(
            f"Their probability: {(strong_headers / (weak_headers + strong_headers) * 100)}%"
        )
        print(strong)
        print(weak)

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
            # "Selfish miner 47": 0,
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

            for _ in block.weak_headers:
                block_counts[block.miner] += 1

        # import json
        # print(json.dumps(self.public_blockchain.to_dict()))
        # self.log.info(block_counts)
        # self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
