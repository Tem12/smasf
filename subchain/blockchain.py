"""Module for class Nakamoto consensus blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
from dataclasses import dataclass
from typing import Optional

from base.blockchain import Blockchain as NakamotoBlockchain


@dataclass
class Blockchain(NakamotoBlockchain):
    """Blockchain class for Subchain consensus."""

    last_strong_block_id: Optional[int] = 0

    def override_chain(self, attacker):
        """Override last N blocks with private chain."""

        # Subchain has different indexing to Nakamoto
        self.chain[attacker.blockchain.fork_block_id :] = []
        self.chain.extend(attacker.blockchain.chain)

        self.last_strong_block_id = len(self.chain)

    def size_from_index(self, index):
        """Get length of strong blocks in the blockchain from specified index.

        Args:
            index (int): The index where to start counting of strong blocks
        Returns:
            int: Length of the blockchain.
        """
        size = 0
        for block in self.chain[index:]:
            # count on just strong blocks
            if not block.is_weak:
                size += 1

        return size

    def size(self):
        """Get length of strong blocks in the blockchain.

        Returns:
            int: Length of the blockchain.
        """
        size = 0
        for block in self.chain:
            # count on just strong blocks
            if not block.is_weak:
                size += 1

        return size

    def length(self):
        """Get length of private chain.

        Returns:
            int: Length of the private chain.
        """
        return self.size() + self.fork_block_id
