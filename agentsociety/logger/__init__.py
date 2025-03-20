"""
Create logger named agentsociety as singleton for ray.
"""

import logging

__all__ = ["get_logger"]


def get_logger():
    logger = logging.getLogger("agentsociety")
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
