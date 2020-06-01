# This script contains a few utils method, meant to be called from the console
# to handle words, dropping duplicates etc...

WORDS_PATH = "static/ressources/words.csv"


def read_words():
    with open(WORDS_PATH, "r") as f:
        words = f.readlines()
    return words


def sort_words():
    words = read_words()
    with open(WORDS_PATH, "w") as f:
        f.writelines(sorted(words))


def drop_duplicates(words):
    return list(dict.fromkeys(words))


def remove_duplicates():
    words = drop_duplicates(read_words())
    with open(WORDS_PATH, "w") as f:
        f.writelines(words)


def normalize():
    words = read_words()
    capitalized = [w.capitalize() for w in words]
    with open(WORDS_PATH, "w") as f:
        f.writelines(capitalized)
