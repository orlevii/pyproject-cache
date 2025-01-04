from typing import Annotated, Any

import click
from pydantic import BaseModel
from swiftcli.types import OptionSettings

from pyproject_cache.logger import logger


def set_log_level(_ctx: click.Context, _: Any, value: int) -> int:
    if value == 0:
        log_level = "ERROR"
    elif value == 1:
        log_level = "WARNING"
    elif value == 2:
        log_level = "INFO"
    else:
        log_level = "DEBUG"
    logger.setLevel(log_level)
    return value


class CommonParams(BaseModel):
    verbose: Annotated[
        int,
        OptionSettings(
            count=True,
            aliases=["-v"],
            help="Sets the verbosity level",
            callback=set_log_level,
        ),
    ] = 0
