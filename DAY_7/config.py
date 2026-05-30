"""
Application Configuration Module
Centralized configuration management for the Violence Detection System
"""

import os
from pathlib import Path
from datetime import timedelta

# ======================== Base Configuration ========================

class Config:
    """Base configuration"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Upload Configuration
    MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
    UPLOAD_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.jpg', '.jpeg', '.png'}
    
    # Detection Settings
    DETECTION_THRESHOLD = 0.5
    DETECTION_CONFIDENCE = 0.5
    
    # Model Configuration
    MODEL_NAME = 'YOLOv8n'
    MODEL_TASK = 'Detection'
    MODEL_PATH = 'runs/detect/mall_yolov8/weights/best.pt'
    
    # Paths
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / 'logs'
    TEMP_DIR = BASE_DIR / 'temp'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = LOGS_DIR / 'app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Server
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    WORKERS = 4
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create necessary directories
        Config.LOGS_DIR.mkdir(exist_ok=True)
        Config.TEMP_DIR.mkdir(exist_ok=True)


# ======================== Development Configuration ========================

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'


# ======================== Testing Configuration ========================

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False


# ======================== Production Configuration ========================

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    LOG_LEVEL = 'INFO'
    
    # Production should use environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable must be set in production')


# ======================== Configuration Selection ========================

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)


# ======================== Feature Flags ========================

class Features:
    """Feature flags for the application"""
    
    ENABLE_AUTHENTICATION = True
    ENABLE_VIDEO_UPLOAD = True
    ENABLE_WEBCAM_STREAM = True
    ENABLE_RTSP_STREAM = True
    ENABLE_LOGGING = True
    ENABLE_ERROR_TRACKING = False  # Set True with Sentry
    
    # Security Features
    ENABLE_RATE_LIMITING = False  # Set True with Flask-Limiter
    ENABLE_CORS = False  # Set True with Flask-CORS


# ======================== User Credentials (Development Only) ========================

DEFAULT_USERS = {
    'admin': {
        'password_hash': 'pbkdf2:sha256:260000$YWYmQQSYlU0fVlLf$db3b7a8e7c8e9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u',
        'roles': ['admin', 'user'],
        'email': 'admin@vdai.local'
    },
    'user': {
        'password_hash': 'pbkdf2:sha256:260000$a8b9c0d1e2f3g4h5$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x',
        'roles': ['user'],
        'email': 'user@vdai.local'
    }
}
