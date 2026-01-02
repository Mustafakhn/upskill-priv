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
        env_file_encoding = 'utf-8'
        case_sensitive = False
        # Prioritize environment variables (set by Docker Compose) over .env file
        extra = 'ignore'


# Create settings instance
settings = Settings()

# Auto-generate public key from private key if not provided
if settings.VAPID_PRIVATE_KEY and not settings.VAPID_PUBLIC_KEY:
    try:
        from app.utils.vapid import get_public_key_from_private, format_vapid_private_key
        formatted_key = format_vapid_private_key(settings.VAPID_PRIVATE_KEY)
        public_key = get_public_key_from_private(formatted_key)
        if public_key:
            settings.VAPID_PUBLIC_KEY = public_key
            print(f"✓ Generated VAPID public key from private key")
        else:
            print(f"⚠ Warning: Could not generate VAPID public key")
    except Exception as e:
        print(f"⚠ Warning: Could not generate VAPID public key: {e}")
        import traceback
        traceback.print_exc()

# Debug: Print VAPID key status (without showing the actual key)
if settings.VAPID_PRIVATE_KEY:
    print(f"✓ VAPID_PRIVATE_KEY is configured (length: {len(settings.VAPID_PRIVATE_KEY)})")
else:
    print(f"⚠ VAPID_PRIVATE_KEY is not configured")

if settings.VAPID_PUBLIC_KEY:
    print(f"✓ VAPID_PUBLIC_KEY is configured (length: {len(settings.VAPID_PUBLIC_KEY)})")
else:
    print(f"⚠ VAPID_PUBLIC_KEY is not configured")
