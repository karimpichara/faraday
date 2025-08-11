import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://localhost/kepler")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Configuration
    API_TOKEN = os.getenv("API_TOKEN", "1234567890")
