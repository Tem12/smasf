"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Tomáš Hladký (xhladk15)
Date: 18.9.2023
"""
import random

from base.blockchain import Blockchain
from base.miner_base import HonestMinerAction as HA
from base.miner_base import MinerType
from base.miner_base import SelfishMinerAction as SA
from base.simulation_manager_base import ActionObjectStore
from nakamoto.simulation_manager import SimulationManager as NakamotoSimulationManager
from fruitchain.honest_miner import HonestMinerStrategy
from fruitchain.selfish_miner import SelfishMinerStrategy
from public_blockchain_functions import (
    calculate_percentage,
    plot_block_counts,
    print_attackers_success,
    print_honest_miner_info,
)
from fruitchain.sim_config import SimulationConfig
from fruitchain.fruitchain_types import FruitchainAction
from tqdm import tqdm

import csv


class SimulationManager(NakamotoSimulationManager):
    # pylint: disable=too-many-instance-attributes
    """Mediator class for Nakamoto consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(
            simulation_config, blockchain
        )  # create everything necessary from Nakamoto

        if blockchain.out is None:
            self.out_path = 'fruit_res.csv'
        else:
            self.out_path = blockchain.out

        self.honest_miner = HonestMinerStrategy(
            mining_power=self.config.honest_miner)
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

        self.winns = {
            miner.miner_id: 0 for miner in self.selfish_miners + [self.honest_miner]
        }

    def parse_config(self, simulation_config: dict) -> SimulationConfig:
        """Parse dict from YAML config."""
        self.log.info("Fruitchain parse config method")

        sim_config = self.general_config_validations(
            simulation_config, ["gamma", "fruit_mine_prob",
                                "superblock_prob"]
        )
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=sim_config["miners"]["honest"]["mining_power"],
            selfish_miners=[
                sm["mining_power"] for sm in sim_config["miners"]["selfish"]
            ],
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
            fruit_mine_prob=sim_config["fruit_mine_prob"],
            superblock_prob=sim_config["superblock_prob"],
        )

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""

        blocks_mined = 0
        # for blocks_mined in range(self.config.simulation_mining_rounds):
        with tqdm(total=self.config.simulation_mining_rounds) as pbar:
            while blocks_mined < self.config.simulation_mining_rounds:
                # competitors with match actions
                action = self.choose_mining_action()
                # print(action)

                leader = None
                if self.ongoing_fork and action == FruitchainAction.MINE_BLOCK:
                    # leader selection based on fruit quantity
                    # highest_fruit_count = -1

                    # get leading competitors
                    # highest_blockchain_size = -1
                    # competitors = []
                    # for miner in self.miners:
                    #     if miner.miner_type == MinerType.SELFISH and miner.blockchain.size() >= highest_blockchain_size:
                    #             competitors.append(miner)
                    #             highest_blockchain_size = miner.blockchain.size()
                    #     elif miner.miner_type == MinerType.HONEST and self.public_blockchain.size() >= highest_blockchain_size:
                    #         competitors.append(miner)
                    #         highest_blockchain_size = self.public_blockchain.size()

                    # Find the maximum fruit count using the custom key function
                    max_fruit_count = max(self.miners, key=lambda miner: miner.get_fruit_count()).get_fruit_count()

                    # Filter miners with the maximum fruit count
                    max_fruit_miners = [miner for miner in self.miners if miner.get_fruit_count() == max_fruit_count]

                    # Randomly select one miner from the list of miners with the maximum fruit count
                    if self.config.gamma == 0.5:
                        leader = random.choice(max_fruit_miners)
                    elif self.config.gamma == 0.0:
                        contains_honest = False
                        for miner in max_fruit_miners:
                            if miner.miner_type == MinerType.HONEST:
                                contains_honest = True
                                break

                        if contains_honest:
                            honest_miners = [miner for miner in max_fruit_miners if
                                             miner.miner_type == MinerType.HONEST]
                            leader = random.choice(honest_miners)
                        else:
                            leader = random.choice(max_fruit_miners)
                    elif self.config.gamma == 1.0:
                        contains_selfish = False
                        for miner in max_fruit_miners:
                            if miner.miner_type == MinerType.SELFISH:
                                contains_selfish = True
                                break

                        if contains_selfish:
                            selfish_miners = [miner for miner in max_fruit_miners if
                                              miner.miner_type == MinerType.SELFISH]
                            leader = random.choice(selfish_miners)
                        else:
                            leader = random.choice(max_fruit_miners)

                    # else:
                    #     for miner in competitors:
                    #         fruit_count = miner.get_fruit_count()
                    #         if fruit_count >= highest_fruit_count:
                    #             if self.config.gamma == 1.0:
                    #                 if leader is None or miner.miner_type == MinerType.SELFISH:
                    #                     # higher chance for selfish if their fruit content count equals
                    #                     leader = miner
                    #                     exit(1)
                    #             elif self.config.gamma == 0.0:
                    #                 if leader is None or miner.miner_type == MinerType.HONEST:
                    #                     # higher chance for selfish if their fruit content count equals
                    #                     leader = miner                                    
                else:
                    leader = self.choose_leader(self.miners, self.miners_info)

                self.one_round(leader, blocks_mined, action)

                if action == FruitchainAction.MINE_BLOCK:
                    self.winns[leader.miner_id] += 1
                    
                    curr_blocks_mined = len(self.get_max_chain().chain)
                    blocks_mined = curr_blocks_mined
                    pbar.n = blocks_mined
                    pbar.refresh()

        # self.log.info(self.config.simulation_mining_rounds)
        # self.log.info(self.winns)

    def add_honest_block(
            self, round_id: int, honest_miner: HonestMinerStrategy, is_weak_block: bool
    ) -> None:
        """Add honest block to public blockchain.

        Args:
            round_id (int): The current round ID.
            honest_miner (HonestMinerStrategy): The honest miner who mined the block.
            is_weak_block (bool): Indicates if the block is a weak block or not.
        """
        fruits = honest_miner.fruit_to_str()
        self.public_blockchain.add_block(
            data=fruits,
            miner=f"Honest miner {honest_miner.miner_id}",
            miner_id=honest_miner.miner_id,
            is_weak=is_weak_block,
        )

        # clearing of private chains of all attackers which are currently in MATCH
        match_objects = self.action_store.get_objects(SA.MATCH)
        for attacker in match_objects:
            attacker.clear_private_chain()
            self.action_store.remove_object(SA.MATCH, attacker)

    def one_round(self, leader, round_id, mining_action):
        """One round of simulation, where is one new block mined."""
        if mining_action == FruitchainAction.MINE_FRUIT:
            # mine fruit
            leader.mine_new_fruit()

            if leader.miner_type == MinerType.HONEST:
                for miner in self.miners:
                    if miner.miner_id != leader.miner_id:
                        miner.receive_new_fruit(leader.miner_id)

        elif mining_action == FruitchainAction.MINE_BLOCK:
            # mine block/superblock
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
                        round_id=round_id, honest_miner=leader, is_weak_block=False
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

            # If block was mined by honest miner, clear fruit-queues for all miners
            if leader.miner_type == MinerType.HONEST:
                for miner in self.miners:
                    miner.clear_fruit_queue()

    def resolve_matches(self) -> None:
        """Resolve matches between honest miner and selfish miners."""
        # self.log.info("resolve_matches")

        # for miner in self.miners:
            # print(f"Power: {miner.get_fruit_count()}")

        match_objects = self.action_store.get_objects(SA.MATCH)

        if self.ongoing_fork:
            self.ongoing_fork = False

            # random choice of winner
            winner = random.choice(match_objects + [self.honest_miner])

            # winner selection based on fruit quantity
            # highest_fruit_count = -1
            # for miner in match_objects + [self.honest_miner]:
            #     fruit_count = miner.get_fruit_count()
            #     if fruit_count > highest_fruit_count:
            #         winner = miner

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

            if match_obj is not self.honest_miner:
                honest_fruit_count = self.honest_miner.get_fruit_count()
                selfish_fruit_count = match_obj.get_fruit_count()

                if selfish_fruit_count > honest_fruit_count:
                    self.resolve_fruit_match(match_obj, [self.honest_miner])
                elif selfish_fruit_count == honest_fruit_count:
                    if self.config.gamma == 1:
                        self.resolve_fruit_match(match_obj, [])
                    elif self.config.gamma == 0.5:
                        winner = random.choice([match_obj, self.honest_miner])
                        if winner == match_obj:
                            self.resolve_fruit_match(match_obj, [])
                    else:
                    #     # gamma is 0 or 0.5. If 0 give attacker 1 round chance to mine new block
                    #     # If 0.5 give chance attacker to mine new block and also group of honest
                    #     # miners, which could possibly win the next round
                    #     self.ongoing_fork = True
                        self.ongoing_fork = True

        else:
            max_fruit_miners = []
            max_fruit_count = -1
            for miner in match_objects:
                fruit_count = miner.get_fruit_count()
                if fruit_count > max_fruit_count:
                    max_fruit_count = fruit_count
                    max_fruit_miners = []
                    max_fruit_miners.append(miner)
                elif fruit_count == max_fruit_count:
                    max_fruit_miners.append(miner)

            if len(max_fruit_miners) == 1:
                if max_fruit_miners[0] is not self.honest_miner:
                    self.resolve_fruit_match(max_fruit_miners[0], [])
            else:
                isHonest = False
                for miner in max_fruit_miners:
                    if self.honest_miner == miner:
                        isHonest = True
                
                if not isHonest:
                    winner = random.choice(max_fruit_miners)
                    self.resolve_fruit_match(winner, [])
                else:
                    if self.config.gamma == 1:
                        # Remove honest from miners
                        max_fruit_miners_selfish = []
                        for miner in max_fruit_miners:
                            if self.honest_miner is not miner:
                                max_fruit_miners_selfish.append(miner)
                        winner = random.choice(max_fruit_miners_selfish)
                        self.resolve_fruit_match(winner, [])
                    elif self.config.gamma == 0.5:
                        winner = random.choice(max_fruit_miners_selfish)
                        if winner is not self.honest_miner:
                            self.resolve_fruit_match(winner, [])
                    else:
                        self.ongoing_fork = True

    def resolve_fruit_match(self, winner, competitors):
        if winner is not self.honest_miner:
            self.public_blockchain.override_chain(winner)
            winner.clear_private_chain()
            self.action_store.remove_object(SA.MATCH, winner)

        winner.clear_fruit_queue()
        # for competitor in competitors:
            # competitor.clear_fruit_queue()
        for miner in self.miners:
            miner.clear_fruit_queue()

    def choose_mining_action(self) -> FruitchainAction:
        choices_list = [FruitchainAction.MINE_FRUIT, FruitchainAction.MINE_BLOCK]
        weights = (self.config.fruit_mine_prob,
                   self.config.superblock_prob)
        return random.choices(choices_list, weights=weights, k=1)[0]
    
    def get_max_chain(self):
        max_chain = self.public_blockchain
        curr_max = len(self.public_blockchain.chain)

        for miner in self.miners:
            if miner.miner_type == MinerType.SELFISH:
                if len(miner.blockchain.chain) >= curr_max:
                    max_chain = miner.blockchain
                    curr_max = len(miner.blockchain.chain)

        return max_chain

    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        # self.log.info("Mediator in Fruitchain")
        # print(type(self.config))
        # print(self.config)

        self.run_simulation()

        # Flush blockchain
        # curr_max = len(self.public_blockchain.chain)
        # for miner in self.miners:
        #     if miner.miner_type == MinerType.SELFISH:
        #         if len(miner.blockchain.chain) >= curr_max:
        #             self.public_blockchain = miner.blockchain
        #             curr_max = len(miner.blockchain.chain)
        self.public_blockchain = self.get_max_chain()

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

        # Store results
        f = open(self.out_path, 'w')
        writer = csv.writer(f)
        writer.writerow(['miner_id', 'fruits'])
        for block in self.public_blockchain:
            writer.writerow([block.miner_id, block.data])

        print('Final chains:')
        print(f'{honest_miner_id}: {len(self.public_blockchain.chain)}')
        for miner in self.miners:
            if miner.miner_type == MinerType.SELFISH:
                print(f'{miner.miner_id}: {len(miner.blockchain.chain)}')

        # print(f'Forks: {self.ongoing_fork_counter}')

        # print(block_counts)
        # import json
        # visualize whole blockchain
        # print(json.dumps(self.public_blockchain.to_dict()))
        # self.log.info(block_counts)
        # self.log.info(self.selfish_miners[0].blockchain.chain)

        # plot_block_counts(block_counts, self.miners_info)
