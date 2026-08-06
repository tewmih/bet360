from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # JWT
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")

    # Application
    app_name: str = Field("Property Service", validation_alias="APP_NAME")
    debug: bool = Field(False, validation_alias="APP_DEBUG")  # ← This was missing
    environment: str = Field("development", validation_alias="APP_ENVIRONMENT")

    # Service
    service_port: int = Field(8001, validation_alias="SERVICE_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Create a single settings instance
settings = Settings()