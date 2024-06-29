import sqlite3
import json
from hashlib import md5
from typing import List
from boggler.boggler_utils import WordNode


def get_solved_boards(conn: sqlite3.Connection) -> tuple:
    curr = conn.cursor()
    sql = """SELECT hash, created, letters, rows, cols, COUNT(*)
        FROM solved_boards as sb
        INNER JOIN solved_words as sw ON sw.solved_board_id = sb.id
        GROUP BY sb.id"""

    return curr.execute(sql).fetchall()


def get_solved_board_by_hash(conn: sqlite3.Connection, hash: str) -> dict | None:
    curr = conn.cursor()
    sql = """SELECT sb.id, sb.rows, sb.cols, sb.letters, sb.created FROM solved_boards as sb
        WHERE sb.hash = ?"""
    board = curr.execute(sql, (hash,)).fetchone()
    if board is None:
        return None

    sql = """SELECT word, word_path, string_agg(dict_id, ',')
        FROM solved_boards as sb
        INNER JOIN solved_words as sw ON sw.solved_board_id = sb.id
        INNER JOIN dictionary_words as dw ON dw.word_id = sw.word_id
        INNER JOIN words as wo ON wo.id = sw.word_id
        WHERE sb.id = ?
        GROUP BY sw.word_path
        ORDER BY word
        """

    words = curr.execute(sql, (board[0],)).fetchall()
    return {
        "words": words if len(words) != 0 else None,
        "rows": board[1],
        "cols": board[2],
        "letters": board[3],
        "created": board[4],
    }


def get_solved_board_by_letters(
    conn: sqlite3.Connection,
    letters: List[str],
) -> List[str] | None:
    curr = conn.cursor()

    sql = """SELECT sb.id FROM solved_boards as sb
    WHERE sb.letters = ?"""

    solved_board_id = curr.execute(sql, (json.dumps(letters),)).fetchone()
    if solved_board_id is None:
        return None

    sql = """SELECT word, word_path, string_agg(dict_id, ',')
        FROM solved_boards as sb
        INNER JOIN solved_words as sw ON sw.solved_board_id = sb.id
        INNER JOIN dictionary_words as dw ON dw.word_id = sw.word_id
        INNER JOIN words as wo ON wo.id = sw.word_id
        WHERE sb.hash = ?
        GROUP BY sw.word_path
        ORDER BY word
        """

    words = curr.execute(sql, (solved_board_id[0],)).fetchall()

    return words if len(words) != 0 else None


def get_dictionaries(conn: sqlite3.Connection) -> List[str] | None:
    curr = conn.cursor()
    return curr.execute(
        """SELECT id, name, display_name, description FROM dictionaries"""
    ).fetchall()


def get_words(conn: sqlite3.Connection, prefix: str | None = None) -> List[str] | None:
    curr = conn.cursor()

    if prefix:
        sql = """SELECT word FROM words WHERE word LIKE ?"""
        recs = curr.execute(sql, (f"{prefix}%",)).fetchall()
    else:
        sql = """SELECT word FROM words"""
        recs = curr.execute(sql).fetchall()

    return [r[0] for r in recs]


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
    return md5(
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
            """INSERT INTO solved_boards(hash, rows, cols, letters) VALUES(?, ?, ?, ?)""",
            (
                make_board_hash(letters, dict_name),
                size,
                size,
                json.dumps(letters),
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
