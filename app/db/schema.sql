DROP TABLE IF EXISTS solved_words;
DROP TABLE IF EXISTS solved_boards;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS dictionaries;

PRAGMA foreign_keys = ON;

CREATE TABLE dictionaries (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    UNIQUE(name, description)
);

CREATE TABLE solved_boards (
    id INTEGER PRIMARY KEY NOT NULL,
    rows INTEGER CHECK (rows >= 3 AND rows <= 10) NOT NULL,
    cols INTEGER CHECK (cols >= 3 AND cols <= 10 AND cols = rows) NOT NULL,
    letters TEXT NOT NULL, -- JSON array of letters
    dict_id INTEGER NOT NULL REFERENCES dictionaries(id) ON DELETE CASCADE,
    max_word_len INTEGER CHECK (max_word_len <= rows * cols) NOT NULL,
    UNIQUE(rows, cols, letters, dict_id, max_word_len)
);

CREATE TABLE words (
    id INTEGER PRIMARY KEY NOT NULL,
    dict_id INTEGER NOT NULL REFERENCES dictionaries(id) ON DELETE CASCADE,
    word TEXT NOT NULL,
    UNIQUE(dict_id, word)
);

CREATE TABLE solved_words (
    word_id INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    solved_board_id INTEGER NOT NULL REFERENCES solved_boards(id) ON DELETE CASCADE,
    word_path TEXT NOT NULL, -- JSON array of board indices
    PRIMARY KEY (word_id, solved_board_id, word_path)
);

-- TODO: CREATE INDEXES

INSERT INTO dictionaries (name, description)
VALUES
    ('dwyl', 'dwyl Dictionary'),
    ('na_english', 'NA English'),
    ('scrabble_2019', 'Scrabble 2019'),
    ('sowpods', 'sowpods'),
    ('twl06', 'Scrabble Tournament List 2006'),
    ('wordnik_2021_07_29', 'Wordnik (2021/07/29)');
	
