from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Rent Builder API"
    VERSION: str = "0.1.0"

    # Рядок підключення до PostgreSQL (локальний приклад)
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/rent_db"

    class Config:
        env_file = ".env"


settings = Settings()
