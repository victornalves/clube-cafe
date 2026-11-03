"""Tema, cabeçalho e proteção de página. Tudo em ui/ é descartável; ver docs/plano-mvp.md."""

import inspect
from collections.abc import Callable
from contextlib import contextmanager

from fastapi.responses import RedirectResponse
from nicegui import app, ui

from app.db import sessao
from app.domain.models import Papel, Usuario
from app.services import auth

CORES = {
    'primary': '#3F5B2E',  # verde da folha e do nome
    'secondary': '#6B4423',  # marrom do grão
    'accent': '#A8743A',  # caramelo da folha
    'dark': '#2E2A24',
}
FUNDO = '#FAF8F3'

MENU = {
    Papel.MEMBRO: [('Meus registros', '/'), ('Minha conta', '/conta')],
    Papel.OPERADOR: [
        ('Membros', '/backoffice/membros'),
        ('Todos os registros', '/backoffice/registros'),
        ('Pendências', '/backoffice/pendencias'),
        ('Auditoria', '/backoffice/auditoria'),
    ],
}
INICIO = {Papel.MEMBRO: '/', Papel.OPERADOR: '/backoffice/registros'}

ui.add_head_html(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&display=swap" rel="stylesheet">'
    f'<style>body {{ background: {FUNDO}; }} .marca {{ font-family: "Cormorant Garamond", serif; letter-spacing: .04em; }}'
    ' .q-stepper__step-inner { padding: 0 !important; }</style>',
    shared=True,
)


def usuario_logado() -> Usuario | None:
    usuario_id = app.storage.user.get('usuario_id')
    if usuario_id is None:
        return None
    with sessao() as s:
        return auth.buscar(s, usuario_id)


def pagina(rota: str, papel: Papel, titulo: str):
    """Página protegida. Sem login vai para /login; com o papel errado, para o início do próprio papel."""

    def decorador(conteudo: Callable[..., None]):
        def pagina_protegida(*args, **kwargs):
            usuario = usuario_logado()
            if usuario is None:
                return RedirectResponse('/login')
            if usuario.papel != papel:
                return RedirectResponse(INICIO[usuario.papel])
            with layout(usuario):
                conteudo(usuario, *args, **kwargs)

        # O FastAPI lê a assinatura para os parâmetros de rota; o usuário não é um deles
        assinatura = inspect.signature(conteudo)
        pagina_protegida.__signature__ = assinatura.replace(parameters=list(assinatura.parameters.values())[1:])
        pagina_protegida.__name__ = conteudo.__name__
        return ui.page(rota, title=f'{titulo} · Clube do Café')(pagina_protegida)

    return decorador


def marca(tamanho: str = 'text-h6'):
    with ui.row().classes('items-center no-wrap gap-2'):
        ui.image('/static/simbolo.png').classes('w-9 h-9')
        ui.label('Clube do Café').classes(f'marca {tamanho} text-primary')


@contextmanager
def layout(usuario: Usuario):
    ui.colors(**CORES)
    backoffice = usuario.papel != Papel.MEMBRO
    with ui.header().classes('bg-white text-dark shadow-1 q-px-md q-py-sm items-center'):
        marca()
        if backoffice:
            ui.badge('Backoffice', color='secondary').classes('q-ml-sm')
        ui.space()
        with ui.row().classes('items-center gap-1 gt-xs'):
            for rotulo, destino in MENU[usuario.papel]:
                ui.button(rotulo, on_click=lambda d=destino: ui.navigate.to(d)).props('flat no-caps color=primary')
        with ui.button(icon='account_circle').props('flat round color=primary'), ui.menu():
            ui.menu_item(usuario.nome).props('disable')
            for rotulo, destino in MENU[usuario.papel]:
                ui.menu_item(rotulo, on_click=lambda d=destino: ui.navigate.to(d)).classes('lt-sm')
            ui.menu_item('Sair', on_click=lambda: ui.navigate.to('/sair'))
    with ui.column().classes('w-full max-w-5xl mx-auto q-pa-md gap-4'):
        yield


def titulo_pagina(texto: str, subtitulo: str | None = None):
    with ui.column().classes('gap-0'):
        ui.label(texto).classes('text-h5 text-weight-medium')
        if subtitulo:
            ui.label(subtitulo).classes('text-body2 text-grey-8')
