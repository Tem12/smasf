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
                res = self.mining_power * 0.5 / 100
                self.log.info(res)

                if random.random() <= res:
                    self.log.info("Previous block won selfish miner")
                    one_sm = list(match_competitors)[0]
                    public_blockchain.chain[-1] = one_sm.blockchain.chain[-1]

                    one_sm.blockchain.chain = []
                    one_sm.blockchain.fork_block_id = None
        public_blockchain.add_block(
            f"Block {mining_round} data", f"Honest miner {self.miner_id}", self.miner_id
        )
        self.action = Action.PUBLISH
        return ongoing_fork
