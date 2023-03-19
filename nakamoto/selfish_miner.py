"""The module contains an implementation of
selfish miner for Nakamoto consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
from base.miner_base import SelfishMinerAction as SA
from base.miner_base import SelfishMinerStrategyBase
from nakamoto.blockchain import Blockchain


class SelfishMinerStrategy(SelfishMinerStrategyBase):
    """Selfish miner class implementation for Nakamoto consensus."""

    def __init__(self, mining_power):
        super().__init__(mining_power)
        self.blockchain = Blockchain(owner=self.miner_id)

    def __postinit__(self):
        if not hasattr(self, "private_blockchain"):
            raise NotImplementedError(
                'Subclass must initialize the "private_blockchain" variable.'
            )

    # pylint: disable=too-many-arguments
    def mine_new_block(
        self,
        mining_round,
        public_blockchain,
        ongoing_fork,
        match_competitors=None,
        gamma=None,
    ):
        self.log.info(
            f"Selfish miner: {self.miner_id} is leader of round: {mining_round}"
        )

        self.update_private_blockchain(public_blockchain, mining_round)

        if self.blockchain.size() != 0:
            if ongoing_fork:
                # THIS WORKS ONLY FOR 1 ATTACKER - multiple attacker = + MATCH
                self.action = SA.OVERRIDE
            else:
                self.action = SA.WAIT

        # Nothing to do with ongoing for, but it can be changed by honest miner
        return ongoing_fork

    def decide_next_action(self, public_blockchain, leader):
        if self.blockchain.size() > 0:
            self.log.info(
                f"Private chain length: {self.blockchain.size()}, "
                f"fork start: {self.blockchain.fork_block_id}"
            )
            chain_difference = (
                self.blockchain.length() - public_blockchain.last_block_id
            )
            self.log.info(f"Chain difference is: {chain_difference}")

            if chain_difference >= 2:
                # wait action should be published block - but not necessary
                self.action = SA.WAIT
                self.log.info("WAIT Nothing to do ....")

            elif chain_difference == 1:
                self.log.info("Override.")
                self.log.info(self.blockchain.fork_block_id)
                self.action = SA.OVERRIDE

            elif chain_difference == 0:
                self.log.info("Match.")
                self.action = SA.MATCH

            else:
                self.log.info("Adopt honest miner is winning.")
                # TDO ongoing fork bude riesenie v mediatorovi
                # ongoing_fork = False
                self.blockchain.chain = []
                self.blockchain.fork_block_id = None
                self.action = SA.ADOPT

        else:
            self.action = SA.IDLE
            self.log.info("Private chain has 0 length --> nothing to do")

        return self.action

    def update_private_blockchain(self, public_blockchain, mining_round):
        if self.blockchain.size() == 0:
            # empty local blockchain
            self.blockchain.initialize(public_blockchain.last_block_id)
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
        else:
            # have already initialized local blockchain
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
