import functools

from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('board', __name__, url_prefix='/board')

@bp.route('/')
def empty():
    return render_template('board.html')

@bp.route('/<letters>', methods=('GET', 'POST'))
def solve(letters):
    return render_template('board.html', letters=letters)