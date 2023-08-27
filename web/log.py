import logging
import os
import sys
import time

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def config_log(level: str) -> logging.Logger:
    formatter = logging.Formatter(
        "[%(levelname)s][%(asctime)s][%(filename)-15s][%(lineno)4d][%(threadName)10s] - %(message)s"
    )
    formatter.converter = time.gmtime

    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    channel = logging.StreamHandler(sys.stdout)

    channel.setFormatter(formatter)
    logger.addHandler(channel)

    return logger


def get_logger():
    global LOGGER
    return LOGGER


LOGGER = config_log(LOG_LEVEL)
