import sqlite3
import json
from hashlib import sha256
from typing import List
from boggler.boggler_utils import WordNode


def get_solved_boards(conn: sqlite3.Connection) -> tuple:
    curr = conn.cursor()
    sql = """SELECT hash, created, di.name, letters, rows, cols FROM solved_boards as sb
        INNER JOIN dictionaries as di ON sb.dict_id = di.id"""

    return curr.execute(sql).fetchall()


def get_solved_board_by_hash(conn: sqlite3.Connection, hash: str) -> dict | None:
    curr = conn.cursor()
    sql = """SELECT sb.id, sb.rows, sb.cols, sb.letters, di.name, sb.created FROM solved_boards as sb
        INNER JOIN dictionaries as di ON sb.dict_id = di.id
        WHERE sb.hash = ?"""
    board = curr.execute(sql, (hash,)).fetchone()
    if board is None:
        return None

    sql = """SELECT word, sw.word_path from words
        INNER JOIN solved_words as sw ON sw.word_id = words.id
        WHERE sw.solved_board_id = ?"""

    words = curr.execute(sql, (board[0],)).fetchall()
    return {
        "words": words if len(words) != 0 else None,
        "rows": board[1],
        "cols": board[2],
        "letters": board[3],
        "dictionary": board[4],
        "created": board[5],
    }


def get_solved_board_words(
    conn: sqlite3.Connection,
    letters: List[str],
    dict_name: str,
    max_word_len: int,
) -> List[str] | None:
    curr = conn.cursor()

    sql = """SELECT sb.id FROM solved_boards as sb
    INNER JOIN dictionaries as di ON di.id = sb.dict_id
    WHERE sb.letters = ? AND di.name = ?"""

    solved_board_id = curr.execute(sql, (json.dumps(letters), dict_name)).fetchone()
    if solved_board_id is None:
        return None

    sql = """SELECT word, sw.word_path from words
        INNER JOIN solved_words as sw ON sw.word_id = words.id
        WHERE sw.solved_board_id = ? AND length(word) <= ?"""

    words = curr.execute(sql, (solved_board_id[0], max_word_len)).fetchall()
    return words if len(words) != 0 else None


def get_dict_names(conn: sqlite3.Connection) -> List[str]:
    curr = conn.cursor()
    names = curr.execute("""SELECT name FROM dictionaries""").fetchall()
    return [n[0] for n in names]


def get_words_by_dict(
    conn: sqlite3.Connection, dict_name: str, prefix: str | None = None
) -> List[str]:
    curr = conn.cursor()

    if prefix:
        sql = """SELECT word FROM words
            INNER JOIN dictionary_words as dw ON words.id=dw.word_id
            INNER JOIN dictionaries as di ON di.name = ?
            WHERE word LIKE ?"""
        recs = curr.execute(sql, (dict_name, f"{prefix}%")).fetchall()
    else:
        sql = """SELECT word FROM words
            INNER JOIN dictionary_words as dw ON words.id=dw.word_id
            INNER JOIN dictionaries as di ON di.name = ?"""
        recs = curr.execute(sql, (dict_name,)).fetchall()

    return [r[0] for r in recs]


def make_board_hash(letters: List, dict_name: str) -> str:
    """Create unique solved board hash for permalinks"""
    return sha256(
        f"{letters}{dict_name}".encode("utf-8"), usedforsecurity=False
    ).hexdigest()


def add_solved_board(
    conn: sqlite3.Connection,
    size: int,
    letters: List[str],
    dict_name: str,
    word_data: List[dict[str, WordNode]],
):
    try:
        curr = conn.cursor()
        # TODO: setup SAVEPOINTS for proper rollbacks
        curr.execute(
            """INSERT INTO solved_boards(hash, rows, cols, letters, dict_id) VALUES(?, ?, ?, ?, (
                SELECT id FROM dictionaries WHERE name = ? LIMIT 1
            ))""",
            (
                make_board_hash(letters, dict_name),
                size,
                size,
                json.dumps(letters),
                dict_name,
            ),
        )

        conn.commit()

        if curr.lastrowid is None:
            print("Failed to insert new solved board. Rollowing back transaction.")
            conn.rollback()
            return

        try:
            solved_board_id = curr.execute(
                "SELECT id FROM solved_boards WHERE rowid = ?", (curr.lastrowid,)
            ).fetchone()[0]
        except IndexError:
            print(
                "Failed to retrieve id of newly solved board. Rolling back transaction."
            )
            conn.rollback()
            return

        word_inserts = [
            (
                solved_board_id,
                f"[{','.join(str([x[0], x[1]]) for x in path)}]",
                word,
            )
            for word, path in word_data
        ]
        conn.executemany(
            """
            INSERT INTO solved_words(solved_board_id, word_path, word_id) 
            SELECT ?, ?, id FROM (SELECT id FROM words WHERE word = ?)
            """,
            word_inserts,
        )

        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(
            f"No solved board was added since an integrity error ocurred. The dictionary for the given name '{dict_name}' probably doesn't exist."
        )
        raise e
    except Exception as e:
        conn.rollback()
        print(
            "An error occurred when adding a solved board to the database. Rolling back transaction.",
            e,
        )
        raise
