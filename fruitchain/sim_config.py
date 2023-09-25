"""Module containing the dataclass for parsed simulation config,
which is specific to the Subchain blockchain.

Author: Tomáš Hladký (xhladk15)
Date: 18.9.2023
"""
from dataclasses import dataclass
from math import fsum

from base.sim_config_base import SimulationConfigBase


@dataclass
class SimulationConfig(SimulationConfigBase):
    """Dataclass for Subchain simulation config.

    All default attributes for simulation are defined in the `SimulationConfigBase` class.

    Attributes:
        fruit_mine_prob (float): Probability of mining a fruit
        superblock_prob (float): Probability of mining a superblock
    """

    fruit_mine_prob: float
    superblock_prob: float

    def __post_init__(self) -> None:
        """Perform additional data validation after initialization."""
        super().__post_init__()

        if fsum([self.fruit_mine_prob,self.superblock_prob]) != 1.0:
            raise ValueError(
                "Mining probabilities of fruit and superblock must be equal to 1")
