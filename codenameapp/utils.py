import json
from uuid import uuid4
import numpy as np


def generate_random_words(path_to_words="ressources/words.csv"):
    with open(path_to_words, encoding="utf8") as words_file:
        words = words_file.readlines()
    words = [w.replace("\n", "").capitalize() for w in words]
    np.random.shuffle(words)
    words = words[:25]
    return np.array(words).reshape((5, 5))


def parse_array_to_json(a):
    n, m = a.shape
    res = {}
    for r in range(n):
        for c in range(m):
            res[f"r{r}c{c}"] = a[r][c]
    return json.dumps(res)


def parse_cell_code(cell_code):
    r, c = int(cell_code[1]), int(cell_code[3])
    return r, c


def generate_response_grid():
    base_array = [1] * 9 + [2] * 8 + [3] + [0] * 7
    np.random.shuffle(base_array)
    map = np.resize(base_array, (5, 5))
    map = np.array(map, dtype=np.uint8)
    return map

