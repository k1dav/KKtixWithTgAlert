import logging
import sys
from os import environ
from typing import List

from loguru import logger

from .logging import InterceptHandler

API_PREFIX = "/api"
VERSION = "0.1.0"

ALLOWED_HOSTS: List[str] = ["*"]
DEBUG: bool = bool(environ.get("DEBUG", False))

PROJECT_NAME: str = environ.get("PROJECT_NAME", "template-api")
TIME_ZONE: str = environ.get("TIME_ZONE", "Asia/Taipei")
BOT_TOKEN: str = environ["TG_BOT_TOKEN"]


# logging config
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
