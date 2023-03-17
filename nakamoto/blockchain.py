"""Module for class Nakamoto consensus blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 16.3.2023
"""
from dataclasses import dataclass
from typing import Any, Dict

from base.blockchain_base import BlockBase, BlockchainBase


@dataclass
class Block(BlockBase):
    """Block class is class for Nakamoto consensus blocks."""

    def __iter__(self):
        yield self.data
        yield self.miner

    def __repr__(self):
        return f"Block(data={self.data}, miner={self.miner})"

    def to_dict(self) -> Dict[str, Any]:
        return {"data": self.data, "miner": self.miner}


@dataclass
class Blockchain(BlockchainBase):
    """Blockchain class is class for Nakamoto consensus blockchain."""

    def add_block(self, data, miner):
        new_block = Block(data, miner)
        self.chain.append(new_block)
        self.last_block_id += 1

    def print_chain(self):
        print(f"Lead: {self.owner}")
        for index, block in enumerate(self.chain):
            print(f"Block {index}:")
            print(f"  Data: {block.data}")
            print(f"  Miner: {block.miner}")

    def to_dict(self) -> Dict[str, Any]:
        return {"chain": [block.to_dict() for block in self.chain], "lead": self.owner}

    def size(self) -> int:
        """Get length of the blockchain."""
        return len(self.chain)

    def length(self) -> int:
        """Get length of private chain."""
        return self.size() + self.fork_block_id
