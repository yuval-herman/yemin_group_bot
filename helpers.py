from datetime import datetime, timedelta
from collections import defaultdict

from db import create_user, delete_user, get_user, update_warnings


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
    wordsDict = defaultdict(lambda: None)
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


words_dict = load_word_dict()

banned_words = ["זונה", "שרמוטה", "זין"]


def is_banned(word: str) -> bool:
    return (words_dict[word] or word) in banned_words


def is_valid_text(text):
    encountered = False
    reason = ""
    for word in text.split():
        if is_banned(word):
            encountered = True
            reason = "מילה לא חוקית"
            break
        for ch in word:
            if is_arabic(ch):
                encountered = True
                reason = "טקסט ערבי"
                break
    return (not encountered, reason)


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


def increment_user_warnings_or_delete(user_id: int):
    """increment user warnings or delete him if he is passed the limit"""

    user = get_user(user_id)
    # if there is no user, create one
    if user is None:
        create_user(user_id)
        return False, 1

    last_warning_date = datetime.fromtimestamp(user["last_warning_date"])
    # if the last warning was more then half a year ago, ignore it
    if last_warning_date < datetime.now() - timedelta(seconds=5):
        warnings = 1
    else:
        warnings = user["warnings"] + 1
    if warnings > 2:
        delete_user(user_id)
        return True, warnings
    update_warnings(user_id, warnings)
    return False, warnings
