from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, model_validator

from functools import lru_cache

class Settings( BaseSettings ):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

    anthropic_key: SecretStr

    # Models
    reviewer_model: str = "claude-sonnet-5-5"
    voter_model: str = ""
    max_tokens: int = Field( default = 2048, gt = 0 )

    # Concurrency
    max_concurrency: int = Field( default = 6, ge = 1 )
    max_retries: int = Field( default = 2, ge = 0 )

    # Voting
    vote_count: int = Field( default = 3, ge = 1 )
    vote_threshold: int = Field( default = 2, ge = 1 )

    @model_validator( mode = "after" )
    def check_vote_threshold( self ) -> "Settings":
        if self.vote_threshold > self.vote_count:
            raise ValueError(
                f"vote_threshold ({self.vote_threshold}) can't exceed "
                f"vote_count ({self.vote_count})"
            )

        return self
    
@lru_cache
def get_settings() -> Settings:
    return Settings()