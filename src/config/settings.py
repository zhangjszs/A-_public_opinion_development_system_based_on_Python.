import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _parse_csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "")
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]

def _get_secret_key() -> str | None:
    value = os.getenv("SECRET_KEY")
    if value:
        return value
    env = os.getenv("FLASK_ENV", "development")
    if env != "production":
        return os.urandom(32).hex()
    return None

class Config:
    # Flask Settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = _get_secret_key()
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    IS_DEVELOPMENT = FLASK_ENV == 'development'

    ALLOWED_ORIGINS = _parse_csv_env('ALLOWED_ORIGINS') or (
        ['http://localhost:3000', 'http://127.0.0.1:3000'] if IS_DEVELOPMENT else []
    )
    ADMIN_USERS = set(_parse_csv_env('ADMIN_USERS'))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or SECRET_KEY
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

    # Database Settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'weibo_analysis')
    DB_CHARSET = 'utf8mb4'
    
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    DB_POOL_RECYCLE = 3600
    DB_POOL_TIMEOUT = 30

    @classmethod
    def get_database_url(cls):
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset={cls.DB_CHARSET}"

    # Redis / Celery Settings
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Path Settings
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    CACHE_DIR = os.path.join(BASE_DIR, 'cache')
    MODEL_DIR = os.path.join(BASE_DIR, 'model')

    # App Settings
    JSON_AS_ASCII = False
    SEND_FILE_MAX_AGE_DEFAULT = 0 if IS_DEVELOPMENT else 43200
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PERMANENT_SESSION_LIFETIME = 86400 * 7 # 7 days
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    @classmethod
    def validate(cls) -> None:
        if cls.FLASK_ENV == 'production':
            if not cls.SECRET_KEY:
                raise RuntimeError('SECRET_KEY must be set in production')
            if not cls.JWT_SECRET_KEY:
                raise RuntimeError('JWT_SECRET_KEY must be set in production (or reuse SECRET_KEY)')
            if not cls.ALLOWED_ORIGINS:
                raise RuntimeError('ALLOWED_ORIGINS must be set in production')

# Late binding for properties that depend on class variables
Config.SQLALCHEMY_DATABASE_URI = Config.get_database_url()
Config.SQLALCHEMY_TRACK_MODIFICATIONS = False
Config.SQLALCHEMY_ECHO = Config.IS_DEVELOPMENT

# Backward compatibility aliases
BASE_DIR = Config.BASE_DIR
LOG_DIR = Config.LOG_DIR
DATA_DIR = Config.DATA_DIR
STATIC_DIR = Config.STATIC_DIR
CACHE_DIR = Config.CACHE_DIR
MODEL_DIR = Config.MODEL_DIR
