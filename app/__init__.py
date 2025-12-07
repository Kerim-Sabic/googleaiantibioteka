"""
BAA-2025 Application Factory
"""

from flask import Flask
from flask_cors import CORS
from config.config import config
import os


def create_app(config_name=None):
    """
    Application factory pattern

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Enable CORS for API access
    CORS(app)

    # Initialize extensions (database, etc.) if needed
    # db.init_app(app)

    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app
