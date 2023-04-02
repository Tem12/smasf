"""The module contains an implementation of
selfish miner for Strongchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy
from strongchain.blockchain import Blockchain, WeakHeader


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for Strongchain consensus."""

    def __init__(self, mining_power: int):
        super().__init__(mining_power)
        self.blockchain = Blockchain(owner=self.miner_id)
        self.weak_headers = list()

    def add_weak_header(self, data, miner, miner_id):
        """Action after mining weak header."""
        new_block = WeakHeader(data, miner, miner_id)
        self.weak_headers.append(new_block)

    def clear_private_chain(self):
        """Clear private blockchain and also private weak headers."""
