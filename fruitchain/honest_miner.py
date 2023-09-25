"""The module contains an implementation of
honest miner for Nakamoto consensus protocol.

Author: Tomáš Hladký (xhladk15)
Date: 18.9.2023
"""
import random
from typing import Set

from base.blockchain import Blockchain
from base.miner_base import HonestMinerAction as Action
from base.miner_base import HonestMinerStrategyBase

from nakamoto.honest_miner import HonestMinerStrategy as NakamotoHonestMinerStrategy


class HonestMinerStrategy(NakamotoHonestMinerStrategy):
    """Honest miner class implementation for Fruitchain consensus."""

    def __init__(self, mining_power: int):
        super().__init__(mining_power)
        self.fruit_queue_count = 0
        self.rewarded_fruit = 0  # Rewarded only when mined fruit included in their mined block

    def mine_new_fruit(self):
        self.fruit_queue_count += 1

    def receive_new_fruit(self):
        self.fruit_queue_count += 1

    def clear_fruit_queue(self):
        self.fruit_queue_count = 0

    def store_fruit_reward(self):
        self.rewarded_fruit += self.fruit_queue_count

    def get_mined_fruit_count(self):
        return self.rewarded_fruit

    def get_fruit_count(self):
        return self.fruit_queue_count
    
        # pylint: disable=too-many-arguments
    def mine_new_block(
        self,
        mining_round: int,
        public_blockchain: Blockchain,
        ongoing_fork: bool,
        match_competitors: Set["HonestMinerStrategyBase"],
        gamma: float,
    ) -> bool:
        """Mine a new block as an honest miner for the Nakamoto consensus.

        Args:
            mining_round (int): The current mining round.
            public_blockchain (Blockchain): The public blockchain.
            ongoing_fork (bool): Indicates if there is an ongoing fork.
            match_competitors (Set[HonestMinerStrategyBase]): A set of competing selfish miners.
            gamma (float): The gamma value for the simulation.

        Returns:
            bool: Whether the fork is ongoing after the block is mined.
        """
        self.log.info(
            f"Honest miner: {self.miner_id} is leader of round: {mining_round}"
        )
        if ongoing_fork:
            print('Honest miner MATCH competitor')
            ongoing_fork = False
            if gamma == 0.5:
                if random.random() <= 0.5:
                    self.log.info("Previous blocks won selfish miner")

                    wining_selfish_miner = random.choice(match_competitors)
                    public_blockchain.override_chain(wining_selfish_miner)
                    # cleaning of competing SM is performed via ADOPT
                    wining_selfish_miner.clear_private_chain()
                    match_competitors.remove(wining_selfish_miner)

        # public_blockchain.add_block(
        #     f"Block {mining_round} data", f"Honest miner {self.miner_id}", self.miner_id
        # )
        self.action = Action.PUBLISH
        return ongoing_fork
