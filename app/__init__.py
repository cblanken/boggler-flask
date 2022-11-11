"""Main app module
"""
from flask import Flask, request, render_template, redirect
from config import config

def create_app(config_name):
    """Return base Flask app object
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    @app.errorhandler(404)
    def page_not_found(_):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(_):
        return render_template('errors/500.html'), 500

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return redirect('board')

    @app.route('/history')
    def history():
        return render_template('solve_history.html')

    return app
