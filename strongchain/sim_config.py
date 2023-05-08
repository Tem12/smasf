"""Module containing the dataclass for parsed simulation config,
specific to the Strongchain blockchain.

Author: Jan Jakub Kubik (xkubik32)
Date: 02.04.2023
"""
from dataclasses import dataclass

from base.sim_config_base import SimulationConfigBase


@dataclass
class SimulationConfig(SimulationConfigBase):
    """Dataclass for Strongchain simulation config.

    All default attributes for simulation are defined in the `SimulationConfigBase` class.

    Attributes:
        weak_to_strong_header_ratio (int): The ratio of weak to strong headers.
    """

    weak_to_strong_header_ratio: int

    def __post_init__(self) -> None:
        """Perform additional data validation after initialization."""
        super().__post_init__()

        if self.weak_to_strong_header_ratio < 1:
            raise ValueError(
                "Weak to strong headers ratio must be at least 1 or higher."
            )
