from pathlib import Path

from nicegui import app, ui

from app.config import config

# Importados pelo efeito colateral: cada módulo registra as próprias páginas
from app.ui import login  # noqa: F401
from app.ui.backoffice import membros as backoffice_membros  # noqa: F401
from app.ui.backoffice import paginas as backoffice  # noqa: F401
from app.ui.membro import paginas as membro  # noqa: F401
from app.ui.membro import registro  # noqa: F401

STATIC = Path(__file__).parent / 'static'
app.add_static_files('/static', STATIC)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='Clube do Café',
        host=config().host,
        port=config().porta,
        favicon=STATIC / 'favicon.png',
        language='pt-BR',
        storage_secret=config().storage_secret,
        show=False,
    )
