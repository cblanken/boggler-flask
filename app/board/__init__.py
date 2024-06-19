"""Blueprint for handling all Boggle Board data and solving
"""

from boggler.boggler_utils import (
    BoggleBoard,
    build_boggle_tree,
    WordNode,
)
from boggler.board_randomizer import read_dice_file, get_random_board
from flask import (
    Blueprint,
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import json
from logging import log
from functools import reduce
import operator
import os
from multiprocessing import Pool
from requests import get, post
from requests.exceptions import JSONDecodeError
from ..db import add_solved_board, get_words_by_dict

Flask.url_defaults

MIN_BOARD_SIZE = 2
MAX_BOARD_SIZE = 6
MIN_WORD_LEN = 3
MAX_WORD_LEN = 20


bp = Blueprint("board", __name__, url_prefix="/board", static_folder="static")


def parse_board_params(rows, cols, letters, dictionary=None, max_len=None):
    """Returns tuple of parsed parameters defining a Board

    Returns
        (board_letters, rows, cols, dictionary_path, max_len)
    """
    # Default size of board is 4x4
    try:  # Default row count
        rows = int(rows)
        rows = min(rows, MAX_BOARD_SIZE)
        rows = max(rows, MIN_BOARD_SIZE)
    except (TypeError, ValueError):
        rows = 4
    try:  # Default column count
        cols = int(cols)
        cols = min(cols, MAX_BOARD_SIZE)
        cols = max(cols, MIN_BOARD_SIZE)
    except (TypeError, ValueError):
        cols = 4

    # Default empty board and listify letters
    if letters is None:
        letters = []
    else:
        letters = letters.split(",")
        letters.extend((rows * cols - len(letters)) * [""])

    # Limit blocks to max of 2 letters
    letters = list(map(lambda x: x[:2] if len(x) >= 2 else x, letters))

    # Remove whitespace
    letters = [letter.strip() for letter in letters]

    # Lowercase
    letters = [x.lower() for x in letters]

    # 2D listify letters
    board_letters = []
    for row in range(0, rows):
        offset = row * cols
        board_letters.append(letters[offset : offset + cols])

    # Default dictionary
    dictionary_path = f"wordlists/{dictionary}"
    if not os.path.exists(dictionary_path) or dictionary is None:
        dictionary_path = "wordlists/wordnik_2021_07_29"
        print(f"Defaulting to {dictionary_path}")

    # Default maximum word length
    try:
        max_len = int(max_len)
        max_len = min(max_len, MAX_WORD_LEN)
        max_len = max(max_len, MIN_WORD_LEN)
    except (TypeError, ValueError):
        max_len = 16

    return (board_letters, rows, cols, dictionary_path, max_len)


def find_paths_by_word(
    board_letters: list[str], max_len: int, dict_name: str
) -> list[dict[str, WordNode]]:
    boggle_board = BoggleBoard(board_letters, max_len)
    board_alpha = sorted(set([cell.letters for cell in boggle_board.board.values()]))
    board_tree = {}
    index: dict[str, list[str]] = {}
    for letters in board_alpha:
        words = get_words_by_dict(current_app.get_db(), dict_name, letters)
        index[letters] = words

    params = [
        (board_alpha, boggle_board, cell, index[cell.letters])
        for cell in boggle_board.board.values()
    ]

    with Pool(processes=len(boggle_board.board)) as pool:
        for i, res in enumerate(pool.map(build_boggle_tree, params)):
            board_tree[params[i][2].pos] = res

    paths_by_word = reduce(
        operator.iconcat, [x.word_paths for x in board_tree.values()], []
    )
    return paths_by_word


@bp.route("/", methods=["GET"])
def board():
    """Default board route"""
    if request.method == "GET":
        args = request.args
        # breakpoint()
        rows = cols = 4
        (board_letters, rows, cols, _, max_len) = parse_board_params(rows, cols, None)
        return render_template(
            "pages/solver.html", board_letters=board_letters, rows=rows, cols=cols
        )


@bp.route("/api/solve", methods=["POST"])
def api_solve():
    """API endpoint for solving boards with the provided GET parameters

    Returns JSON containing board data and found words
    """

    data = request.json
    if data is None:
        return {}
    elif request.method == "POST":
        rows = cols = data.get("sizeSelect")
        letters = data.get("letters")
        dictionary = data.get("dictionarySelect")
        max_len = data.get("maxLengthSelect")
        (board_letters, rows, cols, dictionary_path, max_len) = parse_board_params(
            rows, cols, letters, dictionary, max_len
        )
    else:
        return redirect(url_for("board.board"))

    try:
        word_data = find_paths_by_word(board_letters, max_len, dictionary)
    except Exception as e:
        return "Badly formed board solve request", 400
    data = {
        "words": word_data,
        "total": len(word_data),
        "letters": board_letters,
        "max_len": max_len,
        "dictionary": os.path.basename(os.path.normpath(dictionary_path)),
        "size": {
            "rows": rows,
            "cols": cols,
        },
    }

    data["errors"] = []
    try:
        conn = current_app.get_db()
        add_solved_board(conn, rows, board_letters, dictionary, max_len, word_data)
    except Exception as e:
        data["errors"].append(
            "An error occurred when adding the solved board to the database, so it won't be available under the Solved Boards."
        )
        raise
    return data


@bp.route("/solve", methods=["POST"])
def solve():
    """Endpoints for solved boards by task ID"""

    data = request.form.to_dict()
    headers = {
        "Content-Type": "application/json",
    }
    try:
        data = post(
            request.host_url + url_for("board.api_solve"),
            headers=headers,
            timeout=10,
            data=json.dumps(data),
        ).json()
    except JSONDecodeError as e:
        print(
            "Solve data could not be retrieved from the api endpoint due to a JSON Decoding error",
            e,
        )
        flash("The board could not be solved due to a JSON decoding error.", "error")
        return get(url=request.host_url + url_for("board.board"), params=data)

    # TODO: handle missing post data
    for e in data.get("errors", []):
        flash(e, "error")
    flash("Board solved!", "message")
    flash(
        "Don't forget to checkout the word paths by clicking on words in the table.",
        "message",
    )
    return render_template(
        "pages/solved.html",
        rows=data.get("size").get("rows"),
        cols=data.get("size").get("cols"),
        board_letters=data.get("letters"),
        dictionary=data.get("dictionary_path"),
        max_len=data.get("max_len"),
        found_words=data.get("words"),
    )
