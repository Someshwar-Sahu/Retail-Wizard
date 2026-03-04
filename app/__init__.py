from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import importlib

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    

    db.init_app(app)

    blueprints = [
        'app.routes.admin_access',
        'app.routes.auth',
        'app.routes.cart',
        'app.routes.checkout',
        'app.routes.dashboard',
        'app.routes.features',
        'app.routes.login',
        'app.routes.products',
        'app.routes.reports'
    ]

    for bp in blueprints:
        module = importlib.import_module(bp)
        app.register_blueprint(getattr(module, bp.split('.')[-1] + '_bp'))

    return app