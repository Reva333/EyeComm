import logging
from config.settings import LOGGING_ENABLED, LOG_LEVEL, LOG_FILE


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.propagate = False

    if not LOGGING_ENABLED:
        logger.disabled = True
        logger.addHandler(logging.NullHandler())
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
