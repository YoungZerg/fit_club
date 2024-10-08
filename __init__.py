from flask import Flask, session
from flask_session import Session


def create_app():
    
    app = Flask(__name__)
    app.secret_key = 'c7797a01df530695ab2ddfc7'
    app.config['SESSION_TYPE'] = 'filesystem'
    
    from fit_club.app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from fit_club.app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from fit_club.app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from fit_club.app.trainer import trainer as trainer_blueprint
    app.register_blueprint(trainer_blueprint)

    return app