"""Module logs for customized logger creation.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""

import logging
from typing import Callable, Union

import structlog


def _create(
    name: str, get_logger_func: Callable, logging_options=logging
) -> Union[logging.Logger, structlog.BoundLogger]:
    """Functions for creating logger

    Creates logger with given name.

    Args:
        name: name of the logger
        get_logger_func: function for creating logger object

    Returns:
        Logger object based on get_logger_func
    """
    logging.setLoggerClass(logging_options.Logger)
    logger = get_logger_func(name)

    return logger


def create_logger(name: str) -> structlog.BoundLogger:
    """Creates logger with given name

    Creates object of structlog for logging with given name

    Args:
        name: name of the logger

    Returns:
        Structlog object with given name
    """
    # same as default processors, just without timestamps
    structlog.configure(
        processors=[
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.BoundLogger,
    )
    return _create(name, structlog.getLogger)
