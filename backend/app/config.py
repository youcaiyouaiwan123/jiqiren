from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import ClassVar


class Settings(BaseSettings):
    _backend_dir: ClassVar[Path] = Path(__file__).resolve().parents[1]
    _project_dir: ClassVar[Path] = _backend_dir.parent
    _default_knowledge_vault_path: ClassVar[str] = str(_project_dir / "knowledge")
    _default_knowledge_index_dir: ClassVar[str] = str(_backend_dir / "data" / "chroma" / "knowledge")

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "abaojie"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # JWT
    JWT_SECRET: str = "change-me-to-a-random-secret-key"
    JWT_ACCESS_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Claude AI
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 2048

    # 飞书
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""
    FEISHU_FAQ_APP_TOKEN: str = ""
    FEISHU_FAQ_TABLE_ID: str = ""
    FEISHU_DOC_APP_TOKEN: str = ""
    FEISHU_DOC_TABLE_ID: str = ""

    # 知识库
    KNOWLEDGE_VAULT_PATH: str = _default_knowledge_vault_path
    KNOWLEDGE_INDEX_DIR: str = _default_knowledge_index_dir
    KNOWLEDGE_EMBEDDING_PROVIDER: str = "openai"
    KNOWLEDGE_EMBEDDING_MODEL: str = ""
    KNOWLEDGE_GIT_REPO_URL: str = ""
    KNOWLEDGE_GIT_BRANCH: str = "main"

    @property
    def mysql_dsn(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def knowledge_vault_path(self) -> str:
        raw = (self.KNOWLEDGE_VAULT_PATH or "").strip() or self._default_knowledge_vault_path
        return str(Path(raw).expanduser().resolve())

    @property
    def knowledge_index_dir(self) -> str:
        raw = (self.KNOWLEDGE_INDEX_DIR or "").strip() or self._default_knowledge_index_dir
        return str(Path(raw).expanduser().resolve())

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
