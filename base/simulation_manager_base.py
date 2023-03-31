"""The module contains a base class for Mediator,
from which is inherited in all blockchain mediators.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

from base.logs import create_logger


class ActionObjectStore:
    """A container for storing objects associated with actions.

    The ActionObjectStore class provides a convenient way to store objects
    that are associated with specific actions. It allows adding and removing
    objects, retrieving objects for a given action, getting the list of all
    actions, and clearing the entire store.

    Attributes:
        _store (Dict[Any, List]): A dictionary containing lists of objects keyed by actions.
        _all_actions (List[Any]): A list of all actions in the store.
    """

    def __init__(self):
        """Initialize the ActionObjectStore with an empty store and an empty list of actions."""
        self._store = {}
        self._all_actions = []

    def add_object(self, action: Any, obj: Any = None) -> None:
        """Add an object associated with the given action to the store.

        Args:
            action (Any): The action to associate with the object.
            obj (Any, optional): The object to store. Defaults to None.
        """
        if action not in self._store:
            self._store[action] = [obj]
        else:
            self._store[action].append(obj)

        self._all_actions.append(action)

    def remove_object(self, action: Any, obj: Any = None) -> None:
        """Remove an object associated with the given action from the store.

        Args:
            action (Any): The action associated with the object.
            obj (Any, optional): The object to remove. Defaults to None.
        """
        if action in self._store and obj in self._store[action]:
            self._store[action].remove(obj)
            self._all_actions.remove(action)

            if not self._store[action]:
                del self._store[action]

    def get_objects(self, action: Any) -> List:
        """Retrieve a list of objects associated with the given action.

        Args:
            action (Any): The action to retrieve objects for.

        Returns:
            List: List of objects associated with the action.
        """
        return self._store.get(action, [])

    def get_actions(self) -> List:
        """Retrieve the list of all actions in the store.

        Returns:
            List: List of all actions.
        """
        return self._all_actions

    def clear(self) -> None:
        """Clear the store and the list of actions."""
        self._store.clear()
        self._all_actions.clear()


class SimulationManagerBase(ABC):
    """Abstract base class for all blockchain simulation managers."""

    def __init__(self, simulation_config: Dict[str, Any], blockchain: str):
        self.log = create_logger(blockchain)
        self.config = self.__call_parse_config(simulation_config)

    @abstractmethod
    def parse_config(self, simulation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the configuration for the simulation.

        Args:
            simulation_config (Dict[str, Any]): The simulation configuration dictionary.

        Returns:
            Dict[str, Any]: Parsed configuration dictionary.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """Run the simulation."""
        raise NotImplementedError

    @abstractmethod
    def resolve_overrides(self) -> None:
        """Resolve the 'override' actions in the simulation."""
        raise NotImplementedError

    @abstractmethod
    def resolve_matches(self) -> None:
        """Resolve the 'match' actions in the simulation."""
        raise NotImplementedError

    @staticmethod
    def choose_leader(choices: List[Any], weights: List[float]) -> Any:
        """Select a leader for the current round according to the given weights.

        Args:
            choices (List[Any]): List of possible leaders.
            weights (List[float]): List of weights for each leader.

        Returns:
            Any: The selected leader.
        """
        return random.choices(choices, weights, k=1)[0]

    def validate_blockchain_config_keys(
        self, dictionary: Dict[str, Any], expected_keys: set
    ) -> None:
        """Validate top-level keys in the parsed simulation config.

        Args:
            dictionary (Dict[str, Any]): The dictionary to validate.
            expected_keys (set): The set of expected keys.
        """
        self.log.info("validating simulation config")
        dict_keys = set(dictionary.keys())
        if dict_keys != expected_keys:
            raise ValueError(
                f"You are missing or you have used redundant top-level keys in the YAML config."
                f" Please use just these keys: {expected_keys}"
            )

    def general_config_validations(
        self,
        simulation_config: Dict[str, Any],
        expected_keys_extra: Optional[List] = (),
    ) -> Dict[str, Any]:
        """
        Validates the general configuration of a simulation.

        Args:
            simulation_config (Dict[str, Any]): The simulation configuration dictionary.
            expected_keys_extra (List): The extra expected keys to validate.
                                        Bu default it is empty list.

        Raises:
            ValueError: If there is not exactly 1 honest miner or no selfish
            miners in the configuration.

        Returns:
            Dict[str, Any]: The validated simulation configuration dictionary.
        """
        # check main keys
        expected_keys: Set[str] = {
            "consensus_name",
            "miners",
            "gamma",
            "simulation_mining_rounds",
        }
        for key in expected_keys_extra:
            expected_keys.add(key)

        sim_config: Dict[str, Any] = list(simulation_config.values())[0]
        self.validate_blockchain_config_keys(sim_config, expected_keys)

        miners: Dict[str, Any] = sim_config["miners"]
        if len(list(miners["honest"])) != 1:
            raise ValueError("You must setup exactly 1 honest miner")
        if len(list(miners["selfish"])) == 0:
            raise ValueError("You must setup at least 1 selfish miner")

        return sim_config

    def __call_parse_config(self, simulation_config: Dict[str, Any]) -> Dict[str, Any]:
        return self.parse_config(simulation_config)
