"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 17.3.2023
"""
import random

from base.blockchain import Blockchain
from base.miner_base import HonestMinerAction as HA
from base.miner_base import MinerType
from base.miner_base import SelfishMinerAction as SA
from base.sim_config_base import SimulationConfigBase as SimulationConfig
from base.simulation_manager_base import ActionObjectStore, SimulationManagerBase
from nakamoto.honest_miner import HonestMinerStrategy
from nakamoto.selfish_miner import SelfishMinerStrategy
from public_blockchain_functions import (
    calculate_percentage,
    plot_block_counts,
    print_attackers_success,
    print_honest_miner_info,
)


class SimulationManager(SimulationManagerBase):
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

    def parse_config(self, simulation_config: dict) -> SimulationConfig:
        """Parsing dict from yaml config.

        Args:
            simulation_config (dict): A dictionary containing the simulation configuration.

        Returns:
            SimulationConfig: An instance of SimulationConfig with the parsed configuration values.
        """
        self.log.info("Nakamoto parse config method")

        sim_config = self.general_config_validations(simulation_config, ["gamma"])
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=sim_config["miners"]["honest"]["mining_power"],
            selfish_miners=[
                sm["mining_power"] for sm in sim_config["miners"]["selfish"]
            ],
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
        )

    # pylint: disable=no-self-use
    def resolve_matches_clear(self, winner: SelfishMinerStrategy) -> None:
        """Clear all necessary blockchains in method `resolve_matches`.

        Args:
            winner (SelfishMinerStrategy): The winning selfish miner.
        """
        winner.clear_private_chain()

    def resolve_matches(self) -> None:
        """Resolve matches between honest miner and selfish miners."""
        self.log.info("resolve_matches")
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
                self.action_store.remove_object(SA.MATCH, match_obj)

            else:
                # gamma is 0 or 0.5. If 0 give attacker 1 round chance to mine new block
                # If 0.5 give chance attacker to mine new block and also group of honest
                # miners, which could possibly win the next round
                self.ongoing_fork = True

        else:
            # there is no ongoing fork and multiple attackers with match
            self.ongoing_fork = True

    # pylint: disable=no-self-use
    def resolve_overrides_clear(self, match_obj: SelfishMinerStrategy) -> None:
        """Clear all necessary blockchains in method `resolve_overrides`.

        Args:
            match_obj (SelfishMinerStrategy): The selfish miner with the longest chain.
        """
        match_obj.clear_private_chain()

    def resolve_overrides_select_from_multiple_attackers(self, attackers):
        """Customizable method for selecting of override attacker winner if there
        is more than one attacker with override."""
        return random.choice(attackers)

    def resolve_overrides(self) -> None:
        """Resolve any overrides that need to occur after mining."""
        self.log.info("resolve_overrides")

        match_attackers = self.action_store.get_objects(SA.OVERRIDE)
        if len(match_attackers) == 1:
            # just one attacker in override
            match_obj = match_attackers[0]
        else:
            # multiple attacker
            match_obj = self.resolve_overrides_select_from_multiple_attackers(
                match_attackers
            )

        # override
        self.public_blockchain.override_chain(match_obj)
        self.resolve_overrides_clear(match_obj)
        # It is necessary to increase last block id on honest chain after override
        # which happens only if HM is catching SM and has 1 block shorter chain
        self.public_blockchain.last_block_id += 1

        # action_store is reset after every resolve_overrides -->
        # no need to clean it. Here is cleaning just of private chains
        # of SM competitors
        for attacker in match_attackers:
            attacker.clear_private_chain()

        if self.ongoing_fork:
            # override automatically solves all ongoing fork
            self.ongoing_fork = False

    def add_honest_block(
        self, round_id: int, honest_miner: HonestMinerStrategy, is_weak_block: bool
    ) -> None:
        """Add honest block to public blockchain.

        Args:
            round_id (int): The current round ID.
            honest_miner (HonestMinerStrategy): The honest miner who mined the block.
            is_weak_block (bool): Indicates if the block is a weak block or not.
        """
        self.public_blockchain.add_block(
            data=f"Block {round_id} data",
            miner=f"Honest miner {honest_miner.miner_id}",
            miner_id=honest_miner.miner_id,
            is_weak=is_weak_block,
        )

        # clearing of private chains of all attackers which are currently in MATCH
        match_objects = self.action_store.get_objects(SA.MATCH)
        for attacker in match_objects:
            attacker.clear_private_chain()
            self.action_store.remove_object(SA.MATCH, attacker)

    def selfish_override(self, leader: SelfishMinerStrategy) -> None:
        """Override public blockchain with attacker's private blockchain.

        Args:
            leader (SelfishMinerStrategy): The selfish miner with the longest chain.
        """
        self.ongoing_fork = False
        self.log.info(
            f"Override by attacker {leader.blockchain.fork_block_id},"
            f" {leader.miner_id} in fork"
        )
        self.public_blockchain.override_chain(leader)
        # It is necessary to increase last block id on honest chain after override
        # which happens only if SM wins the block and he is in ongoing fork
        self.public_blockchain.last_block_id += 1
        # cleaning of competing SM is performed via ADOPT
        leader.clear_private_chain()

        # clearing of private chains of all attackers which are currently in MATCH
        match_objects = self.action_store.get_objects(SA.MATCH)
        for attacker in match_objects:
            attacker.clear_private_chain()
            self.action_store.remove_object(SA.MATCH, attacker)

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

        # honest and selfish miner updates state of ongoing fork
        self.ongoing_fork = res

        if leader.miner_type == MinerType.HONEST:
            # honest miner actions
            # --------------------
            if action == HA.PUBLISH:
                # honest miner is leader and want to publish his new block to the public chain
                self.add_honest_block(
                    round_id=round_id, honest_miner=leader, is_weak_block=is_weak_block
                )

            else:
                raise Exception("Fatal error no fork")
        else:
            # selfish miner actions
            # ---------------------
            if action == SA.OVERRIDE:
                # override public blockchain by attacker's private blockchain
                self.selfish_override(leader)

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
        self.winns = {
            miner.miner_id: 0 for miner in self.selfish_miners + [self.honest_miner]
        }

        for blocks_mined in range(self.config.simulation_mining_rounds):
            # competitors with match actions
            leader = self.choose_leader(self.miners, self.miners_info)
            self.winns[leader.miner_id] += 1
            self.one_round(leader, blocks_mined)

        self.log.info(self.config.simulation_mining_rounds)
        self.log.info(self.winns)

        # !!! handle extreme case !!!, when any of selfish miner
        # has the longest chain after the end of simulation.
        # This happens only if any of SM has higher mining power than HM
        # Select the selfish miner with the longest chain if any exists
        # or if the length is the same, then random select
        match_attackers = self.action_store.get_objects(SA.WAIT)
        if len(match_attackers) > 0:
            miner_and_len = list()
            for miner in match_attackers:
                chain_len = miner.blockchain.size()
                miner_and_len.append((miner, chain_len))

            # Find the maximum value
            max_value = max(obj[1] for obj in miner_and_len)
            # Filter the attackers with the highest value
            matching_miners = [obj for obj in miner_and_len if obj[1] == max_value]
            # Select a random object among the ones with the highest value
            winner = random.choice(matching_miners)[0]
            self.public_blockchain.override_chain(winner)

    def run(self):
        """Run the simulation, process the results and plot the block counts."""
        self.log.info("Mediator in Nakamoto")

        self.run_simulation()

        block_counts = {f"Honest miner {self.honest_miner.miner_id}": 0}
        for miner in self.selfish_miners:
            block_counts.update({f"Selfish miner {miner.miner_id}": 0})

        for block in self.public_blockchain.chain:
            block_counts[block.miner] += 1

        attacker_ids = [
            miner.miner_id for miner in self.selfish_miners
        ]  # List of attacker IDs
        honest_miner_id = self.honest_miner.miner_id  # Honest miner ID

        total_blocks = sum(block_counts.values())
        percentages = calculate_percentage(block_counts, total_blocks)
        print_attackers_success(block_counts, percentages, self.winns, attacker_ids)
        print_honest_miner_info(block_counts, percentages, self.winns, honest_miner_id)

        # print(block_counts)
        # import json
        # visualize whole blockchain
        # print(json.dumps(self.public_blockchain.to_dict()))
        # self.log.info(block_counts)
        # self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
