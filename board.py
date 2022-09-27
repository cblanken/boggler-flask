import functools
import operator
import os
from random import choices
from boggler.boggler_utils import BoggleBoard, build_full_boggle_tree, read_boggle_file
from boggler.board_randomizer import read_dice_file, get_random_board
import importlib.resources as ILR

MIN_BOARD_SIZE = 2
MAX_BOARD_SIZE = 10
MIN_WORD_LEN = 3
MAX_WORD_LEN = 20

# Initialize DICE for random board generation
DICE = {}
with ILR.path("boggler.dice", "4x4_classic.csv") as f:
    DICE["classic"] = read_dice_file(f)
with ILR.path("boggler.dice", "4x4_new.csv") as f:
    DICE["new"] = read_dice_file(f)
with ILR.path("boggler.dice", "6x6_super_big.csv") as f:
    DICE["super"] = read_dice_file(f)

from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('board', __name__, url_prefix='/board')

def parse_board_params(rows, cols, letters, dictionary=None, max_len=None):
    # Default size of board is 4x4
    try: # Default row count
        rows = int(rows)
        rows = min(rows, MAX_BOARD_SIZE)
        rows = max(rows, MIN_BOARD_SIZE)
    except:
        rows = 4
    try: # Default column count
        cols = int(cols)
        cols = min(cols, MAX_BOARD_SIZE)
        cols = max(cols, MIN_BOARD_SIZE)
    except:
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
    dictionary_path = url_for("static", filename=f"wordlists/{dictionary}").strip(os.sep)
    if not os.path.exists(dictionary_path) or dictionary is None:
        dictionary_path = url_for("static", filename=f"wordlists/wordnik_2021_07_29").strip(os.sep)
        print(f"Defaulting to {dictionary_path}")

    # Default maximum word length
    try:
        max_len = int(max_len)
        max_len = min(max_len, MAX_WORD_LEN)
        max_len = max(max_len, MIN_WORD_LEN)
    except:
        max_len = 16

    return (board_letters, rows, cols, dictionary_path, max_len)

def find_paths_by_word(board_letters, rows, cols, dictionary_path, max_len):

    boggle_board = BoggleBoard(board_letters, max_len)
    
    boggle_tree = build_full_boggle_tree(boggle_board, dictionary_path)

    paths_by_word = functools.reduce(operator.iconcat, [x.word_paths for x in boggle_tree.values()], [])
    return paths_by_word

@bp.route('/', methods=['GET', 'POST'])
def board():
    if request.form:
        print(request.form)

    if request.method == "GET":
        rows = cols = 4
        (board_letters, rows, cols, dictionary_path, max_len) = parse_board_params(rows, cols, None)
        return render_template('solver.html', board_letters=board_letters, rows=rows, cols=cols)
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
    # Default letter distribution for board sizes without 
    alphabet = ["a", "a", "a", "a", "a", "a", "a", "a", "b", "b", "b", "c", "c", "c", "d", "d", "d", "d", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "f", "f", "g", "g", "g", "h", "h", "h", "i", "i", "i", "i", "i", "i", "i", "j", "k", "k", "l", "l", "l", "l", "l", "m", "m", "m", "n", "n", "n", "n", "n", "o", "o", "o", "o", "o", "o", "p", "p", "p", "qu", "r", "r", "r", "r", "s", "s", "s", "s", "s", "t", "t", "t", "t", "t", "u", "u", "u", "u", "v", "v", "w", "w", "x", "y", "y", "y", "z"]
    try:
        size = int(request.args.get("size"))
    except:
        size = 4
    
    dice_type = request.args.get("dice_type")
    if dice_type in DICE and size * size == len(DICE[dice_type]):
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
        word_data = find_paths_by_word(board_letters, rows, cols, dictionary_path, max_len)
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
        word_data = find_paths_by_word(board_letters, rows, cols, dictionary_path, max_len)
        word_data = [{
            'word': word,
            'len': len(word),
            'path': str(path),
        } for word, path in word_data]
        return word_data

@bp.route('/solve', methods=['GET'])
def solve():
    args = request.args
    if args.get("rows") or args.get("cols") or args.get("letters"):
        rows = request.args.get("rows")
        cols = request.args.get("cols")
        letters = request.args.get("letters")
        dictionary = request.args.get("dictionary")
        max_len = request.args.get("max_len")
    else:
        rows = session.get("rows")
        cols = session.get("cols")
        letters = session.get("letters")
        dictionary = session.get("dictionary")
        max_len = session.get("max_len")


    (board_letters, rows, cols, dictionary_path, max_len) = parse_board_params(rows, cols, letters, dictionary, max_len)

    # Replace empty strings
    found_paths_by_word = find_paths_by_word(board_letters, rows, cols, dictionary_path, max_len)

    return render_template('solved.html', letters=letters, board_letters=board_letters, rows=rows, cols=cols, dictionary=dictionary, max_len=max_len, found_words=found_paths_by_word)