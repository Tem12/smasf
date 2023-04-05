"""The module contains an implementation of
selfish miner for Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
import random

from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for Nakamoto consensus."""

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ):
        """Update the private blockchain (subchain == weak blocks) of the selfish miner.

        Args:
            public_blockchain ('Blockchain'): The public blockchain.
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

    def select_subchain(self, ongoing_fork, competitors, public_subchain):
        """Select winning Subchain."""
        # is there ongoing competition
        if ongoing_fork:
            # check if his Subchain is among competing chains
            if self.blockchain in competitors:
                # it is
                winning_subchain = self.blockchain
            else:
                # it is not
                winning_subchain = random.choice(competitors + [public_subchain])

        else:
            winning_subchain = public_subchain

        return winning_subchain
