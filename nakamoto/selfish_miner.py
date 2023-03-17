"""The module contains an implementation of
selfish miner for Nakamoto consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
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

    def run(self):
        self.log.info("*******" * 20)
        self.log.info("Running selfish miner")
        self.mine_new_block()
        self.update_private_blockchain()
        self.setup_next_action()

        self.log.info(f"miner type: {self.miner_type}")
        self.log.info(f"action: {self.action}")
        self.log.info(f"private blockchain: {self.blockchain}")
        self.log.info(f"mining power: {self.mining_power}%")
        self.log.info(f"id: {self.miner_id}")

    def mine_new_block(self):
        self.log.info("Nakamoto SELFISH miner method mine_new_block")

    def update_private_blockchain(self):
        self.log.info("Update private blockchain in selfish miner")

    def setup_next_action(self):
        self.log.info("Setup next action in selfish miner")
