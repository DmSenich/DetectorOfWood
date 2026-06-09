import logging
import os
from datetime import datetime


def setup_logger():
    log_name = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S.log"
    )
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("wood_volume")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_handler = logging.FileHandler(
        f"logs/{log_name}", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger