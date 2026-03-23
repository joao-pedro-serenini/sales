"""Application factory."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_object=None):
    """Create and configure the Flask application.

    Args:
        config_object: A configuration class or dotted string path.
            Defaults to :class:`~config.Config`.

    Returns:
        A configured :class:`flask.Flask` instance.
    """
    app = Flask(__name__)

    if config_object is None:
        from config import Config
        config_object = Config

    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.controllers.customer_controller import customer_bp
    app.register_blueprint(customer_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
