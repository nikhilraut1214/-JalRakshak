import os
from pydantic import model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JalRakshak AI"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jalrakshak.db")
    
    # Supabase Auth Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "jalrakshak-dev-secret-key-change-in-prod-32chars")
    SUPABASE_JWT_AUDIENCE: str = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")

    # Network / CORS configuration
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Analytical configurations
    LOSS_REFERENCE_LITERS: float = 1000.0  # Backend configured reference amount for loss score normalization
    TREND_NORMALIZATION_FACTOR: float = 50.0  # Slope normalization factor
    ROBUST_EPSILON: float = 1e-6
    # Implementation/configuration choice, not a universal requirement from technical specification (PRD FR-05 & architecture.md Section 7.2)
    MIN_BASELINE_READINGS: int = 5
    
    # Default organization for dev
    DEFAULT_ORG_ID: str = "org-default"

    # Telemetry Ingestion configuration
    CSV_MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    CSV_MAX_ROWS: int = int(os.getenv("CSV_MAX_ROWS", "10000"))

    model_config = {"env_file": ".env", "extra": "allow"}

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            default_dev_secret = "jalrakshak-dev-secret-key-change-in-prod-32chars"
            if not self.SUPABASE_JWT_SECRET or self.SUPABASE_JWT_SECRET == default_dev_secret:
                raise ValueError(
                    "Production configuration error: SUPABASE_JWT_SECRET must be explicitly configured with a non-default secret in production."
                )
            if "*" in [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]:
                raise ValueError(
                    "Production configuration error: Wildcard '*' origin is not permitted in ALLOWED_ORIGINS when credentials/authentication are enabled."
                )
        return self

settings = Settings()
