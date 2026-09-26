import os
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

    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()
