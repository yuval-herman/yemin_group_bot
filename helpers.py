from datetime import datetime, timedelta
from collections import defaultdict
import json
from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dataStructures import InvalidActions, InvalidTextInfo, ReferralSource
from dataStructures import BotActions, InvalidTextInfo

from db import (
    add_censor_string,
    create_user,
    delete_user,
    get_user,
    read_censor_strings,
    remove_censor_string,
    update_warnings,
)


def is_arabic(ch):
    return (
        "\u0600" <= ch <= "\u06FF"
        or "\u0750" <= ch <= "\u077F"
        or "\u08A0" <= ch <= "\u08FF"
        or "\uFB50" <= ch <= "\uFDFF"
        or "\uFE70" <= ch <= "\uFEFF"
        or "\U00010E60" <= ch <= "\U00010E7F"
        or "\U0001EE00" <= ch <= "\U0001EEFF"
    )


def load_word_dict():
    wordsDict = defaultdict[str, Union[str, None]](lambda: None)
    baseWord = ""
    nextIsBaseWord = True
    with open("data/nouns.txt", "r") as f:
        for line in f.readlines():
            if line == "-------\n":
                nextIsBaseWord = True
                continue
            word = line.split(" ")[0]
            if nextIsBaseWord:
                baseWord = word
                nextIsBaseWord = False
            wordsDict[word] = baseWord
    return wordsDict


def get_runtime_banned_words():
    return banned_words


def add_runtime_censor_word(word: str):
    word = stem(word) or word
    add_censor_string(word)
    banned_words.add(word)


def remove_runtime_censor_word(word: str):
    remove_censor_string(word)
    if word in banned_words:
        banned_words.remove(word)


def is_banned(word: str) -> bool:
    return (stem(word) or word) in banned_words


prefixes = [
    "",
    "ו",
    "ה",
    "ש",
    "כש",
    "מש",
    "לכש",
    "ב",
    "כ",
    "ל",
    "מ",
    "מה",
    "שכש",
]


def stem(word: str):
    stemmed = word
    for prefix in prefixes:
        if word.startswith(prefix):
            stemmed = words_dict[word[len(prefix) :]]
        if stemmed is not None:
            break
    return stemmed


def is_valid_text(text: str) -> InvalidTextInfo:
    for word in text.split():
        if is_banned(word):
            return {
                "is_invalid": True,
                "msg": "מילה לא חוקית",
                "action": BotActions.warn,
                "warnings_amount": 0,
                "invalid_action": InvalidActions.swear,
            }
        for ch in word:
            if is_arabic(ch):
                return {
                    "is_invalid": True,
                    "msg": "טקסט ערבי",
                    "action": BotActions.ban,
                    "warnings_amount": 0,
                    "invalid_action": InvalidActions.arabic,
                }

    return {
        "is_invalid": False,
        "action": BotActions.none,
        "msg": "",
        "warnings_amount": 0,
        "invalid_action": InvalidActions.none,
    }


def get_group_rules(user_name: str):
    return f"""
🛑שלום {user_name}, נא לשים לב לחוקי הקבוצה!🛑
מי שלא יציית יזרק במקום!

כללים בקבוצה:
* אין להשתמש בקללות ובשפה לא ראויה.
* אין כניסה ל0מלאנים.
* אין לשלוח הודעות קישורים לקבוצות שלא קשורות למחאת הימין🇮🇱.

כל דברי הסתה או אלימות לא על דעת המנהלים בקבוצה ואסורים בהחלט
"""


def get_join_poll(user_name: str, user_id: int):
    keyboard = [
        [
            InlineKeyboardButton(
                source.value,
                callback_data=json.dumps([source.value, user_id], ensure_ascii=False),
            ),
        ]
        for source in list(ReferralSource)
    ]

    return f"""{user_name} אנחנו שמחים שהצטרפת אלינו!
כדי לשלוח הודעות בקבוצה, עליך לבחור איך הגעת לקבוצה, תודה רבה!""", InlineKeyboardMarkup(
        keyboard
    )


def increment_user_warnings_or_delete(
    user_id: int, invalidTextInfo: InvalidTextInfo
) -> InvalidTextInfo:
    """increment user warnings or delete him if he is passed the limit"""

    user = get_user(user_id)
    # if there is no user, create one
    if user is None:
        create_user(user_id)
        invalidTextInfo["warnings_amount"] = 1
        update_warnings(user_id, invalidTextInfo["warnings_amount"])
        return invalidTextInfo

    last_warning_date = datetime.now()
    if user["last_warning_date"]:
        last_warning_date = datetime.fromtimestamp(user["last_warning_date"])

    # if the last warning was more then half a year ago, ignore it
    if last_warning_date < datetime.now() - timedelta(days=182):
        invalidTextInfo["warnings_amount"] = 1
    else:
        invalidTextInfo["warnings_amount"] = user["warnings"] + 1

    if invalidTextInfo["warnings_amount"] > 2:
        delete_user(user_id)
        invalidTextInfo["action"] = BotActions.ban
        return invalidTextInfo
    update_warnings(user_id, invalidTextInfo["warnings_amount"])
    return invalidTextInfo


words_dict = load_word_dict()

for string in ("זונה", "השרמוטה", "זין"):
    add_censor_string(stem(string) or string)

banned_words = {x[1] for x in read_censor_strings()}
