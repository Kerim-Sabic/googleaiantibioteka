"""
Flask Routes
"""

from flask import Blueprint

# Main blueprint for web pages
main_bp = Blueprint('main', __name__)

# API blueprint for JSON endpoints
api_bp = Blueprint('api', __name__)

# Import route handlers
from app.routes import web_routes, api_routes
