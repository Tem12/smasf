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

    def __init__(self, mining_power: int):
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
        mining_round: int,
        public_blockchain: "Blockchain",
        ongoing_fork: bool,
        match_competitors=None,
        gamma=None,
    ) -> bool:
        """Mine a new block as a selfish miner for the Nakamoto consensus.

        Args:
            mining_round (int): The current mining round.
            public_blockchain ('Blockchain'): The public blockchain.
            ongoing_fork (bool): Indicates if there is an ongoing fork.
            match_competitors (set, optional): A set of competing selfish miners.
            gamma (float, optional): The gamma value for the simulation.

        Returns:
            bool: Whether the fork is ongoing after the block is mined.
        """
        self.log.info(
            f"Selfish miner: {self.miner_id} is leader of round: {mining_round}"
        )

        self.update_private_blockchain(public_blockchain, mining_round)

        if self.blockchain.size() != 0:
            if ongoing_fork:
                self.action = SA.OVERRIDE
            else:
                self.action = SA.WAIT

        return ongoing_fork

    def decide_next_action(self, public_blockchain: "Blockchain", leader: int) -> SA:
        """Decide the next action for the selfish miner.

        Args:
            public_blockchain ('Blockchain'): The public blockchain.
            leader (int): The ID of the leader miner.

        Returns:
            SA: The next action for the selfish miner.
        """
        if self.blockchain.size() > 0:
            chain_difference = (
                self.blockchain.length() - public_blockchain.last_block_id
            )

            if chain_difference >= 2:
                self.action = SA.WAIT

            elif chain_difference == 1:
                self.action = SA.OVERRIDE

            elif chain_difference == 0:
                self.action = SA.MATCH

            else:
                self.blockchain.chain = []
                self.blockchain.fork_block_id = None
                self.action = SA.ADOPT

        else:
            self.action = SA.IDLE

        return self.action

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ):
        """Update the private blockchain of the selfish miner.

        Args:
            public_blockchain ('Blockchain'): The public blockchain.
            mining_round (int): The current mining round.
        """
        if self.blockchain.size() == 0:
            self.blockchain.initialize(public_blockchain.last_block_id)
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
        else:
            self.blockchain.add_block(
                f"Block {mining_round} data",
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
