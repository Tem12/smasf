"""The module contains an implementation of
selfish miner for Strongchain consensus protocol.

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

    def add_weak_header(self, data, miner, miner_id):
        """Action after mining weak header."""
        new_block = WeakHeader(data, miner, miner_id)
        self.weak_headers.append(new_block)

    def clear_private_weak_headers(self) -> None:
        """Clear private weak headers."""
        self.weak_headers = []

    def clear_private_strong_chain(self) -> None:
        """Clear private chain of strong blocks."""
        self.blockchain.chain = []
        self.blockchain.fork_block_id = None

    def clear_private_chain(self):
        """Clear private blockchain and also private weak headers."""
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
            if sm_chain_pow > 1 and sm_chain_pow - 1 <= hm_chain_pow:
                # self.log.info("mine_new_block NOT changing OVERRIDE")
                self.action = SA.OVERRIDE
            else:
                self.action = SA.WAIT

        else:
            # self.log.info("mine_new_block changing OVERRIDE to ADOPT")
            self.clear_private_chain()
            self.action = SA.ADOPT

    def decide_next_action(self, public_blockchain: "Blockchain", leader: int) -> SA:
        # check powers of blockchains and if necessary update actions
        sm_chain_pow = self.blockchain.chains_pow()
        hm_chain_pow = public_blockchain.chains_pow_from_index(
            self.blockchain.fork_block_id
        )

        if sm_chain_pow > hm_chain_pow:
            if sm_chain_pow > 1 and sm_chain_pow - 1 <= hm_chain_pow:
                # self.log.info("decide_next_action NOT changing OVERRIDE")
                self.action = SA.OVERRIDE
            else:
                self.action = SA.WAIT

        else:
            # self.log.info("decide_next_action changing OVERRIDE to ADOPT")
            self.clear_private_chain()
            self.action = SA.ADOPT

        return self.action

    def decide_next_action_weak(self, public_blockchain: "Blockchain") -> SA:
        """Decide next action after HM mines and broadcasts new weak header."""

        # check powers of blockchains and if necessary update actions
        sm_chain_pow = self.blockchain.chains_pow()
        hm_chain_pow = public_blockchain.chains_pow_from_index(
            self.blockchain.fork_block_id
        )

        if sm_chain_pow > hm_chain_pow:
            if sm_chain_pow > 1 and sm_chain_pow - 1 <= hm_chain_pow:
                self.action = SA.OVERRIDE

        return self.action

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ) -> None:
        super().update_private_blockchain(public_blockchain, mining_round)

        # add weak headers to currently mined last block
        self.blockchain.chain[-1].setup_weak_headers(self.weak_headers)
        self.clear_private_weak_headers()
