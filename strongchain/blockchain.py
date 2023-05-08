"""Module containing the Strongchain consensus blocks and blockchain classes.

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

    # Remove unwanted attribute from parent class
    is_weak: None = None

    def __repr__(self) -> str:
        return (
            f"WeakHeader(data={self.data}, miner={self.miner}, "
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

    def setup_weak_headers(self, weak_headers: List[WeakHeader]) -> None:
        """Add a list of weak headers to the current block."""
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

    # Must have some default value which is always overridden
    weak_to_strong_header_ratio: int = 42

    def add_block(
        self, data: str, miner: str, miner_id: int, is_weak: bool = False
    ) -> None:
        new_block = Block(data, miner, miner_id, is_weak)
        self.chain.append(new_block)
        self.last_block_id += 1

    def chains_pow(self) -> float:
        """Compute the total power of the whole blockchain."""
        return self.chains_pow_from_index(index=0)

    def chains_pow_from_index(self, index: int) -> float:
        """Compute the power of the blockchain from a given index."""
        chains_pow = 0
        for block in self.chain[index:]:
            # Strong block pow = 1
            chains_pow += 1
            for _ in block.weak_headers:
                # Weak header pow = 1 / weak_to_strong_header_ratio
                chains_pow = chains_pow + (1 / self.weak_to_strong_header_ratio)

        return chains_pow

    def override_chain(self, attacker) -> None:
        """Replace the last N blocks with the attacker's private chain."""

        # Handle edge case when the first mined block is by selfish miner
        # This seems to be working
        self.chain[attacker.blockchain.fork_block_id :] = []
        self.chain.extend(attacker.blockchain.chain)
