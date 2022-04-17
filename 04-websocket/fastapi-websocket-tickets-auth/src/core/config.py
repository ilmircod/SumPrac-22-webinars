from pydantic import AnyHttpUrl, BaseSettings, RedisDsn


class Settings(BaseSettings):
    environment: str = "local"
    redis_dsn: RedisDsn = "redis://localhost:6379/"
    backend_url: AnyHttpUrl = "https://example.com/"


settings = Settings()
