import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Визначаємо, яке середовище зараз активне (за замовчуванням буде sandbox)
env_state = os.getenv("ENVIRONMENT", "sandbox")
env_file = f".env.{env_state}"


class Settings(BaseSettings):
    ENVIRONMENT: str
    DEBUG: bool
    DATABASE_URL: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")


# Створюємо глобальний об'єкт налаштувань
settings = Settings()
