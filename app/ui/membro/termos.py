"""Tela 03b: o membro aprovado assina os termos da Câmara no primeiro acesso (RN-114, RN-134)."""

from nicegui import ui

from app.db import sessao
from app.domain.models import Papel, Usuario
from app.services import adesao
from app.services.adesao import VERSAO_TERMOS
from app.ui.componentes import notificar_erros
from app.ui.tema import aviso_simulado, pagina, titulo_pagina

CLAUSULAS = [
    (
        'Ao aceitar este termo, o membro concorda que toda transação registrada nesta plataforma está sujeita às '
        'regras da empresa administradora da Câmara do Comércio de Café, conforme definidas neste documento e em '
        'seus anexos.'
    ),
    (
        'O membro reconhece que a Câmara opera com Cédulas de Produto Rural físicas, registradas junto à B3 sob a '
        'conta do escritório de advocacia parceiro, na qualidade de Agente de Registro.'
    ),
    '[Demais cláusulas padrão da Câmara: qualidade aceita, forma de assinatura, foro, tratamento de dados.]',
    'Alterações deste termo são comunicadas ao membro por circular, pela plataforma e por e-mail.',
]


@pagina('/termos', Papel.MEMBRO, 'Termos da Câmara')
def termos(usuario: Usuario):
    with sessao() as s:
        pendente = adesao.precisa_assinar_termos(s, usuario)
    titulo_pagina(
        'Bem-vindo à Câmara',
        'Antes de criar ou assinar qualquer registro, leia e assine os termos da Câmara. É uma assinatura só, '
        'e vale para todas as suas operações futuras.',
    )
    with ui.card().classes('w-full'):
        ui.label(f'Termo de Adesão — Câmara do Comércio de Café · versão {VERSAO_TERMOS} (simulada)').classes(
            'text-subtitle1 text-weight-medium text-primary'
        )
        aviso_simulado('Texto simulado. O termo definitivo vem do escritório jurídico.')
        for i, clausula in enumerate(CLAUSULAS, start=1):
            ui.label(f'{i}. {clausula}').classes('text-body2')

    if not pendente:
        ui.label('Você já assinou os termos.').classes('text-grey-8')
        ui.button('Ir para meus registros', on_click=lambda: ui.navigate.to('/')).props('unelevated no-caps')
        return

    with ui.card().classes('w-full'):
        li = ui.checkbox(f'Li o termo de adesão inteiro, na versão {VERSAO_TERMOS}.')
        aviso_simulado('Assinatura simulada. Na versão final, você assina com o seu certificado digital.')

        def assinar():
            def gravar():
                with sessao() as s:
                    adesao.assinar_termos(s, usuario)

            if notificar_erros(gravar):
                ui.notify('Termos assinados. Bem-vindo!', type='positive')
                ui.navigate.to('/')

        ui.button('Assinar (simulado) e entrar', icon='draw', on_click=assinar).props(
            'unelevated no-caps'
        ).bind_enabled_from(li, 'value')
