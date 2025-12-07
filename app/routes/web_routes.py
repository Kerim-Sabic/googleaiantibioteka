"""
Web Routes - HTML Pages
"""

from flask import render_template
from app.routes import main_bp


@main_bp.route('/')
def index():
    """Home page - BAA-2025 interface"""
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
