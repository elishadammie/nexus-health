from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Defines the application's settings, loaded from environment variables.
    """
    # LLM Settings
    OPENAI_API_KEY: str

    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # This tells pydantic to look for a .env file in the parent directory (nexus-api/)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

# Create a single, importable instance of the settings
settings = Settings()