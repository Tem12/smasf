"""Module contains dataclass for parsed simulation config.

Author: Jan Jakub Kubik (xkubik32)
Date: 17.3.2023
"""

from dataclasses import dataclass
from typing import List


@dataclass
class SimulationConfigBase:
    """Dataclass for simulation config.

    Attributes:
        consensus_name (str): Name of the consensus algorithm.
        honest_miner (int): Mining power percentage of the honest miner.
        selfish_miners (List[int]): List of mining power percentages for selfish miners.
        gamma (float): Gamma value, used in some consensus algorithms.
        simulation_mining_rounds (int): Number of mining rounds in the simulation.
    """

    consensus_name: str
    honest_miner: int
    selfish_miners: List[int]
    gamma: float
    simulation_mining_rounds: int

    def __post_init__(self) -> None:
        """Perform data validation after initialization."""
        print(self.honest_miner)
        print(self.selfish_miners)
        if self.honest_miner + sum(self.selfish_miners) != 100:
            raise ValueError("Invalid mining power values. Sum of them must be 100.")

        if self.gamma not in [0, 0.5, 1]:
            raise ValueError("Invalid gamma value. Accepted values are 0, 0.5, and 1.")

        if self.simulation_mining_rounds <= 0:
            raise ValueError("Invalid number of mining rounds. It must be more than 0.")

        if any(sm > 49 for sm in self.selfish_miners):
            raise ValueError(
                "Selfish miner can't have above 49% of whole mining power."
            )
