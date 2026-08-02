from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_QUEUE_NAME: str = "notifications"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = "localuser"
    SMTP_PASSWORD: str = "pass123"  
    EMAILS_FROM: str = "noreply@gmail.com"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()