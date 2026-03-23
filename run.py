"""Ponto de entrada da aplicação."""

import uvicorn

from app import create_app
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
