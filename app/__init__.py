from flask import Flask, current_app, jsonify, request, url_for, render_template
from werkzeug.exceptions import HTTPException, InternalServerError

from app.database import db_session

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    @app.route("/ping", methods=['GET'])
    def ping():
        return jsonify(success=True,response="pong!"), 200

    @app.route("/", methods=['GET'])
    def index():
        return render_template('index.html')
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify(success=False, error_message="{}".format(e)), 500

    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        return jsonify(success=False, error_message="{}".format(e)), e.code
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
