"""Logging utilities."""

from loguru import logger
import sys


def setup_logger(name: str, level: str = "INFO") -> None:
    """
    Configure logger for FeXsics.
    
    Args:
        name: Logger name.
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level=level
    )
    logger.add(
        f"logs/{name}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
        level=level,
        rotation="500 MB"
    )
