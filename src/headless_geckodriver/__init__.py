"""Headless geckodriver for Selenium."""
import os
import logging

# Set the logging level.
DEBUGGING = any(
    [os.environ.get("DEBUG", "False").lower() == arg for arg in ["true", "1"]]
)
LOG_LEVEL = logging.DEBUG if DEBUGGING is True else logging.INFO


def get_logger() -> logging.Logger:
    """Create the global logger.

    Returns:
        logging.Logger: Logger object.
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=LOG_LEVEL,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logger
