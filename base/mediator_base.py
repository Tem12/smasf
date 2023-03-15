"""The module contains a base class for Mediator,
from which is inherited in all blockchain mediators.

Author: Jan Jakub Kubik (xkubik32)
Date: 14.3.2023
"""
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
    def validate_blockchain_config(self):
        """Validation of blockchain simulation configuration from yaml config."""
        raise NotImplementedError

    def __call_parse_config(self, simulation_config: dict):
        """Call defined parse_config ."""
        return self.parse_config(simulation_config)
