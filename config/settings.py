from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., description="Database connection string")
    SECRET_KEY: str = Field(..., description="Secret key for authentication")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., description="Access token expiration time in minutes")
    ALGORITHM: str = Field(..., description="Algorithm for generating access tokens")
    # DEBUG: bool = Field(False, description="Enable debug mode")
    # ENV: str = Field("development", description="Environment type")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()