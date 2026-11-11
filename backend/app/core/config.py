from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = ["http://localhost:3000"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    log_level: str = "INFO"
    llm_provider: str = ""
    llm_model: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_timeout_seconds: float = 120.0
    llm_health_timeout_seconds: float = 3.0
    llm_context_window: int = 4096
    llm_max_output_tokens: int = 768
    llm_temperature: float = 0.2
    llm_keep_alive: str = "5m"
    rag_database: str = ""
    model_directory: str = "./models"
    rag_embedding_model: str = "all-MiniLM-L6-v2"
    rag_default_top_k: int = Field(default=5, ge=1, le=50)
    rag_min_similarity: float = Field(default=0.3, ge=-1.0, le=1.0)
    rag_max_context_chars: int = Field(default=6000, ge=500)
    rag_max_document_chars: int = Field(default=500_000, ge=1000)
    rag_chunk_words: int = Field(default=300, ge=50)
    rag_chunk_overlap_words: int = Field(default=40, ge=0)
    quantum_kyber_variant: str = "kyber768"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
