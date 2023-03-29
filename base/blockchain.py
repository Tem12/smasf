"""Module for class Nakamoto consensus blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
from dataclasses import dataclass
from typing import Any, Dict

from base.blockchain_base import BlockBase, BlockchainBase


@dataclass
class Block(BlockBase):
    """Block class for Nakamoto consensus blocks.

    Attributes:
        data (str): Data stored in the block.
        miner (str): Miner who created the block.
        miner_id (int): Unique identifier for the miner.
    """

    def __iter__(self):
        yield self.data
        yield self.miner
        yield self.miner_id
        yield self.is_weak

    def __repr__(self) -> str:
        return (
            f"Block(data={self.data}, miner={self.miner}, "
            f"miner_id={self.miner_id}, is_weak={self.is_weak})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "miner": self.miner,
            "miner_id": self.miner_id,
            "is_weak": self.is_weak,
        }


@dataclass
class Blockchain(BlockchainBase):
    """Blockchain class for Nakamoto consensus blockchain."""

    def initialize(self, fork_block_id: int) -> None:
        """Initialize the blockchain after a fork.

        Args:
            fork_block_id (int): The block ID where the fork occurred.
        """
        self.fork_block_id = fork_block_id

    def __iter__(self):
        return iter(self.chain)

    def add_block(self, data: str, miner: str, miner_id: int, is_weak=False) -> None:
        new_block = Block(data, miner, miner_id, is_weak)
        self.chain.append(new_block)
        self.last_block_id += 1

    def print_chain(self) -> None:
        print(f"Lead: {self.owner}")
        for index, block in enumerate(self.chain):
            print(f"Block {index}:")
            print(f"  Data: {block.data}")
            print(f"  Miner: {block.miner}")

    def override_chain(self, attacker):
        """Override last N blocks with private chain."""

        # handle edge case when the first mined block is by selfish miner
        fork_id = attacker.blockchain.fork_block_id
        if fork_id != 0:
            index = fork_id - 1
        else:
            index = fork_id
        self.chain[index:] = []
        self.chain.extend(attacker.blockchain.chain)

    def to_dict(self) -> Dict[str, Any]:
        return {"chain": [block.to_dict() for block in self.chain], "lead": self.owner}

    def size(self) -> int:
        """Get length of the blockchain.

        Returns:
            int: Length of the blockchain.
        """
        return len(self.chain)

    def length(self) -> int:
        """Get length of private chain.

        Returns:
            int: Length of the private chain.
        """
        return self.size() + self.fork_block_id
