"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 17.3.2023
"""
import random

from base.blockchain import Blockchain
from base.mediator_base import ActionObjectStore, MediatorBase
from base.miner_base import HonestMinerAction as HA
from base.miner_base import MinerType
from base.miner_base import SelfishMinerAction as SA
from base.sim_config_base import SimulationConfigBase as SimulationConfig
from nakamoto.honest_miner import HonestMinerStrategy
from nakamoto.my_graphs import plot_block_counts
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
        self.miners = [self.honest_miner] + self.selfish_miners
        self.miners_info = [self.honest_miner.mining_power] + [
            sm.mining_power for sm in self.selfish_miners
        ]
        self.public_blockchain = Blockchain(owner="public blockchain")
        self.action_store = ActionObjectStore()
        self.ongoing_fork = False

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Nakamoto parse config method")

        sim_config = self.general_config_validations(simulation_config)
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=sim_config["miners"]["honest"]["mining_power"],
            selfish_miners=[
                sm["mining_power"] for sm in sim_config["miners"]["selfish"]
            ],
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
        )

    def resolve_matches(self):
        self.log.info("resolve_matches")
        match_objects = self.action_store.get_objects(SA.MATCH)

        if self.ongoing_fork:
            self.ongoing_fork = True

            # random choice of winner
            winner = random.choice(match_objects + [self.honest_miner])
            if winner.miner_type == MinerType.HONEST:
                # nothing to do. Not necessary to override the last block
                pass
            else:
                # winner is one of attackers, so override last block on public blockchain
                self.public_blockchain.override_chain(winner)
                winner.clear_private_chain()

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
                # miners, which could possibly winn the next round
                self.ongoing_fork = True

        else:
            # there is no onging fork and multiple attackers with match
            self.ongoing_fork = True

    def resolve_overrides(self):
        self.log.info("resolve_overrides")

        match_attackers = self.action_store.get_objects(SA.OVERRIDE)
        if len(match_attackers) == 1:
            # just one attacker in override
            match_obj = match_attackers[0]
        else:
            # multiple attacker
            match_obj = random.choice(match_attackers)

        # override
        self.public_blockchain.override_chain(match_obj)
        match_obj.clear_private_chain()

        if self.ongoing_fork:
            # override automatically solves all ongoing fork
            self.ongoing_fork = False

    def add_honest_block(self, round_id, honest_miner, is_weak_block):
        """Add honest block to public blockchain"""
        self.public_blockchain.add_block(
            data=f"Block {round_id} data",
            miner=f"Honest miner {honest_miner.miner_id}",
            miner_id=honest_miner.miner_id,
            is_weak=is_weak_block,
        )

    def one_round(self, leader, round_id, is_weak_block=False):
        """One round of simulation, where is one new block mined."""
        res = leader.mine_new_block(
            mining_round=round_id,
            public_blockchain=self.public_blockchain,
            ongoing_fork=self.ongoing_fork,
            match_competitors=self.action_store.get_objects(SA.MATCH),
            gamma=self.config.gamma,
        )
        # action = leader.get_and_reset_action()
        action = leader.get_action()

        if leader.miner_type == MinerType.HONEST:
            # honest miner actions
            # --------------------
            if action == HA.PUBLISH:
                # honest miner is leader and want to publish his new block to the public chain
                self.add_honest_block(
                    round_id=round_id, honest_miner=leader, is_weak_block=is_weak_block
                )
                # only honest miner updates state of ongoing fork
                self.ongoing_fork = res

            else:
                raise Exception("Fatal error no fork")
        else:
            # selfish miner actions
            # ---------------------
            if action == SA.OVERRIDE:
                # override public blockchain by attacker's private blockchain
                self.ongoing_fork = False
                self.log.info(
                    f"Override by attacker {leader.blockchain.fork_block_id},"
                    f" {leader.miner_id} in fork"
                )
                self.public_blockchain.override_chain(leader)
                leader.clear_private_chain()

            elif action == SA.WAIT:
                # wait ends round if there is no ongoing fork
                if not self.ongoing_fork:
                    # END ROUND - no ongoing fork and selfish
                    # round leader is leading in more than 1 blocks
                    return

            elif action not in [SA.MATCH, SA.ADOPT]:
                raise Exception("Fatal error ongoing fork")

        while True:
            # override loop
            self.action_store.clear()

            for selfish_miner in self.selfish_miners:
                action = selfish_miner.decide_next_action(
                    self.public_blockchain, leader
                )
                self.action_store.add_object(action, selfish_miner)
            all_actions = self.action_store.get_actions()

            # replacement for `do-while` which is not in python
            condition = SA.OVERRIDE in all_actions
            if not condition:
                break

            self.resolve_overrides()

        if SA.MATCH in all_actions:
            self.resolve_matches()

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""

        for blocks_mined in range(self.config.simulation_mining_rounds):
            # competitors with match actions
            leader = self.choose_leader(self.miners, self.miners_info)
            self.one_round(leader, blocks_mined)

    def run(self):
        self.log.info("Mediator in Nakamoto")

        self.run_simulation()

        block_counts = {
            "Honest miner 42": 0,
            "Selfish miner 43": 0,
            "Selfish miner 44": 0,
            # "Selfish miner 45": 0,
            # "Selfish miner 46": 0,
            # "Selfish miner 47": 0,
            # "Selfish miner 48": 0,
            # "Selfish miner 49": 0,
        }
        self.log.info(block_counts)

        self.log.info(block_counts)
        for block in self.public_blockchain.chain:
            self.log.info(block)
            block_counts[block.miner] += 1

        self.log.info(block_counts)
        self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
