import functools
import operator

from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('board', __name__, url_prefix='/board')

def parse_board_params():
    args = request.args
    rows = args.get("rows")
    cols = args.get("cols")
    letters = args.get("letters")

    # Default size of board is 4x4
    if rows is None or cols is None:
        rows = 4
        cols = 4
    else:
        rows = int(rows)
        cols = int(cols)

    # Default empty board
    if letters is None:
        letters = "" 

    letters = letters.split(',')

    # Limit blocks to max of 2 letters
    letters = list(map(lambda x: x[:2] if len(x) >= 2 else x, letters))

    # Fill letters to fit board size
    letters.extend("_" * (rows * cols - len(letters)))

    board_letters = []
    for row in range(0,rows):
        offset = row * cols
        board_letters.append(letters[offset:offset+cols])

    return (board_letters, rows, cols)

@bp.route('/', methods=('GET', 'POST'))
def board():
    (board_letters, rows, cols) = parse_board_params()
    return render_template('components/board.html', board_letters=board_letters, rows=rows, cols=cols)

@bp.route('/solve', methods=('GET', 'POST'))
def solve():
    from boggler.boggler_utils import BoggleBoard, build_full_boggle_tree, read_boggle_file

    (board_letters, rows, cols) = parse_board_params()
    max_depth = request.args.get("max_depth")
    if max_depth is None:
        max_depth = 14
    else:
        max_depth = int(max_depth)

    try :
        boggle_board = BoggleBoard(board_letters, max_depth)
        boggle_tree = build_full_boggle_tree(boggle_board, 'static/wordlists/dwyl')

        found_paths_by_word = functools.reduce(operator.iconcat, [x.word_paths for x in boggle_tree.values()], [])

    except ValueError as e:
        print("The [MAX_WORD_LENGTH] argument must be an integer.")
        print("Please try again.")

    return render_template('solved.html', board_letters=board_letters, rows=rows, cols=cols, found_words=found_paths_by_word)
    # return render_template('components/words_table.html', found_words=found_paths_by_word)
    # return render_template('components/board.html', board_letters=board_letters, rows=rows, cols=cols)
