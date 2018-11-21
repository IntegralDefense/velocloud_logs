import logging

from settings import SCRIPT_LOG_FILE, LOG_LEVEL


def setup_logger(log_level=None, log_location=None):
    log_file = SCRIPT_LOG_FILE
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.addHandler(handler)
