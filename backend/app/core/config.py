from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    api_port: int = 8000

    postgres_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"

    chroma_persist_dir: str = "data/chroma"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change_me"

    jobs_db_path: str = "data/jobs.db"
    artifacts_dir: str = "artifacts"

    tavily_api_key: str = ""

    groq_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""

    ollama_base_url: str = "http://localhost:11434"

    use_celery: bool = False
    api_key_admin: str = Field(default="admin-local-key")
    api_key_editor: str = Field(default="editor-local-key")
    api_key_viewer: str = Field(default="viewer-local-key")


settings = Settings()

