"""
BAA-2025 Configuration
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Base configuration"""

    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # Drug Registry
    REGISTRY_VERSION = "2025"
    REGISTRY_COUNTRY = "Bosnia and Herzegovina"
    REGISTRY_PATH = BASE_DIR / "data" / "registry"

    # Clinical Logic
    CLOSED_WORLD_ASSUMPTION = True  # Only recommend registered drugs
    ENABLE_SUBSTITUTION = True      # Auto-substitute unavailable drugs
    STRICT_REGULATORY = True        # Enforce ZU/Rp restrictions

    # Safety Features
    ENABLE_ALLERGY_CHECK = True
    ENABLE_INTERACTION_CHECK = True
    ENABLE_RENAL_ADJUSTMENT = True
    ENABLE_HEPATIC_ADJUSTMENT = True

    # Dose Calculation
    PEDIATRIC_WEIGHT_BASED_DOSING = True
    ADULT_WEIGHT_THRESHOLD_KG = 40

    # Database (optional, for logging/sessions)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR}/baa2025.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # In production, SECRET_KEY must be set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
