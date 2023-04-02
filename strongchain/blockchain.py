"""Module for class Strongchain consensus blocks and blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from dataclasses import dataclass

from base.blockchain import Blockchain as NakamotoBlockchain


@dataclass
class Blockchain(NakamotoBlockchain):
    """Blockchain class for Strongchain consensus."""
