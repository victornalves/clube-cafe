from pathlib import Path

from nicegui import app, ui

from app.config import config
from app.db import sessao
from app.services import b3, envelopes

# Importados pelo efeito colateral: cada módulo registra as próprias páginas
from app.ui import login  # noqa: F401
from app.ui.backoffice import auditoria, pendencias  # noqa: F401
from app.ui.backoffice import membros as backoffice_membros  # noqa: F401
from app.ui.backoffice import registros as backoffice_registros  # noqa: F401
from app.ui.membro import paginas as membro  # noqa: F401
from app.ui.membro import registro  # noqa: F401

STATIC = Path(__file__).parent / 'static'
app.add_static_files('/static', STATIC)


def expirar_janelas():
    with sessao() as s:
        envelopes.expirar_vencidos(s)


def enviar_a_b3():
    with sessao() as s:
        b3.processar_assinados(s)


app.timer(10, expirar_janelas)
app.timer(5, enviar_a_b3)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='Câmara do Comércio de Café',
        host=config().host,
        port=config().porta,
        favicon=STATIC / 'favicon.png',
        language='pt-BR',
        storage_secret=config().storage_secret,
        show=False,
        reload=not config().producao,
    )
