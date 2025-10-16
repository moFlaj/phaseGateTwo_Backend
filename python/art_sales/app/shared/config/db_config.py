import os


class BaseConfig:
    """Base configuration shared by all environments."""
    # Core Flask / JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 3))

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "art_sales_db")

    # Redis / RQ
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Mail settings (SMTP or mock)
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM", "Art Sales <noreply@artsales.com>")

    # Mailer & async job flags
    USE_MOCK_MAILER = os.getenv("USE_MOCK_MAILER", "False") == "True"
    ASYNC_EMAIL = os.getenv("ASYNC_EMAIL", "False") == "True"

    # Misc
    TESTING = False
    DEBUG = False


class DevConfig(BaseConfig):
    """Development configuration — for local dev via PyCharm Run Config."""
    DEBUG = True
    TESTING = False
    USE_MOCK_MAILER = os.getenv("USE_MOCK_MAILER", "True") == "True"
    ASYNC_EMAIL = os.getenv("ASYNC_EMAIL", "False") == "True"


class ProdConfig(BaseConfig):
    """Production configuration — real mailer, async on, no debug."""
    DEBUG = False
    TESTING = False
    USE_MOCK_MAILER = False
    ASYNC_EMAIL = True


class TestConfig(BaseConfig):
    """Testing configuration — used by pytest fixtures."""
    DEBUG = False
    TESTING = True
    DB_NAME = os.getenv("DB_NAME", "art_sales_test")
    USE_MOCK_MAILER = True
    ASYNC_EMAIL = False
