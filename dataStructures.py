from enum import Enum, auto
from typing import TypedDict


class BotActions(Enum):
    ban = auto()
    warn = auto()
    none = auto()


class InvalidTextInfo(TypedDict):
    is_invalid: bool
    msg: str
    action: BotActions
    warnings_amount: int
