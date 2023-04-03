"""Module for class Strongchain consensus blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from base.blockchain import Block as NakamotoBlock
from base.blockchain import Blockchain as NakamotoBlockchain


@dataclass
class WeakHeader(NakamotoBlock):
    """WeakHeader class for Strongchain consensus blocks."""

    # remove unwanted attribute from parent class
    is_weak: None = None

    def __repr__(self) -> str:
        return (
            f"Weak header(data={self.data}, miner={self.miner}, "
            f"miner_id={self.miner_id})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the block.
        """
        return {
            "data": self.data,
            "miner": self.miner,
            "miner_id": self.miner_id,
        }


@dataclass
class Block(NakamotoBlock):
    """Block data class for Strongchain consensus."""

    weak_headers: List = field(default_factory=list)

    def setup_weak_headers(self, weak_headers):
        """Setup weak headers."""
        self.weak_headers.extend(weak_headers)

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the block.
        """
        return {
            "data": self.data,
            "miner": self.miner,
            "miner_id": self.miner_id,
            "weak_headers": [
                weak_header.to_dict() for weak_header in self.weak_headers
            ],
        }


@dataclass
class Blockchain(NakamotoBlockchain):
    """Blockchain class for Strongchain consensus."""

    # must have some default value which is always overridden
    weak_to_strong_header_ratio: int = 42

    def add_block(
        self, data: str, miner: str, miner_id: int, is_weak: bool = False
    ) -> None:
        new_block = Block(data, miner, miner_id, is_weak)
        self.chain.append(new_block)
        self.last_block_id += 1

    def chains_pow(self):
        """Compute whole blockchain power."""
        return self.chains_pow_from_index(index=0)

    def chains_pow_from_index(self, index):
        """Compute blockchain power from index."""
        chains_pow = 0
        for block in self.chain[index:]:
            # strong block pow = 1
            chains_pow += 1
            for _ in block.weak_headers:
                # weak header pow = 1 / weak_to_strong_header_ratio
                chains_pow = chains_pow + (1 / self.weak_to_strong_header_ratio)

        return chains_pow

    def override_chain(self, attacker) -> None:
        """Override last N blocks with private chain."""

        # handle edge case when the first mined block is by selfish miner
        # seems to be working
        self.chain[attacker.blockchain.fork_block_id :] = []
        self.chain.extend(attacker.blockchain.chain)
