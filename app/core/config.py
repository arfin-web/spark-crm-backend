from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Pydantic reads these values from your .env file automatically.
    If a required value is missing, it throws an error at startup — 
    so you catch config problems immediately.
    """
    DATABASE_URL: str
    GROQ_AI_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # JWT security settings
    JWT_SECRET: str = "spark_crm_super_secret_jwt_key_change_me_in_prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # This tells pydantic-settings to read from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Create a single instance — import this everywhere
settings = Settings()