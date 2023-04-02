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
