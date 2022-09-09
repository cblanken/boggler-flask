import functools

from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('board', __name__, url_prefix='/board')

@bp.route('/')
def root():
    # Default empty board is 4x4
    return render_template('board.html', letters=[], rows=4, cols=4)

@bp.route('/solve', methods=('GET', 'POST'))
def solve():
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

    if letters is None:
        letters = "" 

    # Fill letters to fit board size
    letters = letters.split(",")
    letters = list(map(lambda x: x[:2] if len(x) >= 2 else x, letters))
    letters.extend("" * (rows * cols - len(letters)))

    return render_template('board.html', letters=letters, rows=rows, cols=cols)