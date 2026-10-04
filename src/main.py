from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.database import Base, engine, get_db

# Створення таблиць (на старті цього достатньо)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/healthcheck")
def healthcheck(db: Session = Depends(get_db)):
    return {"status": "ok", "database": "connected"}
