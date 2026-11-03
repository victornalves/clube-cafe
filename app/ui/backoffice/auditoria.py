"""Telas 17 e simulador da B3."""

from nicegui import ui

from app.db import sessao
from app.domain.models import Papel, Usuario
from app.services import b3, eventos
from app.ui.componentes import notificar_erros
from app.ui.tema import pagina, titulo_pagina

COLUNAS = [
    {'name': 'quando', 'label': 'Quando', 'field': 'quando', 'align': 'left'},
    {'name': 'quem', 'label': 'Quem', 'field': 'quem', 'align': 'left'},
    {'name': 'onde', 'label': 'Registro / cadastro', 'field': 'onde', 'align': 'left'},
    {'name': 'tipo', 'label': 'Evento', 'field': 'tipo', 'align': 'left'},
    {'name': 'descricao', 'label': 'Descrição', 'field': 'descricao', 'align': 'left', 'style': 'white-space: normal'},
]


@pagina('/backoffice/auditoria', Papel.OPERADOR, 'Auditoria')
def tela_auditoria(operador: Usuario):
    with sessao() as s:
        log = eventos.listar(s, operador)
    titulo_pagina(
        'Auditoria', 'Log de eventos, append-only: nenhum papel altera ou apaga uma linha. Mais recente primeiro.'
    )
    busca = ui.input(placeholder='Filtrar por registro, pessoa, evento ou texto').props('outlined dense clearable')
    busca.classes('w-full sm:w-96')
    linhas = [
        {
            'id': e.id,
            'quando': e.momento.astimezone().strftime('%d/%m/%Y %H:%M:%S'),
            'quem': nome or 'Sistema',
            'onde': numero or f'{e.entidade} #{e.entidade_id}',
            'tipo': e.tipo,
            'descricao': e.descricao,
        }
        for e, nome, numero in log
    ]
    tabela = ui.table(columns=COLUNAS, rows=linhas, row_key='id', pagination=50).props('flat bordered dense')
    tabela.classes('w-full')
    tabela.bind_filter_from(busca, 'value')


@pagina('/backoffice/simulador-b3', Papel.OPERADOR, 'Simulador da B3')
def tela_simulador(operador: Usuario):
    with sessao() as s:
        atual = b3.modo_simulador(s)
    titulo_pagina(
        'Simulador da B3',
        'Só para demonstração. Define o que a B3 simulada responde nos próximos envios, até mudar de novo.',
    )
    with ui.card().classes('w-full'):
        modo = ui.radio(b3.MODOS_SIMULADOR, value=atual)

        def salvar():
            def gravar():
                with sessao() as s:
                    b3.definir_modo_simulador(s, operador, modo.value)

            if notificar_erros(gravar):
                ui.notify('Simulador atualizado.', type='positive')

        with ui.row().classes('w-full justify-end'):
            ui.button('Salvar', on_click=salvar).props('unelevated no-caps')
    ui.label(
        'O envio automático tenta até 3 vezes (CLUBE_TENTATIVAS_AUTOMATICAS_B3) e consulta a B3 antes de cada '
        'reenvio. Esgotadas as tentativas, ou numa recusa definitiva, o registro vai para Pendências.'
    ).classes('text-caption text-grey-7')
