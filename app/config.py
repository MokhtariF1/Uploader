from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@localhost:5432/upload_project"
    JWT_SECRET_KEY: str = "Hossein_90"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Uploader website"

    class Config:
        env_file = ".env"

settings = Settings()
