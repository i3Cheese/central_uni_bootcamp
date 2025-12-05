from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mirumir"
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
