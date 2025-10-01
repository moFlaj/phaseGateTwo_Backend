# app/config/db_config.py
import os

class BaseConfig:
    # Mongo
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "art_sales_db")

    # JWT / app secrets (important for login)
    # SECRET_KEY must be secret in production. Use env vars / secret manager there.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "1"))

class DevConfig(BaseConfig):
    DEBUG = True
    # override DB if you want: DB_NAME = "art_sales_dev"

class TestConfig(BaseConfig):
    TESTING = True
    # test DB default
    DB_NAME = os.getenv("TEST_DB_NAME", "art_sales_test_db")
    SECRET_KEY = os.getenv("TEST_SECRET_KEY", "test-secret")
    JWT_EXP_HOURS = int(os.getenv("TEST_JWT_EXP_HOURS", "1"))
