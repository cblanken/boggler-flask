import sqlite3
import sys
from pathlib import Path
import re

VALID_WORD = re.compile(r"^[a-zA-Z]{3,}$")


def load_dictionary(words_file: Path, db_file: Path, dict_name: str):
    conn = sqlite3.connect(db_file)
    curr = conn.cursor()

    with open(words_file, encoding="utf-8") as f:
        max_chunk_size = 20_000
        chunk_i = 0

        dict_id_query = curr.execute(
            f"SELECT id FROM dictionaries WHERE name='{dict_name}'"
        )

        try:
            dict_id = dict_id_query.fetchone()[0]
        except IndexError:
            print(f'No dictionary with the name "{dict_name}" found in the database.')
            return

        # TODO: filter words with numbers or punctuation

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

            if last_line:
                break

            # Chunk file in case the dictionary is very large and could result in OOM errors
            chunk_i += 1
            # word_values = ",".join([f"({dict_id}, '{w}')" for w in words])
            word_values = [(dict_id, w) for w in words]
            curr.executemany(
                "INSERT INTO words (dict_id, word) VALUES(?, ?)", word_values
            )
            print(f"> COMMITTING CHUNK: {chunk_i}")
            conn.commit()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        resp = input("Load all predefined dictionaries? (y/n): ")
        db_path = Path(sys.argv[1].strip())
        if re.match(r"^[Yy]$", resp):
            load_dictionary(
                Path("../../wordlists/dwyl/words_alpha.txt"),
                db_path,
                "dwyl",
            )
            load_dictionary(
                Path("../../wordlists/sowpods/sowpods.txt"),
                db_path,
                "sowpods",
            )
            load_dictionary(
                Path("../../wordlists/na_english/NA_english.txt"),
                db_path,
                "na_english",
            )
            load_dictionary(
                Path("../../wordlists/scrabble_2019/words_alpha.txt"),
                db_path,
                "scrabble_2019",
            )
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
