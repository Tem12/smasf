"""This module contains an implementation of the
selfish miner for the Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
import random

from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for the Subchain consensus."""

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ) -> None:
        """Update the private blockchain (subchain == weak blocks) of the selfish miner.

        Args:
            public_blockchain (Blockchain): The public blockchain.
            mining_round (int): The current mining round.
        """
        if self.blockchain.size() == 0:
            self.blockchain.initialize(public_blockchain.last_block_id)
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
                is_weak=True,
            )
        else:
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
                is_weak=True,
            )

    def select_subchain(
        self, ongoing_fork: bool, competitors: list, public_subchain: "Subchain"
    ) -> "Subchain":
        """Select the winning Subchain.

        Args:
            ongoing_fork (bool): Indicates whether there is an ongoing fork.
            competitors (list): A list of competing subchains.
            public_subchain (Subchain): The current public subchain.

        Returns:
            Subchain: The selected winning subchain.
        """
        if ongoing_fork:
            if self.blockchain in competitors:
                winning_subchain = self.blockchain
            else:
                winning_subchain = random.choice(competitors + [public_subchain])
        else:
            winning_subchain = public_subchain

        return winning_subchain
