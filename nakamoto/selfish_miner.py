"""The module contains an implementation of
selfish miner for Nakamoto consensus protocol.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
import random
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
        public_blockchain: Blockchain,
        ongoing_fork: bool,
        match_competitors: Optional[Set["SelfishMinerStrategyBase"]] = None,
        gamma: Optional[float] = None,
    ) -> bool:
        """Mine a new block as a selfish miner for the Nakamoto consensus.

        Args:
            mining_round (int): The current mining round.
            public_blockchain (Blockchain): The public blockchain.
            ongoing_fork (bool): Indicates if there is an ongoing fork.
            match_competitors (Set[SelfishMinerStrategyBase], optional): A set of competing
                                                                         selfish miners.
            gamma (float, optional): The gamma value for the simulation.

        Returns:
            bool: Whether the fork is ongoing after the block is mined.
        """
        self.log.info(
            f"Selfish miner: {self.miner_id} is leader of round: {mining_round}"
        )
        self.update_private_blockchain(public_blockchain, mining_round)

        if ongoing_fork:
            first_competitor = list(match_competitors)[0]

            lead = self.blockchain.size() - first_competitor.blockchain.size()

            # is this attacker id among competing attackers
            if self.miner_id in [
                competitor.miner_id for competitor in match_competitors
            ]:
                # He mined a new block and is currently the longest
                self.action = SA.OVERRIDE

            elif lead >= 2:
                # He has the longest chain and don't care what other does
                self.action = SA.WAIT

            elif lead == 0:
                # competitors have the same length as me but I started after ongoing competition
                # (it means later fork) so I randomly choice from ongoing branches and publish
                # my new block and integrate block to the main chain
                self.action = SA.MATCH

                winner = random.choice(match_competitors + [public_blockchain])
                if winner is not public_blockchain:
                    public_blockchain.chain[-1] = winner.blockchain.chain[-1]

                ongoing_fork = False
                public_blockchain.override_chain(self)
                public_blockchain.last_block_id += 1

                # clearing of private chains of all attackers which are currently in MATCH
                for attacker in match_competitors:
                    attacker.clear_private_chain()

            else:
                # competitors have longer chain than me
                self.clear_private_chain()
                self.action = SA.ADOPT
        else:
            # no ongoing fork I currently mined new block
            self.action = SA.WAIT

        return ongoing_fork

    def lead_length(self, public_blockchain: Blockchain) -> int:
        """Method for computing leading of selfish miner in comparison to honest miner.

        Args:
            public_blockchain (Blockchain): The public blockchain.

        Returns:
            int: The lead length of the selfish miner.
        """
        return self.blockchain.length() - public_blockchain.last_block_id

    def decide_next_action(self, public_blockchain: Blockchain, leader: int) -> SA:
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
        self, public_blockchain: Blockchain, mining_round: int
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
