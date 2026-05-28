from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://agentforge:agentforge@localhost:5432/agentforge"
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ANTHROPIC_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    MAX_AGENT_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 120

    class Config:
        env_file = ".env"

settings = Settings()
