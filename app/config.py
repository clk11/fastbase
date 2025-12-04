from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    app_name: str = "FastBase"
    debug: bool = False

    # Supabase settings
    supabase_url: str
    supabase_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @field_validator('supabase_url')
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        """Validate that Supabase URL uses HTTPS and correct format."""
        if not v.startswith('https://'):
            raise ValueError('Supabase URL must use HTTPS')
        if not v.endswith('.supabase.co'):
            raise ValueError('Invalid Supabase URL format')
        return v

    @field_validator('supabase_key')
    @classmethod
    def validate_supabase_key(cls, v: str) -> str:
        """Validate that Supabase key is not empty."""
        if len(v) < 20:
            raise ValueError('Supabase key appears to be invalid (too short)')
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()
