from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings( BaseSettings ):
    model_config = SettingsConfigDict( env_file = ".env" )

    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    VOYAGE_API_KEY: str
    VOYAGE_MODEL: str = "voyage-4"

settings = Settings()