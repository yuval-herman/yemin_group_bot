from collections import defaultdict


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
    for word in text.split():
        if is_banned(word):
            encountered = True
            break
        for ch in word:
            if is_arabic(ch):
                encountered = True
                break
    return not encountered


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
