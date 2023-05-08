"""This module contains an implementation of an honest miner for the Strongchain
consensus protocol.

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

    def add_weak_header(self, data: str, miner: str, miner_id: int) -> None:
        """Create a new weak header and add it to the list of weak headers.

        Args:
            data (str): The data to be added to the weak header.
            miner (str): The miner who mined the weak header.
            miner_id (int): The unique identifier of the miner.
        """
        new_block = WeakHeader(data, miner, miner_id)
        self.weak_headers.append(new_block)

    def clear_private_weak_chain(self) -> None:
        """Clear the list of private weak headers."""
        self.weak_headers = []
