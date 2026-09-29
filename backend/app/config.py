from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SYNTRA"
    app_env: str = "development"

    llm_api_key_1: str = ""
    llm_api_key_2: str = ""
    llm_api_key_3: str = ""

    llm_model: str = "gemini-3.6-flash"
    llm_temperature: float = 0.0

    database_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()