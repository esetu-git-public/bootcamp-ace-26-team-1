import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def _make_logger(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(LOG_DIR, filename))
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(stream)
    return logger


app_logger = _make_logger("app", "app.log")
audit_logger = _make_logger("audit", "audit.log")
