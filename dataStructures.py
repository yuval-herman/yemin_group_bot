from enum import Enum, auto
from typing import TypedDict


class BotActions(Enum):
    none = auto()
    ban = auto()
    warn = auto()


class InvalidActions(Enum):
    none = auto()
    arabic = auto()
    swear = auto()


class InvalidTextInfo(TypedDict):
    is_invalid: bool
    msg: str
    invalid_action: InvalidActions
    action: BotActions
    warnings_amount: int
