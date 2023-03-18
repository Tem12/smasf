"""The module contains a base class for Mediator,
from which is inherited in all blockchain mediators.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
import random
from abc import ABC, abstractmethod

from base.logs import create_logger


class MediatorBase(ABC):
    """Abstract base class class for all blockchain mediators."""

    def __init__(self, simulation_config: dict, blockchain: str):
        self.log = create_logger(blockchain)
        self.config = self.__call_parse_config(simulation_config)

    @abstractmethod
    def parse_config(self, simulation_config):
        """This method is entry point for running all checks for specific provider monitor."""
        raise NotImplementedError

    @abstractmethod
    def run(self):
        """This method is entry point for running all checks for specific provider monitor."""
        raise NotImplementedError

    @abstractmethod
    def resolve_overrides(self):
        """This method is used after one or multiple attackers
        after `decide_next_action` have `override` action.
        """
        raise NotImplementedError

    @abstractmethod
    def resolve_matches(self):
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
        return self.parse_config(simulation_config)
