"""Application configuration."""

import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///sales.db")
