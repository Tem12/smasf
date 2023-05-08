"""This module contains an implementation of a selfish miner for the Strongchain
consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from typing import Optional, Set

from base.miner_base import SelfishMinerAction as SA
from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy
from strongchain.blockchain import Blockchain, WeakHeader


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for Strongchain consensus."""

    def __init__(self, mining_power: int, ratio: int):
        super().__init__(mining_power)
        self.blockchain = Blockchain(
            owner=self.miner_id, weak_to_strong_header_ratio=ratio
        )
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

    def clear_private_weak_headers(self) -> None:
        """Clear the list of private weak headers."""
        self.weak_headers = []

    def clear_private_strong_chain(self) -> None:
        """Clear the private chain of strong blocks."""
        self.blockchain.chain = []
        self.blockchain.fork_block_id = None

    def clear_private_chain(self) -> None:
        """Clear the private blockchain and private weak headers."""
        self.clear_private_strong_chain()
        self.clear_private_weak_headers()

    # pylint: disable=too-many-arguments
    def mine_new_block(
        self,
        mining_round: int,
        public_blockchain: "Blockchain",
        ongoing_fork: bool,
        match_competitors: Optional[Set[int]] = None,
        gamma: Optional[float] = None,
    ) -> None:
        super().mine_new_block(
            mining_round, public_blockchain, ongoing_fork, match_competitors, gamma
        )

        # check powers of blockchains and if necessary update actions
        sm_chain_pow = self.blockchain.chains_pow()
        hm_chain_pow = public_blockchain.chains_pow_from_index(
            self.blockchain.fork_block_id
        )

        if sm_chain_pow > hm_chain_pow:
            # should be changed to config parameters
            if sm_chain_pow > 1.5 and sm_chain_pow - 1 <= hm_chain_pow:
                self.action = SA.OVERRIDE
            else:
                self.action = SA.WAIT
        else:
            self.clear_private_chain()
            self.action = SA.ADOPT

    def decide_next_action(self, public_blockchain: "Blockchain", leader: int) -> SA:
        # check powers of blockchains and if necessary update actions
        sm_chain_pow = self.blockchain.chains_pow()
        hm_chain_pow = public_blockchain.chains_pow_from_index(
            self.blockchain.fork_block_id
        )

        if sm_chain_pow > hm_chain_pow:
            if sm_chain_pow > 1.5 and sm_chain_pow - 1 <= hm_chain_pow:
                self.action = SA.OVERRIDE
            else:
                self.action = SA.WAIT
        else:
            self.clear_private_chain()
            self.action = SA.ADOPT

        return self.action

    def decide_next_action_weak(
        self,
        public_blockchain: "Blockchain",
        leader: int,
        weak_to_strong_header_ratio: int,
    ) -> SA:
        """Decide the next action after the honest miner mines and broadcasts a new weak header.

        Args:
            public_blockchain (Blockchain): The public blockchain.
            leader (int): The current leader's miner ID.
            weak_to_strong_header_ratio (int): The ratio between weak and strong headers.

        Returns:
            SA: The next action for the selfish miner.
        """

        # Check powers of blockchains and update actions if necessary
        sm_chain_pow = self.blockchain.chains_pow()
        hm_chain_pow = (
            public_blockchain.chains_pow_from_index(self.blockchain.fork_block_id)
            + len(leader.weak_headers) / weak_to_strong_header_ratio
        )

        if sm_chain_pow > hm_chain_pow:
            if sm_chain_pow > 1.5 and sm_chain_pow - 1 <= hm_chain_pow:
                self.action = SA.OVERRIDE
            else:
                self.action = SA.IDLE
        else:
            self.action = SA.IDLE

        return self.action

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ) -> None:
        super().update_private_blockchain(public_blockchain, mining_round)

        # Add weak headers to the currently mined last block
        self.blockchain.chain[-1].setup_weak_headers(self.weak_headers)
        self.clear_private_weak_headers()
