"""
Application Configuration
Load settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Smart Traffic System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration (SQL Server)
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_SERVER: str = "localhost"
    DB_PORT: int = 1433
    DB_NAME: str = "SmartTrafficDB"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_TRUSTED_CONNECTION: str = "yes"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    HERE_MAPS_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    
    # ML Model Paths
    LSTM_MODEL_PATH: str = "../ml-pipeline/models/saved_models/lstm_traffic_model.h5"
    XGBOOST_MODEL_PATH: str = "../ml-pipeline/models/saved_models/xgboost_traffic_model.pkl"
    PROPHET_MODEL_PATH: str = "../ml-pipeline/models/saved_models/prophet_traffic_model.pkl"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "../logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache Settings
    CACHE_TTL: int = 300
    ENABLE_CACHE: bool = True
    
    @property
    def database_url(self) -> str:
        """Construct SQL Server connection string"""
        if self.DB_TRUSTED_CONNECTION.lower() == "yes":
            return f"mssql+pyodbc://{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?driver={self.DB_DRIVER}&trusted_connection=yes"
        else:
            return f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?driver={self.DB_DRIVER}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
