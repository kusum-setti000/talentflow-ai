from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_timeout: int = Field(default=45, ge=5, le=180)
    openai_max_retries: int = Field(default=1, ge=0, le=3)
    max_file_mb: int = Field(default=5, ge=1, le=20)
    max_pages: int = Field(default=30, ge=1, le=100)
    max_characters: int = Field(default=60000, ge=1000, le=200000)
    langsmith_tracing: bool = False
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "talentflow-ai-dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()
