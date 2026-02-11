"""
Application settings and configuration management.
"""
import os
from functools import lru_cache
from typing import List, Optional
from dotenv import load_dotenv

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, computed_field
# from lks_idprovider_keycloak.config import KeycloakConfig
# from lks_idprovider_keycloak.provider import KeycloakProvider

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    app_name: str = Field(default="Tetrics", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    version: str = Field(default="0.1.0", env="VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production-please-use-a-strong-random-key",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
  
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000", "http://localhost:9002"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Database Configuration
    db_user: str = Field(default=os.getenv("POSTGRES_USER", "fastapi_user"), env="POSTGRES_USER")
    db_password: str = Field(default=os.getenv("POSTGRES_PASSWORD", "fastapi123"), env="POSTGRES_PASSWORD")
    db_host: str = Field(default=os.getenv("POSTGRES_HOST", "localhost"), env="POSTGRES_HOST")
    db_port: str = Field(default=os.getenv("POSTGRES_PORT", "5432"), env="POSTGRES_PORT")
    db_name: str = Field(default=os.getenv("POSTGRES_DB", "fastapi_db"), env="POSTGRES_DB")
    database_url: str = Field(
        default_factory=lambda self=None: f"postgresql+psycopg://{os.getenv('POSTGRES_USER', 'fastapi_user')}:{os.getenv('POSTGRES_PASSWORD', 'fastapi123')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'fastapi_db')}",
        env="DATABASE_URL",
        description="Database connection URL, built from individual .env variables."
    )
    database_echo: bool = Field(
        default=False, 
        env="DATABASE_ECHO",
        description="Echo SQL queries for debugging"
    )
    database_pool_size: int = Field(
        default=10, 
        env="DATABASE_POOL_SIZE",
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=20, 
        env="DATABASE_MAX_OVERFLOW",
        description="Maximum overflow connections"
    )
    database_pool_pre_ping: bool = Field(
        default=True,
        env="DATABASE_POOL_PRE_PING",
        description="Verify connections before use"
    )
    database_pool_recycle: int = Field(
        default=3600,
        env="DATABASE_POOL_RECYCLE",
        description="Recycle connections after N seconds"
    )
    
    # Keycloak Configuration
    keycloak_server_url: str = Field(
        default="http://localhost:8080",
        env="KEYCLOAK_SERVER_URL"
    )
    keycloak_realm: str = Field(
        default="lks",
        env="KEYCLOAK_REALM"
    )
    keycloak_client_id: str = Field(
        default="fastapi-client",
        env="KEYCLOAK_CLIENT_ID"
    )
    keycloak_client_secret: Optional[str] = Field(
        default=None,
        env="KEYCLOAK_CLIENT_SECRET"
    )
    keycloak_verify_token: bool = Field(default=True, env="KEYCLOAK_VERIFY_TOKEN")
    
    # COMMENTED OUT - Keycloak not needed for now
    # def get_identity_provider(self) -> KeycloakProvider:
    #     """Get a new Keycloak identity provider instance."""
    #     config = KeycloakConfig(
    #         base_url=self.keycloak_server_url,
    #         realm=self.keycloak_realm,
    #         client_id=self.keycloak_client_id,
    #         client_secret=self.keycloak_client_secret,
    #         timeout=30,  # Default timeout
    #         verify_ssl=False,  # Default SSL verification
    #         use_token_introspection=True,
    #         use_userinfo_endpoint=True,
    #         validate_audience=True,
    #         validate_issuer=True
    #     )
    #     return KeycloakProvider(config=config)
    
    def get_identity_provider(self):
        """Placeholder - Keycloak disabled for now."""
        return None

    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # API Documentation
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", env="OPENAPI_URL")
    

    
    @field_validator("cors_origins")
    def parse_cors_origins(cls, value):
        """Parse CORS origins from string or list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value

    @field_validator("cors_allow_methods")
    def parse_cors_methods(cls, value):
        """Parse CORS methods from string or list."""
        if isinstance(value, str):
            return [method.strip() for method in value.split(",")]
        return value

    @field_validator("cors_allow_headers")
    def parse_cors_headers(cls, value):
        """Parse CORS headers from string or list."""
        if isinstance(value, str):
            return [header.strip() for header in value.split(",")]
        return value
    
    @field_validator("secret_key")
    def validate_secret_key(cls, value):
        """Validate secret key length."""
        if len(value) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return value
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # This will ignore extra fields instead of raising an error
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
