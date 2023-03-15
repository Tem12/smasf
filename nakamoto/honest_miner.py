"""The module contains an implementation of
honest miner for Nakamoto consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
from base.miner_base import HonestMinerStrategyBase


class HonestMinerStrategy(HonestMinerStrategyBase):
    """Honest miner class implementation for Nakamoto consensus."""

    def run(self):
        self.log.info("*******" * 20)
        self.log.info("Running honest miner")
        self.mine_new_block()

        self.log.info(f"logger: {self.log}")
        self.log.info(f"miner type: {self.miner_type}")
        self.log.info(f"action: {self.action}")
        self.log.info(f"mining power is {self.mining_power}")
        self.log.info(f"id is {self.miner_id}")

    def mine_new_block(self):
        self.log.info("Nakamoto HONEST method mine new block")
