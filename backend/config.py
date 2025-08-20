from pydantic import BaseModel
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    MODEL_NAME: str = "gpt-4o"
    SAMPLE_MIN_ROWS: int = 200
    SAMPLE_MAX_ROWS: int = 400
    MAX_FILE_BYTES: int = 10 * 1024 * 1024
    ALLOWED_ORIGINS: list[str] = ["*"]
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finbot_users.db")
    PORT: int = int(os.getenv("PORT", 8000))

    def get_cors_origins(self):
        """Returns CORS origins according to environment"""
        if self.ENVIRONMENT == "production":
            return [
                "https://*.streamlit.app",
                "http://localhost:8501",
                "https://bsc-project-source-code-files-2024-5.onrender.com/"
            ]
        else:
            return ["*"]

settings = Settings()