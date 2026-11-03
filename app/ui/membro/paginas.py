from nicegui import ui

from app.domain.models import Papel, Usuario
from app.ui.tema import pagina, titulo_pagina


@pagina('/', Papel.MEMBRO, 'Meus registros')
def meus_registros(usuario: Usuario):
    with ui.row().classes('w-full items-end justify-between'):
        titulo_pagina('Meus registros', 'Contratos em que você é parte.')
        ui.button('Novo registro', icon='add').props('unelevated no-caps disable')
    with ui.card().classes('w-full items-center q-pa-xl'):
        ui.icon('description', size='xl').classes('text-grey-5')
        ui.label('Você ainda não tem registros.').classes('text-grey-8')


@pagina('/conta', Papel.MEMBRO, 'Minha conta')
def minha_conta(usuario: Usuario):
    titulo_pagina('Minha conta', 'Para alterar algum dado, fale com o backoffice.')
    with ui.card().classes('w-full'):
        ui.label(usuario.nome).classes('text-subtitle1')
        ui.label(usuario.email).classes('text-grey-8')
