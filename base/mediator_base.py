"""The module contains a base class for Mediator,
from which is inherited in all blockchain mediators.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
import random
from abc import ABC, abstractmethod

from base.logs import create_logger


class ActionObjectStore:
    """A container for storing objects associated with actions.

    The ActionObjectStore class provides a convenient way to store objects
    that are associated with specific actions. It allows adding and removing
    objects, retrieving objects for a given action, getting the list of all
    actions, and clearing the entire store.

    Attributes:
        _store (dict): A dictionary containing lists of objects keyed by actions.
        _all_actions (list): A list of all actions in the store.
    """

    def __init__(self):
        """Initialize the ActionObjectStore with an empty store and an empty list of actions."""
        self._store = {}
        self._all_actions = []

    def add_object(self, action, obj=None):
        """Add an object associated with the given action to the store.

        Args:
            action: The action to associate with the object.
            obj: The object to store (default is None).
        """
        if action not in self._store:
            self._store[action] = [obj]
        else:
            self._store[action].append(obj)

        self._all_actions.append(action)

    def remove_object(self, action, obj=None):
        """Remove an object associated with the given action from the store.

        Args:
            action: The action associated with the object.
            obj: The object to remove (default is None).
        """
        if action in self._store and obj in self._store[action]:
            self._store[action].remove(obj)
            self._all_actions.remove(action)

            if not self._store[action]:
                del self._store[action]

    def get_objects(self, action):
        """Retrieve a list of objects associated with the given action.

        Args:
            action: The action to retrieve objects for.

        Returns:
            List of objects associated with the action.
        """
        return self._store[action]

    def get_actions(self):
        """Retrieve the list of all actions in the store.

        Returns:
            List of all actions.
        """
        return self._all_actions

    def clear(self):
        """Clear the store and the list of actions."""
        self._store.clear()
        self._all_actions.clear()


class MediatorBase(ABC):
    """Abstract base class class for all blockchain mediators."""

    def __init__(self, simulation_config: dict, blockchain: str):
        self.log = create_logger(blockchain)
        self.config = self.__call_parse_config(simulation_config)

    @abstractmethod
    def __parse_config(self, simulation_config):
        """This method is entry point for running all checks for specific provider monitor."""
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        raise NotImplementedError

    @abstractmethod
    def __resolve_overrides(self):
        """This method is used after one or multiple attackers
        after `decide_next_action` have `override` action.
        """
        raise NotImplementedError

    @abstractmethod
    def __resolve_matches(self, match_competitors, ongoing_fork):
        """This method is used after one or multiple attackers
        after `decide_next action` have `match` action.
        """
        raise NotImplementedError

    @staticmethod
    def choose_leader(choices, weights):
        """Select according weights leader of current round."""
        return random.choices(choices, weights, k=1)[0]

    def validate_blockchain_config_keys(
        self, dictionary: dict, expected_keys: set
    ) -> None:
        """Top level keys validation of parsed simulation config."""
        self.log.info("validating simulation config")
        dict_keys = set(dictionary.keys())
        if dict_keys != expected_keys:
            raise ValueError(
                f"You are missing or you have used redundant top level keys in YAML config."
                f" Please use just these keys: {expected_keys}"
            )

    def __call_parse_config(self, simulation_config: dict):
        """Call defined parse_config ."""
        return self.__parse_config(simulation_config)
