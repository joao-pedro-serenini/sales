"""Configuração da aplicação."""

import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///sales.db")
