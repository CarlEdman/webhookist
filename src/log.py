#! python3

import logging
from rich.logging import RichHandler

log = logging.getLogger(__name__)

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

