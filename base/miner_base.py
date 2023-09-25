"""The module contains a base classes for selfish, honest miners
and general properties and actions for them.

Author: Jan Jakub Kubik (xkubik32)
Date: 15.3.2023
"""
from abc import ABC, abstractmethod
from enum import Enum
from itertools import count
from typing import Any, List

from base.logs import create_logger


class HonestMinerAction(Enum):
    """General honest miner actions."""

    PUBLISH = 0


class SelfishMinerAction(Enum):
    """General selfish miner actions."""

    IDLE = 0
    ADOPT = 1
    WAIT = 2
    OVERRIDE = 3
    MATCH = 4


class MinerType(Enum):
    """Types of miners."""

    HONEST = 0
    SELFISH = 1


class MinerStrategyBase(ABC):
    """General base class for all miners.

    Attributes:
        action (Any): The current action taken by the miner.
        mining_power (float): The mining power of the miner.
        miner_id (int): The unique identifier of the miner.
        log (Any): Logger instance for logging events.
    """

    counter = count(start=1)

    def __init__(self, mining_power: float):
        self.action = None
        self.mining_power = mining_power
        self.miner_id = next(self.counter)
        self.log = create_logger(str(self.miner_id))

    # pylint: disable=too-many-arguments
    @abstractmethod
    def mine_new_block(
        self,
        mining_round: int,
        public_blockchain: Any,
        ongoing_fork: Any,
        match_competitors: List[int],
        gamma: float,
    ) -> None:
        """Base method for running the business logic of miner if he mines a new block.

        Args:
            mining_round (int): The current mining round.
            public_blockchain (Any): The public blockchain instance.
            ongoing_fork (Any): The ongoing fork in the blockchain.
            match_competitors (List[int]): A list of competitor miners' IDs.
            gamma (float): The gamma parameter representing the honest miners'
                           probability of mining on the private chain.
        """
        raise NotImplementedError

    def get_and_reset_action(self) -> Any:
        """Get action attribute and reset it.

        Returns:
            Any: The current action taken by the miner.
        """
        action = self.action
        self.action = None
        return action

    def get_action(self) -> Any:
        """Get action attribute.

        Returns:
            Any: The current action taken by the miner.
        """
        return self.action


class HonestMinerStrategyBase(MinerStrategyBase, ABC):
    """General base class for honest miner.

    Attributes:
        miner_type (MinerType): The type of the miner.
    """

    def __init__(self, mining_power: float):
        super().__init__(mining_power)
        self.miner_type = MinerType.HONEST


class SelfishMinerStrategyBase(MinerStrategyBase, ABC):
    """General base class for selfish miner.

    Attributes:
        miner_type (MinerType): The type of the miner.
    """

    def __init__(self, mining_power: float):
        super().__init__(mining_power)
        self.miner_type = MinerType.SELFISH

    @abstractmethod
    def decide_next_action(self, public_blockchain: Any, leader: int) -> None:
        """Base selfish miner method for setting up the action after public blockchain update.

        Args:
            public_blockchain (Any): The public blockchain instance.
            leader (int): The unique identifier of the current leader miner.
        """
        raise NotImplementedError

    @abstractmethod
    def update_private_blockchain(
        self, public_blockchain: Any, mining_round: int
    ) -> None:
        """Base selfish miner method for updating his private blockchain.

        Args:
            public_blockchain (Any): The public blockchain instance.
            mining_round (int): The current mining round.
        """
        raise NotImplementedError
