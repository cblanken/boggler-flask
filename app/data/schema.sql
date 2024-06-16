DROP TABLE IF EXISTS solved_boards;
DROP TABLE IF EXISTS dictionaries;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS solved_board_words;

PRAGMA foreign_keys = ON;

CREATE TABLE dictionaries (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    UNIQUE(name, description)
);

CREATE TABLE solved_boards (
    id INT PRIMARY KEY,
    rows INT CHECK (rows >= 3 AND rows <= 10) NOT NULL,
    cols INT CHECK (cols >= 3 AND cols <= 10 AND cols = rows) NOT NULL,
    letters TEXT NOT NULL, -- JSON array of letters
    dict_id INT REFERENCES dictionaries(id) ON DELETE CASCADE,
    max_word_len INT CHECK (max_word_len <= rows * cols) NOT NULL,
    UNIQUE(rows, cols, letters, dict_id, max_word_len)
);

CREATE TABLE words (
    id INT PRIMARY KEY,
    dict_id INT REFERENCES dictionaries(id) ON DELETE CASCADE,
    word TEXT NOT NULL,
    UNIQUE(dict_id, word)
);

CREATE TABLE solved_board_words (
    word_id INT REFERENCES words(id) NOT NULL,
    solved_board_id INT REFERENCES solved_boards(id) ON DELETE CASCADE,
    word_path TEXT NOT NULL,
    PRIMARY KEY (word_id, solved_board_id)
);

INSERT INTO dictionaries (name, description)
VALUES
    ('dwyl', 'dwyl Dictionary'),
    ('na_english', 'NA English'),
    ('scrabble_2019', 'scrabble 2019'),
    ('sowpods', 'sowpods');
	
