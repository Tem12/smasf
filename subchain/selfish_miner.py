"""The module contains an implementation of
selfish miner for Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy
from subchain.blockchain import Blockchain


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for Subchain consensus."""

    def __init__(self, mining_power: int):
        super().__init__(mining_power)
        self.blockchain = Blockchain(owner=self.miner_id)
        self.blockchain_weak = Blockchain(owner=self.miner_id)

    def clear_private_weak_chain(self):
        """Clear private chain of weak blocks."""
        self.blockchain_weak.chain = []

    def clear_private_strong_chain(self):
        """Clear private chain of strong blocks."""
        self.blockchain.chain = []
        self.blockchain.fork_block_id = None

    def clear_private_chain(self):
        """Clear private chains of weak and also strong blocks."""
        self.clear_private_strong_chain()
        self.clear_private_weak_chain()

    def lead_length(self, public_blockchain):
        """Method for computing leading of selfish miner in comparison to honest miner."""
        fork_block_id = self.blockchain.fork_block_id
        pub_size = public_blockchain.size_from_index(fork_block_id)
        return self.blockchain.size() - pub_size

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ):
        """Update the private strong blockchain of the selfish miner.

        Args:
            public_blockchain ('Blockchain'): The public blockchain.
            mining_round (int): The current mining round.
        """
        # at the beginning add blockchain of weak blocks and clear it
        self.blockchain.chain.extend(self.blockchain_weak.chain)
        self.clear_private_weak_chain()

        # after that do the same as in Nakamoto
        if self.blockchain.size() == 0:
            self.blockchain.initialize(public_blockchain.last_strong_block_id)
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
        else:
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
