DROP TABLE IF EXISTS solved_boards;
DROP TABLE IF EXISTS dictionaries;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS solved_board_words;

CREATE TABLE dictionaries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    path_name VARCHAR(4096)
);

-- TODO add NOT NULL(s)
CREATE TABLE solved_boards (
    id INT PRIMARY KEY,
    rows INT CHECK (rows >= 3 AND rows <= 10),
    cols INT CHECK (cols >= 3 AND cols <= 10 AND cols = rows),
    letters varchar(256),
    dict_id INT references dictionaries(id),
    max_word_len INT CHECK (max_word_len <= rows * cols)
);

CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100)
);

CREATE TABLE solved_board_words (
    word_id INT REFERENCES words(id),
    solved_board_id INT REFERENCES solved_boards(id),
    word_path VARCHAR(1024)
);