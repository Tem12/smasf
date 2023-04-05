"""The module contains an implementation of
honest miner for Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
import random

from nakamoto.honest_miner import HonestMinerStrategy as NakamotoHonestMinerStrategy


class HonestMinerStrategy(NakamotoHonestMinerStrategy):
    """Honest miner class implementation for Subchain consensus."""

    # pylint: disable=no-self-use
    def select_subchain(self, ongoing_fork, competitors, public_subchain):
        """Select winning Subchain."""
        if ongoing_fork:
            winning_subchain = random.choice(competitors + [public_subchain])
        else:
            winning_subchain = public_subchain

        return winning_subchain
