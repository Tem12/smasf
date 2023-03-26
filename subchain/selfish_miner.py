"""The module contains an implementation of
selfish miner for Subchain consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""
from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for Nakamoto consensus."""

    # pylint: disable=unused-argument
    @staticmethod
    def select_subchain(ongoing_fork, competitors, public_subchain):
        """Select winning Subchain."""
        print("")
