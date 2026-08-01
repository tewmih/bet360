
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from  environment variables."""

    #Database
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    #JWT authentication
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(..., validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(..., validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")

    #Application
    debug: bool = Field(False, validation_alias="APP_DEBUG")
    environment: str = Field("development", validation_alias="APP_ENVIRONMENT")
    app_name: str = Field("User Service", validation_alias="APP_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
# Create a single settings instance.
settings = Settings()
