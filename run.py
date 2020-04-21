import json
import logging

from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect

from app.utils import get_random_words, parse_cell_code, generate_response_grid, genid

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app = Flask(__name__)

grid = get_random_words("ressources/words.csv")
grid_response = generate_response_grid()

grids = {0: grid}
grids_response = {0: grid_response}


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/<id>/grid")
def get_grid(id):
    return render_template("grid.html", data=grids[id])


@app.route("/new")
def new_game():
    id = genid()
    grid = get_random_words("ressources/words.csv")
    grid_response = generate_response_grid()
    grids[id] = grid
    grids_response[id] = grid_response
    return redirect(f"{id}/grid")


@app.route("/cell")
def get_cell_data():
    cell_code = request.args.get('code')
    r, c = parse_cell_code(cell_code)
    val = grid_response[r, c]
    logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
