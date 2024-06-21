import sqlite3
import sys
from pathlib import Path
import re
import time

VALID_WORD = re.compile(r"^[a-zA-Z]{3,}$")


def load_dictionary(words_file: Path, conn: sqlite3.Connection | None, dict_name: str):
    if conn is None:
        # TODO: log
        return

    curr = conn.cursor()

    with open(words_file, encoding="utf-8") as f:
        max_chunk_size = 100_000
        chunk_i = 0

        dict_id_query = curr.execute(
            f"SELECT id FROM dictionaries WHERE name='{dict_name}'"
        )

        try:
            dict_id = dict_id_query.fetchone()[0]
        except (TypeError, IndexError):
            print(f'No dictionary with the name "{dict_name}" found in the database.')
            return

        print(f"\nDictionary: {dict_name}")
        while True:
            words = []
            last_line = False
            for i in range(0, max_chunk_size):
                line = f.readline()
                if line == "":
                    last_line = True
                    break

                word = line.strip()
                if VALID_WORD.match(word):
                    words.append(word)

            # Chunk file in case the dictionary is very large and could result in OOM errors
            chunk_i += 1
            # Insert words
            print(f"> COMMITTING WORDS CHUNK: {chunk_i}")
            curr.executemany(
                "INSERT OR IGNORE INTO words (word) VALUES(?)", [(w,) for w in words]
            )
            conn.commit()

            word_values = [(dict_id, w) for w in words]

            # Link dictionary and words
            print("  > LINKING WORDS TO DICTIONARY")
            curr.executemany(
                """INSERT INTO dictionary_words (dict_id, word_id) VALUES(?, (
                        SELECT id FROM words WHERE word = ?
                    )
                )""",
                word_values,
            )
            conn.commit()

            if last_line:
                break


def load_default_dictionaries(conn: sqlite3.Connection | None):
    if conn is None:
        # TODO: log
        return
    start = time.time()
    curr_dir = Path(__file__).parent
    load_dictionary(
        Path(curr_dir, "../../wordlists/dwyl/words_alpha.txt"),
        conn,
        "dwyl",
    )
    load_dictionary(
        Path(curr_dir, "../../wordlists/na_english/NA_english.txt"),
        conn,
        "na_english",
    )
    load_dictionary(
        Path(curr_dir, "../../wordlists/scrabble_2019/words_alpha.txt"),
        conn,
        "scrabble_2019",
    )
    load_dictionary(
        Path(curr_dir, "../../wordlists/sowpods/sowpods.txt"),
        conn,
        "sowpods",
    )
    load_dictionary(
        Path(curr_dir, "../../wordlists/twl06/twl06.txt"),
        conn,
        "twl06",
    )
    load_dictionary(
        Path(curr_dir, "../../wordlists/wordnik_2021_07_29/wordnik.txt"),
        conn,
        "wordnik_2021_07_29",
    )
    end = time.time()
    print(f"Loaded all dictionaries into database in {(end - start):.4f} seconds\n")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        resp = input("Load all predefined dictionaries? (y/n): ")
        db_path = Path(sys.argv[1].strip())
        if re.match(r"^[Yy]$", resp):
            load_default_dictionaries(db_path)
    elif len(sys.argv) == 4:
        load_dictionary(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].strip())
    else:
        print("Load one dictionary file:")
        print(
            "Usage: python load_dictionary.py <dictionary_file_path.txt> <sqlite_db.sqlite> <dictionary_name>"
        )
        print(
            "The <dictionary_name> must match the dictionary name in the `dictionaries` table."
        )

        print()
        print("Load all predefined dictionaries:")
        print("Usage: python load_dictionary.py <sqlite_db.sqlite>")
        sys.exit(0)
