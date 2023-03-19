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
    """Create a logger with the given name.

    Args:
        name (str): Name of the logger.
        get_logger_func (Callable): Function for creating logger object.
        logging_options (Optional): Logging options. Default is Python's logging module.

    Returns:
        Union[logging.Logger, structlog.BoundLogger]: Logger object based on get_logger_func.
    """
    logging.setLoggerClass(logging_options.Logger)
    logger = get_logger_func(name)

    return logger


def create_logger(name: str) -> structlog.BoundLogger:
    """Create a logger with the given name.

    Create a structlog logger object with the given name.

    Args:
        name (str): Name of the logger.

    Returns:
        structlog.BoundLogger: Structlog logger object with the given name.
    """
    # Same as default processors, just without timestamps
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
