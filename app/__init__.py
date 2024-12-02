"""Main app module
"""

from flask import Flask, current_app, g, jsonify, request, render_template, redirect
from flask_debugtoolbar import DebugToolbarExtension
from config import config
from boggler.board_randomizer import read_dice_file, get_random_board
from math import sqrt
from pathlib import Path
from random import choices
from string import ascii_lowercase
from sys import getsizeof
from time import time
from flask_socketio import SocketIO
import importlib.resources as ILR
import sqlite3
from .db.load_dictionary import load_default_dictionaries
from .db import get_dictionaries, get_words, get_solved_boards


# Initialize DICE for random board generation
DICE = {}


def handle_dice_file(filename: str):
    try:
        with ILR.path("boggler.dice", filename) as f:
            return read_dice_file(f)
    except FileNotFoundError:
        print(f"Unable to load '{filename}' DICE file")


DICE = {
    "classic": {"dice": handle_dice_file("4x4_classic.csv"), "size": 4},
    "new": {"dice": handle_dice_file("4x4_new.csv"), "size": 4},
    "big": {"dice": handle_dice_file("5x5_big.csv"), "size": 5},
    "super": {"dice": handle_dice_file("6x6_super_big.csv"), "size": 6},
}


socketio = SocketIO()


def create_app(config_name):
    """Return base Flask app object"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    data_dir = Path(app.config.get("DATA_DIR"))
    data_dir.mkdir(exist_ok=True)

    db_path = Path(data_dir, "boggler.sqlite")
    try:
        sqlite3.connect(db_path)
    except Exception:
        raise RuntimeError(f"Unable to create or connect to database at: {db_path}")

    def get_db() -> sqlite3.Connection | None:
        db = getattr(g, "_database", None)
        if db is None:
            try:
                setattr(g, "_database", sqlite3.connect(db_path))
                db = g._database
            except sqlite3.OperationalError as e:
                print(
                    f"An error ocurred when attempting to connect to the database. Error: {e}"
                )
            except Exception as e:
                # TODO: fix exception specificity
                print(
                    f"Application failed to connect or initialize database. Ensure the data directory is accessible and has appropriate permissions. Error: {e}"
                )

        return db

    app.get_db = get_db

    def load_words():
        with app.app_context():
            db = get_db()
            if db is None:
                raise RuntimeError(
                    f"Unable to load words into database. DB connection is {db}"
                )
            app.__setattr__("words_by_alpha", {})
            print("Loading words into memory...")
            start = time()
            for letter in ascii_lowercase:
                print(f"> Loading words with prefix: {letter}")
                app.words_by_alpha[letter] = get_words(db, prefix=letter)
            end = time()
            print(
                f"Loaded dictionaries into memory in {(end - start):.4f} seconds with a size of {getsizeof(app.words_by_alpha) / 1024}MB"
            )

    def init_db():
        print("Initializing database...")
        with app.app_context():
            db = get_db()
            if db is None:
                raise RuntimeError(
                    f"The database could not be initialized because the DB connection is {db}"
                )

            with app.open_resource("db/schema.sql", mode="r") as f:
                db.cursor().executescript(f.read())
                db.commit()

            load_default_dictionaries(db, data_dir)

    # This file is necessary to prevent multiple threads
    # from attempting to initialize the db simultaneously
    disable_init_file = Path(".db_no_init")

    try:
        with app.app_context():
            db = get_db()
            if (
                db is None or (app.config.get("INIT_DB")
            ) and not disable_init_file.exists()):
                disable_init_file.touch()
                disable_init_file.chmod(0o660)
                init_db()
            
            db = get_db()
            curr = db.cursor()
            table_names = [x[0] for x in curr.execute("SELECT name FROM sqlite_master").fetchall()]
            db_has_tables = all(
                [
                    table in table_names
                    for table in [
                        "dictionaries",
                        "words",
                        "dictionary_words",
                        "solved_boards",
                    ]
                ]
            )

            if not db_has_tables:
                print("The database has not been properly initialized. Try starting the application with INIT_DB=1")
                exit(1)

            load_words()
    except RuntimeError as e:
        print(f"Unable to start application: {e}")
        exit(1)

    if app.debug:
        DebugToolbarExtension(app)
        app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = getattr(app, "_database", None)
        if db is not None:
            db.close()

    @app.errorhandler(404)
    def page_not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(_):
        return render_template("errors/500.html"), 500

    @app.route("/", methods=["GET", "POST"])
    def index():
        return redirect("board")

    @app.route("/api/solved", methods=["GET"])
    def api_solved():
        solved_boards = get_solved_boards(current_app.get_db())
        return jsonify(solved_boards)

    @app.route("/solved")
    def history():
        return render_template("pages/solved_boards.html")

    @app.route("/api/random", methods=["GET"])
    def api_random():
        """API endpoint to get a random board"""
        args = request.args

        # Parse args
        dice_type = args.get("dice_type")
        dice = DICE.get(dice_type, None)

        board = []
        if dice is None:
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
                size = int(args.get("size"))
            except TypeError:
                size = 4

            board = [choices(alphabet, k=size) for _ in range(0, size)],
            dice_type = "random"
        else:
            board = get_random_board(dice.get("dice"))
            size = dice.get("size", 0)

        return {"board": board, "dice_type": dice_type, "size": size}

    @app.route("/api/dictionaries")
    def api_dictionaries():
        return jsonify(get_dictionaries(current_app.get_db()))

    socketio.init_app(app)
    return app
