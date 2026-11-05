from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Tudo que pode mudar sem deploy vem do ambiente (RN-99, RN-119)."""

    model_config = SettingsConfigDict(env_file='.env', env_prefix='CLUBE_', extra='ignore')

    database_url: str = 'postgresql+psycopg://clube:clube@localhost:5450/clube_cafe'
    storage_secret: str = 'troque-em-producao'
    host: str = '127.0.0.1'  # 0.0.0.0 só atrás do Caddy, no deploy
    porta: int = 8350  # portas próprias para não disputar 8080/5432 com outros projetos da máquina
    login_demo: bool = True  # botões "Entrar como" sem senha; em produção, só se LOGIN_DEMO=true
    producao: bool = False  # sem reload automático e sem o segredo padrão

    janela_assinatura_minutos: int = 15
    prazo_legal_dias_uteis: int = 30
    tentativas_automaticas_b3: int = 3
    validade_links_adesao_dias: int = 10  # assinatura da proposta e link de criar senha


@lru_cache
def config() -> Config:
    cfg = Config()
    if cfg.producao and cfg.storage_secret == Config.model_fields['storage_secret'].default:
        raise RuntimeError('Em produção, defina CLUBE_STORAGE_SECRET.')
    return cfg
