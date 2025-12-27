"""
Configuration file for GearGuard
Set environment variables or modify defaults here
"""

import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    
    # PostgreSQL Database Configuration
    # Option 1: Use environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Option 2: Configure directly (not recommended for production)
    # Format: postgresql://username:password@host:port/database
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'gearguard')
    
    # Build database URL - PostgreSQL is REQUIRED (no SQLite fallback)
    if not DATABASE_URL:
        # URL-encode password to handle special characters
        encoded_password = quote_plus(POSTGRES_PASSWORD)
        encoded_user = quote_plus(POSTGRES_USER)
        # Build PostgreSQL connection string
        SQLALCHEMY_DATABASE_URI = f'postgresql://{encoded_user}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Validate that we're using PostgreSQL
    if not SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        raise ValueError(
            "PostgreSQL is required. Please configure PostgreSQL connection. "
            "See POSTGRESQL_SETUP.md for instructions."
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Flask-Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = 10

