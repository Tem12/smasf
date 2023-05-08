"""This module contains an implementation of the
honest miner for the Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
import random

from nakamoto.honest_miner import HonestMinerStrategy as NakamotoHonestMinerStrategy


class HonestMinerStrategy(NakamotoHonestMinerStrategy):
    """Honest miner class implementation for the Subchain consensus."""

    # pylint: disable=no-self-use
    def select_subchain(
        self, ongoing_fork: bool, competitors: list, public_subchain: "Subchain"
    ) -> "Subchain":
        """Select the winning Subchain.

        Args:
            ongoing_fork (bool): Indicates whether there is an ongoing fork.
            competitors (list): A list of competing subchains.
            public_subchain (Subchain): The current public subchain.

        Returns:
            Subchain: The selected winning subchain.
        """
        if ongoing_fork:
            winning_subchain = random.choice(competitors + [public_subchain])
        else:
            winning_subchain = public_subchain

        return winning_subchain
