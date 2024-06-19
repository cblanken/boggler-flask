import sqlite3
import json
from typing import List
from boggler.boggler_utils import WordNode


def get_dict_names(conn: sqlite3.Connection) -> List[str]:
    curr = conn.cursor()
    names = curr.execute("""SELECT name FROM dictionaries""").fetchall()
    return [n[0] for n in names]


def get_words_by_dict(conn: sqlite3.Connection, dict_name: str) -> List[str]:
    curr = conn.cursor()
    recs = curr.execute(
        """SELECT word FROM words
        INNER JOIN dictionaries as di ON di.name = ?""",
        (dict_name,),
    ).fetchall()
    return [r[0] for r in recs]


def add_solved_board(
    conn: sqlite3.Connection,
    size: int,
    letters: List[str],
    dict_name: str,
    max_word_len: int,
    word_data: List[dict[str, WordNode]],
):
    try:
        curr = conn.cursor()
        # TODO: check for existing solved board and return

        # TODO: setup SAVEPOINTS for proper rollbacks
        curr.execute(
            """INSERT INTO solved_boards(rows, cols, letters, dict_id, max_word_len) VALUES(?, ?, ?, (
                SELECT id FROM dictionaries WHERE name = ? LIMIT 1
            ), ?)""",
            (size, size, json.dumps(letters), dict_name, max_word_len),
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

        dict_id = curr.execute(
            "SELECT id FROM dictionaries WHERE name = ?", (dict_name,)
        ).fetchone()[0]

        word_inserts = [
            (
                solved_board_id,
                f"[{','.join(str([x[0], x[1]]) for x in path)}]",
                word,
                dict_id,
            )
            for word, path in word_data
        ]
        conn.executemany(
            """
            INSERT INTO solved_words(solved_board_id, word_path, word_id) 
            SELECT ?, ?, id FROM (SELECT id FROM words WHERE word = ? AND dict_id = ?)
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
