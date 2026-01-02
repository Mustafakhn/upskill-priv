from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Learning Platform"
    VERSION: str = "1.0.0"

    # Database - MySQL
    MYSQL_URL: str = "mysql+pymysql://remote_user:M0nkey%40123@144.24.121.168:3306/learning_platform"

    # Database - MongoDB
    MONGODB_URL: str = "mongodb://remote_user:Password%40123@144.24.121.168:27017/"

    # AI Endpoint
    AI_ENDPOINT: str = "http://144.24.121.168:5000/generate"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production"  # Different key for refresh tokens
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # Scraping
    SCRAPE_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    FREE_JOURNEYS_LIMIT: int = 5

    # Search Providers (free tiers and paid)
    SERPAPI_KEY: Optional[str] = None
    BING_API_KEY: Optional[str] = None
    GOOGLE_CSE_API_KEY: Optional[str] = None
    GOOGLE_CSE_ID: Optional[str] = None  # Custom Search Engine ID

    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list of origins, or "*" for all

    # Web Push (VAPID)
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_CONTACT_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate public key from private key if not provided
        if self.VAPID_PRIVATE_KEY and not self.VAPID_PUBLIC_KEY:
            try:
                from app.utils.vapid import get_public_key_from_private, format_vapid_private_key
                formatted_key = format_vapid_private_key(self.VAPID_PRIVATE_KEY)
                public_key = get_public_key_from_private(formatted_key)
                if public_key:
                    self.VAPID_PUBLIC_KEY = public_key
            except Exception as e:
                print(f"Warning: Could not generate VAPID public key: {e}")


settings = Settings()
