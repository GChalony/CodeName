# This script contains a few utils method, meant to be called from the console
# to handle words, dropping duplicates etc...
import sys

WORDS_PATH = "static/ressources/words.csv"


def read_words():
    with open(WORDS_PATH, "r", encoding='utf8') as f:
        words = f.readlines()
    return words


def sort_words():
    words = read_words()
    with open(WORDS_PATH, "w", encoding='utf8') as f:
        f.writelines(sorted(words))


def drop_duplicates(words):
    return list(dict.fromkeys(words))


def remove_duplicates():
    words = drop_duplicates(read_words())
    with open(WORDS_PATH, "w", encoding='utf8') as f:
        f.writelines(words)


def normalize():
    words = read_words()
    capitalized = [w.capitalize() for w in words]
    with open(WORDS_PATH, "w", encoding='utf8') as f:
        f.writelines(capitalized)


def _get_code(char):
    return int.from_bytes(char.encode(), sys.byteorder)


chars_levels = {
    "warn": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "classic": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \néèêëàâîôûçÂ-'"
}
char_levels_codes = {
    level: [_get_code(c) for c in s] for level, s in chars_levels.items()
}


def get_weird_chars(words=None, level="classic"):
    if words is None:
        words = read_words()
    res = []
    for l, w in enumerate(words):
        for c in w:
            code = _get_code(c)
            if code not in char_levels_codes[level]:
                print(l, c, w)
                res.append((l, c))
    return res
