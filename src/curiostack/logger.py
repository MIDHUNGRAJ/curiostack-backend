import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str, debug: bool = False) -> logging.Logger:
    """_summary_

    Args:
        name (str): _description_

    Returns:
        logging.Logger: _description_
    """
    # File will save to the root directory
    log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Log file name
    log_file = os.path.join(log_dir, "curiostack.log")

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    if debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

    # File handler (with rotation)
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setting formatter
    if debug:
        console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    if debug:
        logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
