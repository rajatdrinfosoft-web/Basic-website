from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask_assets import Environment, Bundle
from flask_migrate import Migrate
from flask_compress import Compress

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()
assets = Environment()
migrate = Migrate()
compress = Compress()

def create_app():
    app = Flask(__name__)

    # Load config from config.py
    app.config.from_object('config.Config')

    db.init_app(app)  # Initialize SQLAlchemy with the app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    cache.init_app(app)
    assets.init_app(app)
    migrate.init_app(app, db)
    compress.init_app(app)

    # Define asset bundles
    css_bundle = Bundle('css/bootstrap.min.css', 'css/style.css', filters='cssmin', output='gen/packed.css')
    js_bundle = Bundle('js/bootstrap.bundle.min.js', 'js/script.js', filters='jsmin', output='gen/packed.js')

    assets.register('css_all', css_bundle)
    assets.register('js_all', js_bundle)

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
