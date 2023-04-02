import re
from pathlib import Path

REG_NORMALIZE = re.compile(r'(?!(\.[a-z0-9]{3,4}))[^0-9a-zA-Za-яА-Яіїґ_]')

CYRILLIC = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = TRANSLATION = (
    "a",
    "b",
    "v",
    "g",
    "d",
    "e",
    "e",
    "j",
    "z",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "h",
    "ts",
    "ch",
    "sh",
    "sch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
    "je",
    "i",
    "ji",
    "g",
)


def normalize(string: str) -> str:
    '''Function normalizes the string according to regex and translates the string using two lists.

    Returns translated string.
    '''
    letter_string = re.sub(REG_NORMALIZE, '_', string)
    TRANS = {ord(c.upper()): l.upper() for c, l in zip(CYRILLIC, TRANSLATION)}
    TRANS.update({ord(c) : l for c, l in zip(CYRILLIC, TRANSLATION)})
    trans_string = letter_string.translate(TRANS)

    return trans_string 
