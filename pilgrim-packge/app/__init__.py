from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Load config from config.py
    app.config.from_object('config.Config')

    db.init_app(app)  # Initialize SQLAlchemy with the app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes import main
    from .auth import auth
    from .admin_routes import admin
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app
