from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "CareerForge AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DB_ECHO: bool = False  # Set to true in .env to enable verbose SQLAlchemy SQL logging
    SECRET_KEY: str = "insecure-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://careerforge:password@localhost:5432/careerforge_db"
    DATABASE_URL_SYNC: str = "postgresql://careerforge:password@localhost:5432/careerforge_db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    # Judge0
    JUDGE0_BASE_URL: str = "https://judge0-ce.p.rapidapi.com"
    JUDGE0_API_KEY: str = ""
    JUDGE0_HOST: str = "judge0-ce.p.rapidapi.com"
    MOCK_JUDGE0: bool = False

    # AI Provider & Ollama Configuration
    AI_PROVIDER: str = "ollama"
    AI_BASE_URL: str = "http://localhost:11434"
    AI_API_KEY: str = "ollama"
    AI_MODEL: str = "gemma4:12b-mlx"
    AI_MAX_TOKENS: int = 2048
    AI_TEMPERATURE: float = 0.2
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma4:12b-mlx"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60


settings = Settings()
