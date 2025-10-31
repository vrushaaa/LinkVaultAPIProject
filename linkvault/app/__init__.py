import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load config
    from config import Config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register CLI group
    @app.cli.group()
    def cli():
        """LinkVault management commands."""
        pass

    # === IMPORT MODELS CORRECTLY ===
    from app.models.bookmark import Bookmark  # noqa: F401
    from app.models.tag import Tag          # noqa: F401

    # === REGISTER BLUEPRINTS ===
    from app.routes.bookmark_routes import bp as bookmarks_bp
    from app.routes.bookmark_routes import short_bp

    app.register_blueprint(bookmarks_bp, url_prefix='/api')
    app.register_blueprint(short_bp)  # Root level

    # === CLI COMMANDS ===
    from app.cli.export import export
    from app.cli.imp import import_bookmarks
    app.cli.add_command(export)
    app.cli.add_command(import_bookmarks)

    return app