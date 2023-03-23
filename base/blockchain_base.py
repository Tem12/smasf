"""Module for base class of blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 16.3.2023
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BlockBase(ABC):
    """BlocksBase class is the base class for blocks in all consensus protocols.

    Attributes:
        data (str): Data stored in the block.
        miner (Optional[str]): Miner who mined the block.
        miner_id (Optional[int]): Miner's unique identifier.
    """

    data: str
    miner: Optional[str] = None
    miner_id: Optional[int] = None

    @abstractmethod
    def __iter__(self):
        """Definition of iteration."""
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        """String representation."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialization of block to dictionary."""
        raise NotImplementedError


@dataclass
class BlockchainBase(ABC):
    """BlockchainBase class is the base class for blockchain in all consensus protocols.

    Attributes:
        chain (List): List of blocks in the blockchain.
        owner (Optional[str]): Owner of the blockchain. Defaults to 'Main chain'.
        last_block_id (Optional[int]): Identifier of the last block in the blockchain.
        fork_block_id (Optional[int]): Identifier of the block where the fork starts.
    """

    chain: List = field(default_factory=list)
    owner: Optional[str] = "Main chain"
    last_block_id: Optional[int] = 0
    fork_block_id: Optional[int] = None

    @abstractmethod
    def add_block(self, data: str, miner: str, miner_id: int, is_weak=False) -> None:
        """Add newly mined block to the blockchain."""
        raise NotImplementedError

    @abstractmethod
    def print_chain(self) -> None:
        """Print whole blockchain."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialization of blockchain to dictionary."""
        raise NotImplementedError
