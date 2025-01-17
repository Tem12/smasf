"""The module contains an implementation of
selfish miner for Nakamoto consensus protocol.

Author: Tomáš Hladký (xhladk15)
Date: 18.9.2023
"""
import random
from typing import Optional, Set

from base.blockchain import Blockchain
from base.miner_base import SelfishMinerAction as SA
from base.miner_base import SelfishMinerStrategyBase

from nakamoto.selfish_miner import SelfishMinerStrategy as NakamotoSelfishMinerStrategy

import json

BLOCK_REWARD = 10


class SelfishMinerStrategy(NakamotoSelfishMinerStrategy):
    """Selfish miner class implementation for Fruitchain consensus."""

    def __init__(self, mining_power: int):
        super().__init__(mining_power)
        self.fruit_queue = []
        self.private_queue = []

    def mine_new_fruit(self):
        self.private_queue.append(self.miner_id)

    def receive_new_fruit(self, miner_id):
        self.fruit_queue.append(miner_id)
        # pass
    
    def clear_fruit_queue(self):
        self.fruit_queue.clear()
        self.private_queue.clear()

    def get_fruit_count(self):
        return self.fruit_queue.count(self.miner_id) + self.private_queue.count(self.miner_id)
        # return self.private_queue.count(self.miner_id)

    def fruit_to_str(self):
        return json.dumps(self.fruit_queue + self.private_queue)
    
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
        # self.log.info(
        #     f"Selfish miner: {self.miner_id} is leader of round: {mining_round}"
        # )
        self.update_private_blockchain(public_blockchain, mining_round)

        if ongoing_fork:
            first_competitor = list(match_competitors)[0]
            # print('Selfish miner MATCH competitor')

            req_diff = (self.mining_power / 100) - (first_competitor.mining_power / 100)
            block_lead = self.blockchain.size() - first_competitor.blockchain.size()
            lead = (self.get_fruit_count() / BLOCK_REWARD) - (first_competitor.get_fruit_count() / BLOCK_REWARD)

            # print(f'self: {self.get_fruit_count() / BLOCK_REWARD}')
            # print(f'competitor: {first_competitor.get_fruit_count() / BLOCK_REWARD}')
            # if lead <= req_diff:
                # print(lead)
            # print(f'Lead: {lead}')
            # print(f'Req Diff: {req_diff}')

            # is this attacker id among competing attackers
            if self.miner_id in [
                competitor.miner_id for competitor in match_competitors
            ]:
                # He mined a new block and is currently the longest
                self.action = SA.OVERRIDE

            elif block_lead >= 2:
                # He has the longest chain and don't care what other does
                self.action = SA.WAIT

            elif (lead == 0) or (lead >= 0 and req_diff > 0 and lead <= req_diff):
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
                self.clear_fruit_queue()
                self.action = SA.ADOPT
        else:
            # no ongoing fork I currently mined new block
            self.action = SA.WAIT

        return ongoing_fork

    # def mine_new_block(
    #     self,
    #     mining_round: int,
    #     public_blockchain: Blockchain,
    #     ongoing_fork: bool,
    #     match_competitors: Optional[Set["SelfishMinerStrategyBase"]] = None,
    #     gamma: Optional[float] = None,
    # ) -> bool:
    #     """Mine a new block as a selfish miner for the Nakamoto consensus.

    #     Args:
    #         mining_round (int): The current mining round.
    #         public_blockchain (Blockchain): The public blockchain.
    #         ongoing_fork (bool): Indicates if there is an ongoing fork.
    #         match_competitors (Set[SelfishMinerStrategyBase], optional): A set of competing
    #                                                                      selfish miners.
    #         gamma (float, optional): The gamma value for the simulation.

    #     Returns:
    #         bool: Whether the fork is ongoing after the block is mined.
    #     """
    #     self.update_private_blockchain(public_blockchain, mining_round)

    #     if ongoing_fork:
    #         first_competitor = list(match_competitors)[0]

    #         lead = self.blockchain.size() - first_competitor.blockchain.size()

    #         # is this attacker id among competing attackers
    #         if self.miner_id in [
    #             competitor.miner_id for competitor in match_competitors
    #         ]:
    #             # He mined a new block and is currently the longest
    #             self.action = SA.OVERRIDE

    #         elif lead >= 2:
    #             # He has the longest chain and don't care what other does
    #             self.action = SA.WAIT

    #         elif lead == 0:
    #             # competitors have the same length as me but I started after ongoing competition
    #             # (it means later fork) so I randomly choice from ongoing branches and publish
    #             # my new block and integrate block to the main chain
    #             self.action = SA.MATCH

    #             winner = random.choice(match_competitors + [public_blockchain])
    #             if winner is not public_blockchain:
    #                 public_blockchain.chain[-1] = winner.blockchain.chain[-1]

    #             ongoing_fork = False
    #             public_blockchain.override_chain(self)
    #             public_blockchain.last_block_id += 1

    #             # clearing of private chains of all attackers which are currently in MATCH
    #             for attacker in match_competitors:
    #                 attacker.clear_private_chain()

    #         else:
    #             # competitors have longer chain than me
    #             self.clear_private_chain()
    #             self.action = SA.ADOPT
    #     else:
    #         # no ongoing fork I currently mined new block
    #         self.action = SA.WAIT

    #     return ongoing_fork

    def update_private_blockchain(
        self, public_blockchain: Blockchain, mining_round: int
    ) -> None:
        """Update the private blockchain of the selfish miner.

        Args:
            public_blockchain (Blockchain): The public blockchain.
            mining_round (int): The current mining round.
        """
        fruits = self.fruit_to_str()
        if self.blockchain.size() == 0:
            self.blockchain.initialize(public_blockchain.last_block_id)
            self.blockchain.add_block(
                fruits,
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
        else:
            self.blockchain.add_block(
                fruits,
                f"Selfish miner {self.miner_id}",
                self.miner_id,
            )
