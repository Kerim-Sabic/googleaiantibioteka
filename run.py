#!/usr/bin/env python3
"""
Bosnia & Herzegovina Antibiotic Advisor (BAA-2025)
Main Application Entry Point

This is a hospital-grade, deterministic clinical decision support system.
"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Development server settings
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    print("=" * 70)
    print("Bosnia & Herzegovina Antibiotic Advisor (BAA-2025)")
    print("Hospital-Grade Clinical Decision Support System")
    print("=" * 70)
    print(f"Running on http://localhost:{port}")
    print("Registry Base: Registar lijekova Bosne i Hercegovine 2025")
    print("=" * 70)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
