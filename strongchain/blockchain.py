"""Module for class Strongchain consensus blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from dataclasses import dataclass, field
from typing import List

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


@dataclass
class Block(NakamotoBlock):
    """Block data class for Strongchain consensus."""

    weak_headers: List = field(default_factory=list)

    def setup_weak_headers(self, weak_headers):
        """Setup weak headers."""
        self.weak_headers.extend(weak_headers)


@dataclass
class Blockchain(NakamotoBlockchain):
    """Blockchain class for Strongchain consensus."""

    def power(self):
        """Compute whole blockchain power."""

    def power_from_index(self):
        """Compute blockchain power from index."""
