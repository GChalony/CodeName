import cv2
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as cols
import numpy as np

print("Generating codename maps...")

with open("words.csv", encoding="utf8") as words_file:
    words = words_file.readlines()
words = [w.replace("\n", "") for w in words]
np.random.shuffle(words)
words = words[:25]

base_array = [1] * 9 + [2] * 8 + [3] + [0] * 7
np.random.shuffle(base_array)
map = np.resize(base_array, (5, 5))
map = np.array(map, dtype=np.uint8)

colors = ["white", "red", "blue", "black"]
text_colors = [colors[val] if val != 0 else "black" for val in base_array]

fig = plt.figure(figsize=(12, 5))

# Add skull
pos = list.index(base_array, 3)
x, y = pos%5/5 + .1, pos//5 / 5 + .06
ax = plt.gca()
skull = cv2.imread("skull.png")
imagebox = OffsetImage(skull, zoom=0.08)
ab = AnnotationBbox(imagebox, (x, y), frameon=False)
ax.add_artist(ab)

for i, w in enumerate(words):
    x, y = i%5/5 + .1, i//5 / 5 + .1
    if i == pos:
        y+=.03
    plt.text(x, y, w.upper(), ha="center", va="center", c=text_colors[i], fontfamily="serif")

ps = np.linspace(0.002, 0.998, 6)
for p in ps:
    plt.axhline(p)
    plt.axvline(p)
fig.tight_layout()
plt.axis("off")

figbw = plt.figure(figsize=(12, 5))
for i, w in enumerate(words):
    x, y = i%5/5 + .1, i//5 / 5 + .1
    plt.text(x, y, w.upper(), ha="center", va="center", fontfamily="serif")

ps = np.linspace(0.002, 0.998, 6)
for p in ps:
    plt.axhline(p)
    plt.axvline(p)
figbw.tight_layout()
plt.axis("off")

path = f"images/{datetime.now().strftime('%Y-%m-%d %H%M%S')}"
os.mkdir(path)

fig.savefig(f"{path}/colored_image")
figbw.savefig(f"{path}/bw_image")

print(f"Images saved at {path}")
print("Done!")
