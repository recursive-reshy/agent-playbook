from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings( BaseSettings ):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

    anthropic_api_key: str
    
    # The classifier runs on every ticket, so it should be cheap and fast.
    classifier_model: str = "claude-haiku-4-5-20251001"

    # Model routing: simple tickets go to the cheap model, complex ones to the stronger one.
    simple_model: str = "claude-haiku-4-5-20251001"
    complex_model: str = "claude-sonnet-5"

    # Below this confidence, a ticket goes to human review instead of a handler.
    confidence_threshold: float = 0.7

settings = Settings()