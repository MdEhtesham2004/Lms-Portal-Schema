import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
"config class for handling application configs"

class Config:
    # Database configuration
    # SQLALCHEMY_DATABASE_URI = 'postgresql://aifaflaskrestdb_user:lmjzIJs7IhVAjuZ1imzKokMYP9uDM9ja@dpg-d3hlt6r3fgac739thjbg-a.oregon-postgres.render.com/aifaflaskrestdb' 
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db' 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET=os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI=os.environ.get("GOOGLE_REDIRECT_URI")
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@aifirstacademy.com')
    
    
    # File upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    # In Flask app config
    
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    REDIS_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() in ['true', 'on', '1']
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day, 50 per hour')
    RATELIMIT_HEADERS_ENABLED = True
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '30'))  # minutes
    
    # Security headers
    SECURITY_HEADERS_ENABLED = os.environ.get('SECURITY_HEADERS_ENABLED', 'true').lower() in ['true', 'on', '1']
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'false').lower() in ['true', 'on', '1']
    
    # Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "https://checkout.razorpay.com", "https://accounts.google.com"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "data:"],
        'connect-src': ["'self'", "https://api.razorpay.com"],
        'frame-src': ["'self'", "https://api.razorpay.com", "https://accounts.google.com"],
    }
