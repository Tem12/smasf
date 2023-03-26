"""The module contains an implementation of
honest miner for Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
from nakamoto.honest_miner import HonestMinerStrategy as NakamotoHonestMinerStrategy


class HonestMinerStrategy(NakamotoHonestMinerStrategy):
    """Honest miner class implementation for Subchain consensus."""

    # pylint: disable=unused-argument
    @staticmethod
    def select_subchain(ongoing_fork, competitors, public_subchain):
        """Select winning Subchain."""
        print("")
