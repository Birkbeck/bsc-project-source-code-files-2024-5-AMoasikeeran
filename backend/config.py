from pydantic import BaseModel
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    MODEL_NAME: str = "gpt-4o"
    SAMPLE_MIN_ROWS: int = 200
    SAMPLE_MAX_ROWS: int = 400
    MAX_FILE_BYTES: int = 10 * 1024 * 1024
    ALLOWED_ORIGINS: list[str] = ["*"]

settings = Settings()