import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

from codenameapp.utils import generate_response_grid, generate_random_words

words = generate_random_words("../static/ressources/words.csv")
answers = generate_response_grid()

cmap = ListedColormap(["#808080", "#ff5300", "#0af", "#000"])


def draw_grid(colors, ax):
    ax.pcolormesh(colors, cmap=cmap, edgecolors='w', linewidth=2)
    ax.set_axis_off()
    ax.set_aspect(0.5)
    for i in range(5):
        for j in range(5):
            text = ax.text(j + .5, i + .5, words[i, j],
                           ha="center", va="center", color="w")


ts = datetime.datetime.now().strftime("%m-%d-%YT%H%M%S")
fig, ax = plt.subplots()
draw_grid(answers, ax)
fig.tight_layout()
fig.savefig(f"../generated/{ts}-answers")
print(f"../generated/{ts}-answers")
fig, ax = plt.subplots()
draw_grid(np.full((5, 5), 0), ax)
fig.tight_layout()
fig.savefig(f"../generated/{ts}-empty.png")
#plt.show()
