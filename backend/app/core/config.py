from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded exclusively from environment variables."""

    database_url: str = "postgresql+psycopg://academia:academia_local@localhost:5432/academia_bid"
    auth_provider: str = "local"
    local_default_user_id: str = "dev-user-001"
    media_provider: str = "local"
    local_media_url: str = "http://localhost:8000/media/demo.mp4"
    cors_origins: str = "http://localhost:3000"
    azure_tenant_id: str = ""
    azure_backend_client_id: str = ""
    azure_backend_client_secret: str = ""
    azure_frontend_client_id: str = ""
    azure_backend_scope: str = ""
    sharepoint_site_host: str = "bidgservicios.sharepoint.com"
    sharepoint_site_path: str = "/sites/Centrodeaprendizaje"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
