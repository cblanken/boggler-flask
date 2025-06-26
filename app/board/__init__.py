"""Blueprint for handling all Boggle Board data and solving"""

from boggler.boggler_utils import (
    BoggleBoard,
    build_boggle_tree,
    WordNode,
)
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
import operator
from functools import reduce
from requests import get, post
from requests.exceptions import JSONDecodeError
from ..db import (
    add_solved_board,
    get_dictionaries,
    get_solved_board_by_letters,
    get_solved_board_by_hash,
    make_board_hash,
)


Flask.url_defaults

MIN_BOARD_SIZE = 2
MAX_BOARD_SIZE = 6
MIN_WORD_LEN = 3
MAX_WORD_LEN = 20


bp = Blueprint("board", __name__, url_prefix="/board", static_folder="static")


def parse_board_params(rows, cols, letters):
    """Returns tuple of parsed parameters defining a Board

    Returns
        (board_letters, rows, cols)
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

    return (board_letters, rows, cols)


def find_paths_by_word(board_letters: list[str]) -> list[dict[str, WordNode]]:
    boggle_board = BoggleBoard(board_letters, len(board_letters) ** 2)
    board_alpha = sorted(set([cell.letters for cell in boggle_board.board.values()]))
    board_tree = {}
    index: dict[str, list[str]] = {}
    for letters in board_alpha:
        if len(letters) > 0:
            index[letters] = current_app.words_by_alpha[letters[0]]

    params = [
        (board_alpha, boggle_board, cell, index[cell.letters])
        for cell in boggle_board.board.values()
        if len(cell.letters) > 0
    ]

    print(f">> Generating WordTrees...")
    for p in params:
        res = build_boggle_tree(p)
        print(f">> {p[2]}")
        board_tree[p[2]] = res

    paths_by_word = reduce(
        operator.iconcat, [x.word_paths for x in board_tree.values()], []
    )
    return paths_by_word


@bp.route("/", methods=["GET"])
def board():
    """Default board route"""
    if request.method == "GET":
        rows = cols = 4
        (board_letters, rows, cols) = parse_board_params(rows, cols, None)
        return render_template(
            "pages/solver.html", board_letters=board_letters, rows=rows, cols=cols
        )


@bp.route("/api/solve", methods=["POST"])
def api_solve():
    """API endpoint for solving boards with the provided GET parameters

    Returns found words and their paths for a given board.

    If the board has not already been solved, then the new board is solved with the maximium
    possible `max_len` and then added to the database. Otherwise the solved_words are retrieved
    from the database.
    """

    data = request.json
    if data is None:
        return {}

    if request.method == "POST":
        rows = cols = data.get("sizeSelect")
        letters = data.get("letters")
        (board_letters, rows, cols) = parse_board_params(rows, cols, letters)
    else:
        return redirect(url_for("board.board"))

    data = {
        "letters": board_letters,
        "size": {
            "rows": rows,
            "cols": cols,
        },
    }

    solved_words = get_solved_board_by_letters(current_app.get_db(), board_letters)
    word_data = (
        find_paths_by_word(board_letters) if solved_words is None else solved_words
    )
    data["words"] = word_data
    data["total"] = len(data["words"])
    data["errors"] = []

    if solved_words is None:
        try:
            conn = current_app.get_db()
            add_solved_board(conn, rows, board_letters, word_data)
        except Exception:
            data["errors"].append(
                "An error occurred when adding the solved board to the database, so it won't be available under the Solved Boards."
            )

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
            f'http://localhost:{request.server[1]}{url_for("board.api_solve")}',
            headers=headers,
            timeout=30,
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

    if not len(data.get("errors", [])) > 0:
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
        found_words=data.get("words"),
        board_hash=make_board_hash(data.get("letters")),
        dictionaries=get_dictionaries(current_app.get_db()),
    )


@bp.route("/api/solved/<hash>", methods=["GET"])
def api_solved_by_hash(hash):
    data = get_solved_board_by_hash(current_app.get_db(), hash)
    return data or {}


@bp.route("/solved/<hash>", methods=["GET"])
def solved_by_hash(hash):
    data = get_solved_board_by_hash(current_app.get_db(), hash)
    if data is None:
        flash("This board doesn't exist!", "error")
        return render_template("errors/404.html"), 404

    if not data["is_current"]:
        flash(
            "This board was solved on an old version of the provided dictionaries, so it may be missing some words or include words that have since been deleted.",
            "warning",
        )

    return render_template(
        "pages/solved.html",
        found_words=data.get("words"),
        rows=data.get("rows"),
        cols=data.get("cols"),
        board_letters=json.loads(data.get("letters", "").encode("utf-8")),
        board_hash=hash,
        dictionaries=get_dictionaries(current_app.get_db()),
    )
