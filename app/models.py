from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Dictionary(db.Model):
    __tablename__ = "dictionaries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    filepath = db.Column(db.String, nullable=False)
    words = db.relationship("Word", backref="dictionary")

    def __repr__(self):
        return f"Dictionary: {self.name}, Filepath: {self.filepath}"

class Word(db.Model):
    __tablename__ = "words"
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String, unique=False, nullable=False)
    dict_id = db.Column(db.Integer, db.ForeignKey(Dictionary.id), nullable=False)
    definition = db.Column(db.String, unique=False, default="")
    paths = db.relationship("SolvedBoardPath", backref="word")

    def __repr__(self):
        return f"Word: {self.word}"

class SolvedBoard(db.Model):
    __tablename__ = "solved_boards"
    id = db.Column(db.Integer, primary_key=True)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)
    letters = db.Column(db.String, nullable=False)
    dict_id = db.Column(db.Integer, db.ForeignKey(Dictionary.id), nullable=False)
    max_word_len = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"SolvedBoard: {self.rows}, {self.cols}, {self.letters}, {self.max_word_len}"

class SolvedBoardPath(db.Model):
    __tablename__ = "solved_board_paths"
    word_id = db.Column(db.Integer, db.ForeignKey(Word.id), primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey(SolvedBoard.id), primary_key=True)
    path = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"SolvedBoardWord: {self.id}, Board ID: {self.board_id}, Path: {self.path}"