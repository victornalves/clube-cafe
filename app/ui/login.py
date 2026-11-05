from fastapi.responses import RedirectResponse
from nicegui import app, ui

from app.db import sessao
from app.services import auth
from app.ui.tema import CORES, INICIO, marca_destaque, usuario_logado


@ui.page('/login', title='Entrar · Câmara do Comércio de Café')
def login():
    usuario = usuario_logado()
    if usuario is not None:
        return RedirectResponse(INICIO[usuario.papel])

    ui.colors(**CORES)

    def entrar():
        if not email.value or not senha.value:
            ui.notify('Informe e-mail e senha.', type='warning')
            return
        with sessao() as s:
            usuario = auth.autenticar(s, email.value, senha.value)
        if usuario is None:
            ui.notify('E-mail ou senha incorretos.', type='negative')
            return
        app.storage.user['usuario_id'] = usuario.id
        ui.navigate.to(INICIO[usuario.papel])

    with ui.column().classes('absolute-center items-center w-full max-w-3xl q-px-md'):
        with ui.column().classes('items-center q-mb-lg'):
            marca_destaque()
        with ui.card().classes('w-full max-w-sm q-pa-lg'):
            email = ui.input('E-mail').props('outlined type=email autocomplete=username').classes('w-full')
            senha = ui.input('Senha', password=True).props('outlined autocomplete=current-password').classes('w-full')
            senha.on('keydown.enter', entrar)
            ui.button('Entrar', on_click=entrar).props('unelevated no-caps').classes('w-full q-mt-sm')
        ui.label('Acesso só para membros da Câmara. Sem conta? Fale com o backoffice.').classes(
            'text-caption text-grey-7 text-center q-mt-sm'
        )


@ui.page('/sair')
def sair():
    app.storage.user.clear()
    return RedirectResponse('/login')
