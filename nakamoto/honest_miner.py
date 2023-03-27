"""The module contains an implementation of
honest miner for Nakamoto consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
import random

from base.miner_base import HonestMinerAction as Action
from base.miner_base import HonestMinerStrategyBase


class HonestMinerStrategy(HonestMinerStrategyBase):
    """Honest miner class implementation for Nakamoto consensus."""

    # pylint: disable=too-many-arguments
    def mine_new_block(
        self,
        mining_round: int,
        public_blockchain: "Blockchain",
        ongoing_fork: bool,
        match_competitors: set,
        gamma: float,
    ) -> bool:
        """Mine a new block as an honest miner for the Nakamoto consensus.

        Args:
            mining_round (int): The current mining round.
            public_blockchain ('Blockchain'): The public blockchain.
            ongoing_fork (bool): Indicates if there is an ongoing fork.
            match_competitors (set): A set of competing selfish miners.
            gamma (float): The gamma value for the simulation.

        Returns:
            bool: Whether the fork is ongoing after the block is mined.
        """
        self.log.info(
            f"Honest miner: {self.miner_id} is leader of round: {mining_round}"
        )
        if ongoing_fork:
            ongoing_fork = False
            if gamma == 0.5:
                if random.random() <= 0.5:
                    self.log.info("Previous blocks won selfish miner")

                    wining_selfish_miner = random.choice(match_competitors)
                    public_blockchain.override_chain(wining_selfish_miner)
                    wining_selfish_miner.clear_private_chain()
                    match_competitors.remove(wining_selfish_miner)

        # public_blockchain.add_block(
        #     f"Block {mining_round} data", f"Honest miner {self.miner_id}", self.miner_id
        # )
        self.action = Action.PUBLISH
        return ongoing_fork
