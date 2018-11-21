import os

from dotenv import load_dotenv

load_dotenv()

# Basic Info
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTERPRISE_ID = os.environ.get("VELOCLOUD_ENTERPRISE_ID", None)
HOST = os.environ.get("VELOCLOUD_HOST", None)
LOGS_TO_PULL = ["events", "firewall"]

# CREDENTIALS
ENTERPRISE_USERNAME = os.environ.get("VELOCLOUD_ENTERPRISE_USERNAME", None)
ENTERPRISE_PASSWORD = os.environ.get("VELOCLOUD_ENTERPRISE_PASSWORD", None)
OPERATOR_USERNAME = os.environ.get("VELOCLOUD_OPERATOR_USERNAME", None)
OPERATOR_PASSWORD = os.environ.get("VELOCLOUD_OPERATOR_PASSWORD", None)

# Logging
TIME_FILE = os.path.join(
    BASE_DIR, os.environ.get("VELOCLOUD_TIME_FILE", "default_time.log")
)
LOG_DIRECTORY = os.path.join(BASE_DIR, "logs")
SCRIPT_LOG_FILE = os.path.join(LOG_DIRECTORY, "script.log")
FIREWALL_LOG_FILE = os.path.join(LOG_DIRECTORY, "firewall.log")
EVENT_LOG_FILE = os.path.join(LOG_DIRECTORY, "events.log")
ALERT_LOG_FILE = os.path.join(LOG_DIRECTORY, "alerts.log")
LOG_LEVEL="DEBUG"

# Default Time config (in seconds)
DEFAULT_TIME_DELTA = 600