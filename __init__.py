from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.route('/')
    def index():
        return render_template('index.html')

    from . import board
    app.register_blueprint(board.bp)

    # @app.route('/board/<letters>')
    # def user(letters):
    #     return render_template('solved.html', letters=letters)

    return app