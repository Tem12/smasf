"""The module contains an implementation of
honest miner for Strongchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from nakamoto.honest_miner import HonestMinerStrategy as NakamotoHonestMinerStrategy
from strongchain.blockchain import WeakHeader


class HonestMinerStrategy(NakamotoHonestMinerStrategy):
    """Honest miner class implementation for Strongchain consensus."""

    def __init__(self, mining_power: int):
        super().__init__(mining_power)
        self.weak_headers = list()

    def add_weak_header(self, data, miner, miner_id):
        """Action after mining weak header."""
        new_block = WeakHeader(data, miner, miner_id)
        self.weak_headers.append(new_block)

    def clear_private_chain(self):
        """Clear public weak headers."""
