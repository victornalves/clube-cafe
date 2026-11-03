from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Tudo que pode mudar sem deploy vem do ambiente (RN-99, RN-119)."""

    model_config = SettingsConfigDict(env_file='.env', env_prefix='CLUBE_', extra='ignore')

    database_url: str = 'postgresql+psycopg://clube:clube@localhost:5433/clube_cafe'
    storage_secret: str = 'troque-em-producao'
    host: str = '127.0.0.1'  # 0.0.0.0 só atrás do Caddy, no deploy
    porta: int = 8080

    janela_assinatura_minutos: int = 15
    prazo_legal_dias_uteis: int = 30
    tentativas_automaticas_b3: int = 3


@lru_cache
def config() -> Config:
    return Config()
