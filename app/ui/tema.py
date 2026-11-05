"""Tema, cabeçalho e proteção de página. Tudo em ui/ é descartável; ver docs/plano-mvp.md."""

import inspect
from collections.abc import Callable
from contextlib import contextmanager

from fastapi.responses import RedirectResponse
from nicegui import app, ui

from app.db import sessao
from app.domain.models import Papel, Usuario
from app.services import adesao, auth

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
        ('Propostas', '/backoffice/propostas'),
        ('Membros', '/backoffice/membros'),
        ('Todos os registros', '/backoffice/registros'),
        ('Pendências', '/backoffice/pendencias'),
        ('Auditoria', '/backoffice/auditoria'),
        ('Simulador B3', '/backoffice/simulador-b3'),
    ],
}
INICIO = {Papel.MEMBRO: '/', Papel.OPERADOR: '/backoffice/registros'}

ui.add_head_html(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&display=swap" rel="stylesheet">'
    f'<style>body {{ background: {FUNDO}; }}'
    # Logotipo: nome em versalete serifado, como na logo da Câmara
    ' .marca { font-family: "Cormorant Garamond", serif; font-weight: 600; text-transform: uppercase;'
    ' letter-spacing: .1em; line-height: 1.15; color: #3F5B2E; }'
    # No celular o nome do cabeçalho quebra em duas linhas, para o ícone da conta caber ao lado
    ' .marca-cabecalho { font-size: 13px; letter-spacing: .06em; min-width: 0; }'
    ' .marca-destaque { font-size: 19px; text-align: center; text-wrap: balance; }'
    ' .marca-fio { height: 1px; width: 56px; background: #6B4423; flex: none; }'
    ' @media print { .q-header, .nao-imprimir { display: none !important; } .q-page-container { padding-top: 0 !important; } }'
    ' @media (min-width: 600px) {'
    ' .marca-cabecalho { font-size: 17px; letter-spacing: .1em; white-space: nowrap; }'
    ' .marca-destaque { font-size: 25px; white-space: nowrap; } }'
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
            # Membro aprovado assina os termos antes de qualquer outra tela (RN-114)
            if rota != '/termos':
                with sessao() as s:
                    if adesao.precisa_assinar_termos(s, usuario):
                        return RedirectResponse('/termos')
            with layout(usuario):
                conteudo(usuario, *args, **kwargs)

        # O FastAPI lê a assinatura para os parâmetros de rota; o usuário não é um deles
        assinatura = inspect.signature(conteudo)
        pagina_protegida.__signature__ = assinatura.replace(parameters=list(assinatura.parameters.values())[1:])
        pagina_protegida.__name__ = conteudo.__name__
        return ui.page(rota, title=f'{titulo} · {NOME}')(pagina_protegida)

    return decorador


NOME = 'Câmara do Comércio de Café'


def marca():
    """Logotipo do cabeçalho: símbolo e nome numa linha."""
    with ui.row().classes('items-center no-wrap gap-3 min-w-0'):
        ui.image('/static/simbolo.png').classes('w-9 h-9 flex-none')
        ui.label(NOME).classes('marca marca-cabecalho')


def marca_destaque():
    """Logotipo completo, como na logo: símbolo grande e o nome entre dois fios."""
    with ui.column().classes('items-center gap-4'):
        ui.image('/static/simbolo.png').classes('w-28 h-28')
        with ui.row().classes('items-center no-wrap gap-4'):
            ui.element('div').classes('marca-fio gt-xs')
            ui.label(NOME).classes('marca marca-destaque')
            ui.element('div').classes('marca-fio gt-xs')


def entrar_como(email: str):
    """Login de demonstração: troca de pessoa num clique (CLUBE_LOGIN_DEMO)."""
    with sessao() as s:
        usuario = auth.autenticar_demo(s, email)
    if usuario is None:
        ui.notify('Usuário de demonstração não encontrado. Rode scripts.seed ou scripts.demo.', type='warning')
        return
    app.storage.user['usuario_id'] = usuario.id
    ui.navigate.to(INICIO[usuario.papel])


@contextmanager
def layout(usuario: Usuario):
    ui.colors(**CORES)
    backoffice = usuario.papel != Papel.MEMBRO
    with ui.header().classes('bg-white text-dark shadow-1 q-px-md q-py-sm items-center no-wrap'):
        marca()
        if backoffice:
            ui.badge('Backoffice', color='secondary').classes('q-ml-sm gt-xs')
        ui.space()
        with ui.row().classes('items-center gap-1 gt-xs'):
            for rotulo, destino in MENU[usuario.papel]:
                ui.button(rotulo, on_click=lambda d=destino: ui.navigate.to(d)).props('flat no-caps color=primary')
        with ui.button(icon='account_circle').props('flat round color=primary'), ui.menu():
            ui.menu_item(usuario.nome).props('disable')
            for rotulo, destino in MENU[usuario.papel]:
                ui.menu_item(rotulo, on_click=lambda d=destino: ui.navigate.to(d)).classes('lt-sm')
            if auth.login_demo_ligado():
                ui.separator()
                ui.menu_item('Entrar como (demonstração)').props('disable')
                for email, nome, descricao in auth.PERSONAS_DEMO:
                    if email != usuario.email:
                        ui.menu_item(f'{nome} · {descricao}', on_click=lambda e=email: entrar_como(e))
                ui.separator()
            ui.menu_item('Sair', on_click=lambda: ui.navigate.to('/sair'))
    # Backoffice trabalha com tabelas largas; o membro, com leitura em coluna
    largura = 'max-w-7xl' if backoffice else 'max-w-5xl'
    with ui.column().classes(f'w-full {largura} mx-auto q-pa-md gap-4'):
        yield


@contextmanager
def layout_publico():
    """Páginas sem login: proposta de adesão, links recebidos por e-mail, caixa de e-mails simulada."""
    ui.colors(**CORES)
    with ui.header().classes('bg-white text-dark shadow-1 q-px-md q-py-sm items-center no-wrap'):
        with ui.link(target='/login').classes('no-underline'):
            marca()
        ui.space()
        ui.button('Entrar', on_click=lambda: ui.navigate.to('/login')).props('flat no-caps color=primary')
    with ui.column().classes('w-full max-w-3xl mx-auto q-pa-md gap-4'):
        yield


def aviso_simulado(texto: str):
    with (
        ui.card().classes('w-full bg-orange-1 q-pa-sm').props('flat bordered'),
        ui.row().classes('no-wrap items-start gap-2'),
    ):
        ui.icon('science', color='secondary').classes('q-mt-xs')
        ui.label(texto).classes('text-body2 text-secondary')


def titulo_pagina(texto: str, subtitulo: str | None = None):
    with ui.column().classes('gap-0'):
        ui.label(texto).classes('text-h5 text-weight-medium')
        if subtitulo:
            ui.label(subtitulo).classes('text-body2 text-grey-8')
