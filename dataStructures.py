from enum import Enum, auto, unique
from typing import Dict, TypedDict


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


@unique
class ReferralSource(Enum):
    social_media = "רשתות חברתיות"
    word_of_mouth = "מפה לאוזן"
    online_search = "חיפוש באינטרנט"
    telegram_search = "חיפוש בטלגרם"
    other_group = "קבוצה אחרת"
    advertisement = "פרסום"
    other = "אחר"


kick_messages: Dict[InvalidActions, str] = {
    InvalidActions.none: "",
    InvalidActions.swear: "לאחר שקילל והוזהר בפעם השלישית",
    InvalidActions.arabic: "לאחר שרשם בערבית",
}
