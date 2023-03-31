"""The module contains an implementation of
selfish miner for Nakamoto consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
from typing import Optional, Set

from base.blockchain import Blockchain
from base.miner_base import SelfishMinerAction as SA
from base.miner_base import SelfishMinerStrategyBase


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

    def clear_private_chain(self) -> None:
        """Clear private chain after it overrides the main chain."""
        self.blockchain.chain = []
        self.blockchain.fork_block_id = None

    # pylint: disable=too-many-arguments
    def mine_new_block(
        self,
        mining_round: int,
        public_blockchain: "Blockchain",
        ongoing_fork: bool,
        match_competitors: Optional[Set[int]] = None,
        gamma: Optional[float] = None,
    ) -> None:
        """Mine a new block as a selfish miner for the Nakamoto consensus.

        Args:
            mining_round (int): The current mining round.
            public_blockchain (Blockchain): The public blockchain.
            ongoing_fork (bool): Indicates if there is an ongoing fork.
            match_competitors (set, optional): A set of competing selfish miners.
            gamma (float, optional): The gamma value for the simulation.
        """
        self.log.info(
            f"Selfish miner: {self.miner_id} is leader of round: {mining_round}"
        )
        self.update_private_blockchain(public_blockchain, mining_round)

        if ongoing_fork:
            first_competitor = list(match_competitors)[0]
            if (
                len(match_competitors) == 1
                and self.miner_id == first_competitor.miner_id
            ):
                # only 1 competitor and that's me and I currently mined new block
                self.action = SA.OVERRIDE

            else:
                # there is more competitors or the only one and it is not me
                lead = self.blockchain.size() > first_competitor.blockchain.size()
                if lead >= 2:
                    # I have the longest chain and don't care what other does
                    self.action = SA.WAIT

                elif lead == 1:
                    # I have the longest chain but just by 1 block
                    self.action = SA.OVERRIDE

                elif lead == 0:
                    # competitors have the same length as me
                    self.action = SA.MATCH

                else:
                    # competitors have longer chain than me
                    self.clear_private_chain()
                    self.action = SA.ADOPT

        else:
            # no ongoing fork I currently mined new block
            self.action = SA.WAIT

    def lead_length(self, public_blockchain: "Blockchain") -> int:
        """Method for computing leading of selfish miner in comparison to honest miner.

        Args:
            public_blockchain (Blockchain): The public blockchain.

        Returns:
            int: The lead length of the selfish miner.
        """
        return self.blockchain.length() - public_blockchain.last_block_id

    def decide_next_action(self, public_blockchain: "Blockchain", leader: int) -> SA:
        """Decide the next action for the selfish miner.

        Args:
            public_blockchain (Blockchain): The public blockchain.
            leader (int): The ID of the leader miner.

        Returns:
            SA: The next action for the selfish miner.
        """
        if self.blockchain.size() > 0:
            # selfish miner has private blockchain
            lead = self.lead_length(public_blockchain)

            if lead >= 2:
                # private blockchain is more than 1 blocks longer than public blockchain
                self.action = SA.WAIT

            elif lead == 1:
                # private blockchain is exactly 1 block longer than public blockchain
                self.action = SA.OVERRIDE

            elif lead == 0:
                # private blockchain has the same length as public blockchain
                self.action = SA.MATCH

            else:
                # private blockchain is smaller than public blockchain
                self.clear_private_chain()
                self.action = SA.ADOPT

        else:
            # selfish miner has no private blockchain
            self.action = SA.IDLE

        return self.action

    def update_private_blockchain(
        self, public_blockchain: "Blockchain", mining_round: int
    ) -> None:
        """Update the private blockchain of the selfish miner.

        Args:
            public_blockchain (Blockchain): The public blockchain.
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
