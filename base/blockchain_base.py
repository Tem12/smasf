"""Module for base class of blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 16.3.2023
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class BlockBase(ABC):
    """BlocksBase class is base class for blocks in all consensus protocols."""

    data: str
    miner: str = None

    @abstractmethod
    def __iter__(self):
        """Definition of iteration."""
        raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        """String representation."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialization of block to dictionary."""
        raise NotImplementedError


@dataclass
class BlockchainBase(ABC):
    """BlockchainBase class is base class for blockchain in all consensus protocols."""

    chain: list = field(default_factory=list)
    lead: str = "Main chain"
    last_block_id: int = 0
    fork_block_id: int = None

    @abstractmethod
    def add_block(self, data, miner):
        """Add newly mined block to the blockchain."""
        raise NotImplementedError

    @abstractmethod
    def print_chain(self):
        """Print whole blockchain."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialization of blockchain to dictionary."""
        raise NotImplementedError
