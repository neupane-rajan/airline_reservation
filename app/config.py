from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./airline.db")
    
    # Payment gateway mock settings
    PAYMENT_GATEWAY_URL: str = "https://mock-payment-gateway.example.com/api/v1/process"
    PAYMENT_API_KEY: str = "mock-payment-api-key"

settings = Settings()