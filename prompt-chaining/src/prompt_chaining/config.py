from pydantic_settings import BaseSettings, SettingsConfigDict

class Setttings( BaseSettings ):
    model_config = SettingsConfigDict( env_file = ".env", extra = "ignore" )

    anthropic_api_key: str
    model: str = "claude-sonnet-5"
    max_tokens: int = 4096

settings = Setttings()