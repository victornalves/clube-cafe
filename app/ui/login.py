from fastapi.responses import RedirectResponse
from nicegui import app, ui

from app.db import sessao
from app.services import auth
from app.ui.tema import CORES, INICIO, entrar_como, marca_destaque, usuario_logado


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

    with ui.column().classes('items-center justify-center w-full max-w-3xl mx-auto q-px-md q-py-xl min-h-screen'):
        with ui.column().classes('items-center q-mb-lg'):
            marca_destaque()
        with ui.card().classes('w-full max-w-sm q-pa-lg'):
            email = ui.input('E-mail').props('outlined type=email autocomplete=username').classes('w-full')
            senha = ui.input('Senha', password=True).props('outlined autocomplete=current-password').classes('w-full')
            senha.on('keydown.enter', entrar)
            ui.button('Entrar', on_click=entrar).props('unelevated no-caps').classes('w-full q-mt-sm')
        with ui.row().classes('items-center gap-1 q-mt-sm'):
            ui.label('Ainda não é membro?').classes('text-caption text-grey-7')
            ui.link('Propor adesão à Câmara', '/adesao').classes('text-caption text-primary')
        if auth.login_demo_ligado():
            personas_demo()


def personas_demo():
    """Tudo é simulado: entrar como qualquer pessoa do roteiro, sem senha."""
    with ui.column().classes('w-full items-center gap-2 q-mt-lg'):
        with ui.row().classes('w-full items-center no-wrap gap-3'):
            ui.separator().classes('col')
            ui.label('Demonstração · entrar como').classes('text-caption text-grey-7')
            ui.separator().classes('col')
        with ui.element('div').classes('grid grid-cols-2 sm:grid-cols-4 gap-2 w-full'):
            for email, nome, descricao in auth.PERSONAS_DEMO:
                backoffice = email.endswith('@backoffice.demo')
                cor = 'secondary' if backoffice else 'primary'
                botao = ui.button(on_click=lambda e=email: entrar_como(e)).props(f'outline no-caps color={cor}')
                with botao, ui.column().classes('items-start gap-0 w-full'):
                    ui.label(nome).classes('text-weight-medium')
                    ui.label(descricao).classes('text-caption text-grey-8 text-left')
        # Fluxo de adesão: o candidato não tem login, e os links chegam por e-mail (simulado)
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-2 w-full q-mt-sm'):
            for rotulo, descricao, destino, icone in [
                ('Propor adesão', 'Como candidato, sem login', '/adesao', 'person_add'),
                ('E-mails enviados', 'Links de assinatura, diligência e senha', '/emails', 'inbox'),
            ]:
                botao = ui.button(icon=icone, on_click=lambda d=destino: ui.navigate.to(d))
                botao.props('outline no-caps color=accent align=left')
                with botao, ui.column().classes('items-start gap-0'):
                    ui.label(rotulo).classes('text-weight-medium')
                    ui.label(descricao).classes('text-caption text-grey-8 text-left')


@ui.page('/sair')
def sair():
    app.storage.user.clear()
    return RedirectResponse('/login')
