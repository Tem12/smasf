"""The module contains an implementation of
honest miner for Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
from nakamoto.honest_miner import HonestMinerStrategy as NakamotoHonestMinerStrategy
from subchain.strong.blockchain import Blockchain


class HonestMinerStrategy(NakamotoHonestMinerStrategy):
    """Honest miner class implementation for Subchain consensus."""

    def __init__(self, mining_power: int):
        super().__init__(mining_power)
        self.blockchain_weak = Blockchain(owner="public blockchain weak")

    def clear_private_weak_chain(self) -> None:
        """Clear the private weak chain by resetting its list of blocks."""
        # public chain of weak blocks
        self.blockchain_weak.chain = []
