DROP TABLE IF EXISTS corpus_versions;
DROP TABLE IF EXISTS solved_words;
DROP TABLE IF EXISTS dictionary_words;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS solved_boards;
DROP TABLE IF EXISTS dictionaries;

PRAGMA foreign_keys = ON;

CREATE TABLE dictionaries (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    UNIQUE(name, description)
);

-- Tracks versioning of dictionaries and all their words (corpus), so
-- boards can be solved on the entire word set but also indicate
-- if it has been solved on an old version of the corpus
CREATE TABLE corpus_versions (
    id INTEGER NOT NULL PRIMARY KEY,
    -- What changed and why
    description TEXT NOT NULL,
    -- type = Type of change
    -- INIT = initial schema setup
    -- ADD = additive like new words and dictionaries
    -- DEL = deletions like removing typos or invalid words
    -- MIX = updates to fix typos or combination of ADD & DEL to fix a single issue
    type TEXT CHECK( type IN ('INIT', 'ADD','DEL','MIX') ) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE solved_boards (
    id INTEGER PRIMARY KEY NOT NULL,
    hash TEXT CHECK(length(hash) == 32) UNIQUE NOT NULL,
    rows INTEGER CHECK (rows >= 3 AND rows <= 10) NOT NULL,
    cols INTEGER CHECK (cols >= 3 AND cols <= 10 AND cols = rows) NOT NULL,
    letters TEXT NOT NULL, -- JSON array of letters
    created DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cv_id INTEGER NOT NULL REFERENCES corpus_versions(id) ON DELETE CASCADE,
    UNIQUE(rows, cols, letters)
);

CREATE INDEX sb_hash_idx ON solved_boards (hash);

CREATE TABLE words (
    id INTEGER PRIMARY KEY NOT NULL,
    word TEXT COLLATE NOCASE NOT NULL,
    UNIQUE(word)
);

CREATE TABLE dictionary_words (
    id INTEGER PRIMARY KEY NOT NULL,
    dict_id INTEGER NOT NULL REFERENCES dictionaries(id) ON DELETE CASCADE,
    word_id INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    UNIQUE(dict_id, word_id)
);

CREATE INDEX dw_idx ON dictionary_words (word_id);

CREATE TABLE solved_words (
    solved_board_id INTEGER NOT NULL REFERENCES solved_boards(id) ON DELETE CASCADE,
    word_id INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    word_path TEXT NOT NULL, -- JSON array of board indices
    PRIMARY KEY (word_id, solved_board_id, word_path)
);

CREATE INDEX sw_word_idx ON solved_words (word_id);
CREATE INDEX sw_sboard_idx ON solved_words (solved_board_id);

INSERT INTO dictionaries (name, display_name, description)
VALUES
    ('dwyl', 'dwyl', 'The dwyl (Do What You Love) open source English wordlist. See https://github.com/dwyl/english-words for details.'),
    ('free_scrabble', 'Free Scrabble Dictionary', 'The English wordlist provided by https://www.freescrabbledictionary.com/english-word-list/.'),
    ('scrabble_2019', 'Scrabble 2019', "A wordlist based off the Collins official Scrabble dictionary (2019)"),
    ('sowpods', 'sowpods', 'A European English word list also provided by freescrabbledictionary.com at https://www.freescrabbledictionary.com/twl06/.'),
    ('twl06', 'Scrabble Tournament List (2006)', 'The official Scrabble Tournament word list from 2006'),
    ('wordnik_2021_07_29', 'Wordnik (2021/07/29)', 'A wordlist based off the Wordnik online dictionary. See https://www.wordnik.com for the official online dictionary.');
	
INSERT INTO corpus_versions (description, type)
VALUES
    ("Database initialization", "INIT")