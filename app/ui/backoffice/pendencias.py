"""Tela 15: falhas na B3 que esperam uma pessoa, ordenadas pelo prazo legal."""

from datetime import UTC, datetime

from nicegui import ui

from app.db import sessao
from app.domain.models import Papel, Usuario
from app.services import b3
from app.ui.componentes import valor_total
from app.ui.tema import pagina, titulo_pagina

COLUNAS = [
    {'name': 'prazo', 'label': 'Prazo legal', 'field': 'prazo', 'align': 'left'},
    {'name': 'numero', 'label': 'Número', 'field': 'numero', 'align': 'left'},
    {'name': 'membro', 'label': 'Vendedor', 'field': 'membro', 'align': 'left'},
    {'name': 'valor', 'label': 'Valor', 'field': 'valor', 'align': 'right'},
    {'name': 'resposta', 'label': 'Última resposta da B3', 'field': 'resposta', 'align': 'left'},
    {'name': 'tentativas', 'label': 'Tentativas', 'field': 'tentativas', 'align': 'right'},
    {'name': 'parado', 'label': 'Parado há', 'field': 'parado', 'align': 'left'},
    {'name': 'responsavel', 'label': 'Responsável', 'field': 'responsavel', 'align': 'left'},
]


def _tempo(desde: datetime | None) -> str:
    if desde is None:
        return '—'
    minutos = int((datetime.now(UTC) - desde).total_seconds() // 60)
    if minutos < 60:
        return f'{minutos} min'
    if minutos < 60 * 24:
        return f'{minutos // 60} h'
    return f'{minutos // (60 * 24)} dias'


@pagina('/backoffice/pendencias', Papel.OPERADOR, 'Pendências')
def tela_pendencias(operador: Usuario):
    with sessao() as s:
        fila = b3.pendencias(s, operador)

    titulo_pagina(
        'Pendências',
        'Contratos cujo registro na B3 falhou e precisam de decisão de uma pessoa. '
        'Ordenados pelo prazo legal: quem vence primeiro aparece primeiro.',
    )
    if not fila:
        with ui.card().classes('w-full items-center q-pa-xl'):
            ui.icon('task_alt', size='xl', color='primary')
            ui.label('Nenhum contrato parado.').classes('text-grey-8')
        return

    urgente = fila[0].prazo.dias_uteis_restantes
    ui.label(f'{len(fila)} contrato(s) parado(s) · o mais urgente vence em {urgente} dias úteis').classes(
        'text-subtitle1 text-weight-medium ' + ('text-negative' if urgente <= 5 else 'text-accent')
    )
    linhas = [
        {
            'id': p.registro.id,
            'prazo': f'Restam {p.prazo.dias_uteis_restantes} dias úteis',
            'vence': f'{p.prazo.limite:%d/%m/%Y}',
            'urgente': p.prazo.dias_uteis_restantes <= 5,
            'numero': p.registro.numero,
            'membro': p.registro.vendedor.nome,
            'valor': valor_total(p.registro),
            'resposta': f'{p.ultimo_envio.status_http} · {p.ultimo_envio.mensagem}' if p.ultimo_envio else '—',
            'tentativas': p.tentativas,
            'parado': _tempo(p.ultimo_envio.momento if p.ultimo_envio else None),
            'responsavel': p.registro.responsavel.nome if p.registro.responsavel else 'ninguém',
        }
        for p in fila
    ]
    tabela = ui.table(columns=COLUNAS, rows=linhas, row_key='id').props('flat bordered').classes('w-full')
    tabela.classes('cursor-pointer')
    tabela.add_slot(
        'body-cell-prazo',
        """<q-td :props="props">
             <q-badge :color="props.row.urgente ? 'negative' : 'accent'" :label="props.value" />
             <div class="text-caption text-grey-7">vence {{ props.row.vence }}</div>
           </q-td>""",
    )
    tabela.on('rowClick', lambda e: ui.navigate.to(f'/backoffice/registros/{e.args[1]["id"]}'))
    ui.label('Clique numa linha para resolver.').classes('text-caption text-grey-7')
