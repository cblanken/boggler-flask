from flask import Flask, request, render_template, redirect

def create_app():
    app = Flask(__name__)
    # TODO: handle session key with env vars
    app.secret_key = "THIS_IS_A_TEST_KEY_REMOVE_ME!"

    from .board import bp
    app.register_blueprint(bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return redirect('board')

    @app.route('/history')
    def history():
        return render_template('solve_history.html')

    return app