# app/__init__.py
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from .extensions import bcrypt
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'your-super-secret-key-that-is-long-and-random'
    project_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(project_dir, "database.db")

    CORS(app)
    bcrypt.init_app(app)

    db.init_app(app)

    with app.app_context():
        from .models import init_data
        db.create_all()
        init_data()

    from .auth import auth_bp
    from .recipes import recipes_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(recipes_bp, url_prefix='/api')

    @app.route('/')
    def landing_page():
        return render_template('landing.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/app')
    def main_app_page():
        return render_template('index.html')

    # The conflicting duplicate route has been removed.

    return app