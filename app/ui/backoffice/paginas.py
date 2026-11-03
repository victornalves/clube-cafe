from nicegui import ui

from app.domain.models import Papel, Usuario
from app.ui.tema import pagina, titulo_pagina

# Telas que ainda vão ser construídas no Marco 3 (docs/plano-mvp.md)
EM_CONSTRUCAO = [
    ('/backoffice/registros', 'Todos os registros', 'Contratos de todos os membros, com a situação interna completa.'),
    ('/backoffice/pendencias', 'Pendências', 'Registros com falha na B3, ordenados pelo prazo legal.'),
    ('/backoffice/auditoria', 'Auditoria', 'Log de eventos.'),
]


def _em_construcao(rota: str, titulo: str, subtitulo: str):
    @pagina(rota, Papel.OPERADOR, titulo)
    def tela(usuario: Usuario):
        titulo_pagina(titulo, subtitulo)
        with ui.card().classes('w-full items-center q-pa-xl'):
            ui.icon('construction', size='xl').classes('text-grey-5')
            ui.label('Em construção.').classes('text-grey-8')


for rota, titulo, subtitulo in EM_CONSTRUCAO:
    _em_construcao(rota, titulo, subtitulo)
