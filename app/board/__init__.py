"""Blueprint for handling all Boggle Board data and solving
"""
import functools
import operator
import os
from math import sqrt
from random import choices
import importlib.resources as ILR
from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)
from boggler.boggler_utils import BoggleBoard, build_full_boggle_tree, read_boggle_file
from boggler.board_randomizer import read_dice_file, get_random_board
from requests import get
from celery_worker import cel

MIN_BOARD_SIZE = 2
MAX_BOARD_SIZE = 10
MIN_WORD_LEN = 3
MAX_WORD_LEN = 20

# Initialize DICE for random board generation
DICE = {}
try:
    with ILR.path("boggler.dice", "4x4_classic.csv") as f:
        DICE["classic"] = read_dice_file(f)
except FileNotFoundError:
    print("Unable to load '4x4_classic.csv' DICE file")

try:
    with ILR.path("boggler.dice", "4x4_new.csv") as f:
        DICE["new"] = read_dice_file(f)
except FileNotFoundError:
    print("Unable to load '4x4_new.csv' DICE file")

try:
    with ILR.path("boggler.dice", "5x5_big.csv") as f:
        DICE["big"] = read_dice_file(f)
        for r in DICE["big"]:
            print(r)
except FileNotFoundError:
    print("Unable to load '5x5_big.csv' DICE file")

try:
    with ILR.path("boggler.dice", "6x6_super_big.csv") as f:
        DICE["super"] = read_dice_file(f)
except FileNotFoundError:
    print("Unable to load '6x6_super_big.csv' DICE file")


bp = Blueprint('board', __name__, url_prefix='/board', static_folder='static')

def parse_board_params(rows, cols, letters, dictionary=None, max_len=None):
    """Returns tuple of parsed parameters defining a Board

    Returns
        (board_letters, rows, cols, dictionary_path, max_len)
    """
    # Default size of board is 4x4
    try: # Default row count
        rows = int(rows)
        rows = min(rows, MAX_BOARD_SIZE)
        rows = max(rows, MIN_BOARD_SIZE)
    except (TypeError, ValueError):
        rows = 4
    try: # Default column count
        cols = int(cols)
        cols = min(cols, MAX_BOARD_SIZE)
        cols = max(cols, MIN_BOARD_SIZE)
    except (TypeError, ValueError):
        cols = 4

    # Default empty board and listify letters
    if letters is None:
        letters = []
    else:
        letters = letters.split(',')
        letters.extend((rows * cols - len(letters)) * [""])

    # Limit blocks to max of 2 letters
    letters = list(map(lambda x: x[:2] if len(x) >= 2 else x, letters))

    # Remove whitespace
    letters = [letter.strip() for letter in letters]

    # Lowercase
    letters = [x.lower() for x in letters]

    # 2D listify letters
    board_letters = []
    for row in range(0,rows):
        offset = row * cols
        board_letters.append(letters[offset:offset+cols])

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

def find_paths_by_word(board_letters, dictionary_path, max_len):
    """Return list of paths by word
    """
    boggle_board = BoggleBoard(board_letters, max_len)
    boggle_tree = build_full_boggle_tree(boggle_board, dictionary_path)
    paths_by_word = functools.reduce(operator.iconcat, [x.word_paths for x in boggle_tree.values()], [])
    return paths_by_word

@bp.route('/', methods=['GET', 'POST'])
def board():
    """Default board route
    """
    if request.form:
        print(request.form)

    if request.method == "GET":
        rows = cols = 4
        (board_letters, rows, cols, _, max_len) = parse_board_params(rows, cols, None)
        return render_template('pages/solver.html', board_letters=board_letters, rows=rows, cols=cols)
    elif request.method == "POST":
        rows = cols = request.form["sizeSelect"]
        letters = request.form["letters"]
        dictionary = request.form["dictionarySelect"]
        max_len = request.form["maxLengthSelect"]

        session["rows"] = rows
        session["cols"] = cols
        session["letters"] = letters
        session["dictionary"] = dictionary
        session["max_len"] = max_len
        return redirect(url_for("board.solve"))

@bp.route('/api/random', methods=['GET'])
def api_random():
    """API endpoing to get a random board 
    """
    # Default letter distribution for board sizes without dice
    alphabet = ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'c',
        'd', 'd', 'd', 'd', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'f', 'f',
        'g', 'g', 'g', 'h', 'h', 'h', 'i', 'i', 'i', 'i', 'i', 'i', 'i', 'j', 'k', 'k',
        'l', 'l', 'l', 'l', 'l', 'm', 'm', 'm', 'n', 'n', 'n', 'n', 'n', 'o', 'o', 'o',
        'o', 'o', 'o', 'p', 'p', 'p', 'qu', 'r', 'r', 'r', 'r', 's', 's', 's', 's', 's',
        't', 't', 't', 't', 't', 'u', 'u', 'u', 'u', 'v', 'v', 'w', 'w', 'x', 'y', 'y',
        'y', 'z']
    try:
        size = int(request.args.get("size"))
    except TypeError:
        size = 4

    dice_type = request.args.get("dice_type")
    if dice_type in DICE and size == int(sqrt(len(DICE[dice_type]))):
        return {
            "board": get_random_board(DICE[dice_type]),
            "dice_type": dice_type
        }
    else:
        return {
            "board": [choices(alphabet, k=size) for x in range(0, size)],
            "dice_type": "random",
        }

@bp.route('/api/solve', methods=['GET'])
def api_solve():
    """API endpoint for solving boards with the provided GET parameters

    Returns JSON containing board state and found words
    """
    rows = request.args.get("rows")
    cols = request.args.get("cols")
    letters = request.args.get("letters")
    dictionary = request.args.get("dictionary")
    max_len = request.args.get("max_len")
    (board_letters, rows, cols, dictionary_path, max_len) = parse_board_params(rows, cols, letters, dictionary, max_len)
    is_db = False
    if is_db:
        # TODO: Read from db
        pass
    else:
        word_data = find_paths_by_word(board_letters, dictionary_path, max_len)
        word_data = [{
            'word': word,
            'len': len(word),
            'path': [{
                'row': node[0],
                'col': node[1],
            } for node in path]
        } for word, path in word_data]
        return {
            'words': word_data,
            'total': len(word_data),
            'max_len': max_len,
            'dictionary': os.path.basename(os.path.normpath(dictionary_path)),
            'size': {
                'rows': rows,
                'cols': cols,
            }
        }

@bp.route('/api/solve/table', methods=['GET'])
def api_solve_words():
    """API endpoint for data displayed in solved board table

    Returns only displayed table data (word, len, path) for a given board
    """
    args = request.args
    rows = request.args.get("rows")
    cols = request.args.get("cols")
    letters = request.args.get("letters")
    dictionary = request.args.get("dictionary")
    max_len = request.args.get("max_len")
    (board_letters, rows, cols, dictionary_path, max_len) = parse_board_params(rows, cols, letters, dictionary, max_len)
    is_db = False
    if is_db:
        # TODO: Read from db
        pass
    else:
        word_data = find_paths_by_word(board_letters, dictionary_path, max_len)
        word_data = [{
            'word': word,
            'len': len(word),
            'path': str(path),
        } for word, path in word_data]
        return word_data

@cel.task()
def find_paths_by_word_async(rows, cols, letters, board_letters, dictionary_path, max_len):
    """Celery Task for asynchronously finding words in board
    """
    found_words = find_paths_by_word(board_letters, dictionary_path, max_len)
    return [
        rows,
        cols,
        letters,
        board_letters,
        dictionary_path,
        max_len,
        found_words
    ]

@bp.route('/solve/task', methods=["POST"])
def task_submit():
    """Endpoint to submit board solving tasks
    """
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        json = request.json
        (board_letters, _rows, _cols, dictionary_path, max_len) = parse_board_params(
            json["rows"], json["cols"], json["letters"], json["dictionary"], json["max_len"]
        )

        task = find_paths_by_word_async.apply_async(args=[
            json["rows"], json["cols"], json["letters"], board_letters, dictionary_path, max_len
        ])
        return {
            "status_url": url_for("board.task_status", task_id=task.id),
            "task_id": task.id,
        }
    else:
        print("INVALID Content-Type. Please try again.")
        return {"status:": f"INVALID Content-Type: {content_type}"}

@bp.route('/solved/<task_id>', methods=['GET'])
def solved(task_id):
    """Endpoints for solved boards by task ID
    """

    headers = {
        "Content-Type": "application/json",
    }
    data = get(f"http://localhost:5000/board/solved/task/data/{task_id}", headers=headers, timeout=2.0).json()
    return render_template('pages/solved.html',
        letters=data["letters"],
        board_letters=data["board_letters"],
        rows=int(data["rows"]),
        cols=int(data["cols"]),
        dictionary=data["dictionary_path"],
        max_len=data["max_len"],
        found_words=data["found_words"],
    )


@bp.route('/solved/task/status/<task_id>')
def task_status(task_id):
    """Endpoint for board solve statuses by task ID
    """
    task = find_paths_by_word_async.AsyncResult(task_id)
    if task.status == "FAILURE":
        response = {
            "status": task.status,
            "info": str(task.info),
        }
    elif task.status != "SUCCESS":
        # Task is only STARTED, PENDING or RETRYing
        response = {
            "status": task.status,
        }
    else:
        # SUCCESS!
        response = {
            "status": task.status,
        }

    return response

@bp.route('/solved/task/data/<task_id>')
def task_data(task_id):
    """Endpoint for board solve data
    """
    task = find_paths_by_word_async.AsyncResult(task_id)
    if task.status == "FAILURE":
        response = {
            "status": task.status,
            "info": str(task.info),
        }
    elif task.status != "SUCCESS":
        # Task is only STARTED, PENDING or RETRYing
        response = {
            "status": task.status,
            "info": str(task.info),
        }
    else:
        # SUCCESS!
        response = {
            "rows": int(task.result[0]),
            "cols": int(task.result[1]),
            "letters": task.result[2],
            "board_letters": task.result[3],
            "dictionary_path": task.result[4],
            "max_len": task.result[5],
            "found_words": task.result[6],
        }
    
    return response
