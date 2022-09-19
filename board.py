import functools
import operator
import os

from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('board', __name__, url_prefix='/board')

def parse_board_params(rows, cols, letters):
    # Default size of board is 4x4
    try:
        rows = int(rows)
    except:
        rows = 4
    try:
        cols = int(cols)
    except:
        cols = 4

    # Default empty board
    if letters is None:
        letters = "_" 

    letters = letters.split(',')

    # Remove whitespace
    letters = [letter.strip() for letter in letters]

    # Replace blanks
    letters = list(map(lambda x: "_" if len(x) == 0 else x, letters))

    # Limit blocks to max of 2 letters
    letters = list(map(lambda x: x[:2] if len(x) >= 2 else x, letters))

    # Lowercase
    letters = [x.lower() for x in letters]

    # Fill letters to fit board size
    letters.extend("_" * (rows * cols - len(letters)))

    board_letters = []
    for row in range(0,rows):
        offset = row * cols
        board_letters.append(letters[offset:offset+cols])

    return (board_letters, rows, cols)

def find_paths_by_word(board_letters, rows, cols):
    from boggler.boggler_utils import BoggleBoard, build_full_boggle_tree, read_boggle_file

    max_depth = request.args.get("max_depth")
    if max_depth is None:
        max_depth = 14
    else:
        max_depth = int(max_depth)

    boggle_board = BoggleBoard(board_letters, max_depth)
    boggle_tree = build_full_boggle_tree(boggle_board, 'static/wordlists/scrabble_2019')
    paths_by_word = functools.reduce(operator.iconcat, [x.word_paths for x in boggle_tree.values()], [])
    return paths_by_word

@bp.route('/', methods=['GET', 'POST'])
def board():
    if request.form:
        print(request.form)

    if request.method == "GET":
        rows = cols = 4
        board_letters = " " * rows * cols
        return render_template('solver.html', board_letters=board_letters, rows=rows, cols=cols)
    elif request.method == "POST":
        rows = cols = request.form["sizeSelect"]
        letters = request.form["letters"]

        session["rows"] = rows
        session["cols"] = cols
        session["letters"] = letters
        return redirect(url_for("board.solve"))

@bp.route('/api', methods=['GET'])
def api():
    # TODO: add DB
    is_db = False
    if is_db:
        # Read from db
        pass
    else:
        (board_letters, rows, cols) = parse_board_params()
        word_data = find_paths_by_word(board_letters, rows, cols)
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
            'total': len(word_data)
        }

@bp.route('/solve', methods=['GET'])
def solve():
    if request.method == "GET":
        print("GET")
        args = request.args
        if args.get("rows") or args.get("cols") or args.get("letters"):
            rows = request.args.get("rows")
            cols = request.args.get("cols")
            letters = request.args.get("letters")
        else:
            rows = session.get("rows")
            cols = session.get("cols")
            letters = session.get("letters")

    (board_letters, rows, cols) = parse_board_params(rows, cols, letters)
    print(rows)
    print(cols)
    print(board_letters)
    found_paths_by_word = find_paths_by_word(board_letters, rows, cols)

    return render_template('solved.html', board_letters=board_letters, rows=rows, cols=cols, found_words=found_paths_by_word)