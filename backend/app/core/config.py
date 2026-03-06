from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────────────────
    app_env: str = "dev"
    api_port: int = 8000

    # ── CORS ───────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins.
    # Defaults to Vite dev server; override in production with your real domain.
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── Databases ──────────────────────────────────────────────────────────
    postgres_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"

    # ── Vector / Graph stores ──────────────────────────────────────────────
    chroma_persist_dir: str = "data/chroma"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change_me"

    # ── Local job store ────────────────────────────────────────────────────
    jobs_db_path: str = "data/jobs.db"
    artifacts_dir: str = "artifacts"

    # ── External API keys ──────────────────────────────────────────────────
    tavily_api_key: str = ""
    groq_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""

    # ── Local LLM ─────────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"

    # ── Worker mode ────────────────────────────────────────────────────────
    use_celery: bool = False

    # ── API keys (role-based) ──────────────────────────────────────────────
    api_key_admin: str = Field(default="admin-local-key")
    api_key_editor: str = Field(default="editor-local-key")
    api_key_viewer: str = Field(default="viewer-local-key")

    @field_validator("cors_origins")
    @classmethod
    def _validate_cors(cls, v: str) -> str:
        # Security: warn if using wildcard in production-like environments
        return v


settings = Settings()
