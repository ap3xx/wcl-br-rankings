import logging
import os
import sys
import time
from datetime import datetime


def config_log(level: str) -> logging.Logger:
    formatter = logging.Formatter(
        "[%(levelname)s][%(asctime)s][%(filename)-15s][%(lineno)4d][%(threadName)10s] - %(message)s"
    )
    formatter.converter = time.gmtime

    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logfile_path = os.getenv("LOGFILE_PATH", "/opt/logs")
    file_handler = logging.FileHandler(f"{logfile_path}/{datetime.now().strftime('%Y%m%d%H%M')}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger():
    global LOGGER
    return LOGGER


LOGGER = config_log(os.getenv("LOG_LEVEL", "INFO"))
