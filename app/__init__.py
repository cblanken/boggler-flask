"""Main app module
"""

from flask import Flask, request, render_template, redirect
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy
from config import config
from boggler.boggler_utils import BoggleBoard, build_full_boggle_tree, read_boggle_file
from boggler.board_randomizer import read_dice_file, get_random_board
import json
from math import sqrt
from random import choices
import importlib.resources as ILR

db = SQLAlchemy()
sock = Sock()

# Initialize DICE for random board generation
DICE = {}


def handle_dice_file(filename: str):
    try:
        with ILR.path("boggler.dice", filename) as f:
            return read_dice_file(f)
    except FileNotFoundError:
        print(f"Unable to load '{filename}' DICE file")


DICE = {
    "classic": handle_dice_file("4x4_classic.csv"),
    "new": handle_dice_file("4x4_new.csv"),
    "big": handle_dice_file("5x5_big.csv"),
    "super": handle_dice_file("6x6_super_big.csv"),
}


def create_app(config_name):
    """Return base Flask app object"""
    app = Flask(__name__)
    sock.init_app(app)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    @app.errorhandler(404)
    def page_not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(_):
        return render_template("errors/500.html"), 500

    @app.route("/", methods=["GET", "POST"])
    def index():
        return redirect("board")

    @app.route("/history")
    def history():
        return render_template("pages/solve_history.html")

    @app.route("/api/random", methods=["GET"])
    def api_random():
        """API endpoint to get a random board"""
        # Default letter distribution for board sizes without dice
        # fmt: off
        alphabet = [
            "a", "a", "a", "a", "a", "a", "a", "a", "b", "b",
            "b", "c", "c", "c", "d", "d", "d", "d", "e", "e",
            "e", "e", "e", "e", "e", "e", "e", "e", "f", "f",
            "g", "g", "g", "h", "h", "h", "i", "i", "i", "i",
            "i", "i", "i", "j", "k", "k", "l", "l", "l", "l",
            "l", "m", "m", "m", "n", "n", "n", "n", "n", "o",
            "o", "o", "o", "o", "o", "p", "p", "p", "qu", "r",
            "r", "r", "r", "s", "s", "s", "s", "s", "t", "t",
            "t", "t", "t", "u", "u", "u", "u", "v", "v", "w",
            "w", "x", "y", "y", "y", "z",
        ]
        # fmt: off
        try:
            size = int(request.args.get("size"))
        except TypeError:
            size = 4

        dice_type = request.args.get("dice_type")
        if dice_type in DICE and size == int(sqrt(len(DICE[dice_type]))):
            return {"board": get_random_board(DICE.get(dice_type)), "dice_type": dice_type}
        else:
            return {
                "board": [choices(alphabet, k=size) for x in range(0, size)],
                "dice_type": "random",
            }

    @sock.route("/solve")
    def solve(ws):
        while True:
            data = ws.receive()
            print(f"RECEIVED DATA: {data}")

            # TODO: solve board
            solve_data = json.loads(data.encode("utf-8"))
            print(f"SOLVE DATA: {solve_data}")

            # TODO error handling json
            ws.send(solve_data)

    return app
