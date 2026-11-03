"""Telas 14 e 16: todos os registros e o detalhe do backoffice, com a resolução de falha na B3."""

import json

from nicegui import ui

from app.db import sessao
from app.domain.estados import NOME_INTERNO, VISAO_MEMBRO, Estado
from app.domain.formatos import formatar_inteiro
from app.domain.models import EnvioB3, Papel, Registro, Usuario
from app.services import b3, envelopes, eventos, registros
from app.services.b3 import Prazo
from app.services.erros import NaoEncontrado
from app.ui.componentes import bloco, detalhes_registro, notificar_erros, selo_estado, valor_total
from app.ui.membro.detalhe import assinaturas_envelope, documentos_envelope, hora
from app.ui.tema import pagina, titulo_pagina

COLUNAS = [
    {'name': 'numero', 'label': 'Número', 'field': 'numero', 'align': 'left', 'sortable': True},
    {'name': 'vendedor', 'label': 'Vendedor', 'field': 'vendedor', 'align': 'left', 'sortable': True},
    {'name': 'comprador', 'label': 'Comprador', 'field': 'comprador', 'align': 'left', 'sortable': True},
    {'name': 'sacas', 'label': 'Sacas', 'field': 'sacas', 'align': 'right'},
    {'name': 'valor', 'label': 'Valor total', 'field': 'valor', 'align': 'right'},
    {'name': 'interno', 'label': 'Situação interna', 'field': 'interno', 'align': 'left', 'sortable': True},
    {'name': 'membro', 'label': 'Membro vê', 'field': 'membro', 'align': 'left'},
    {'name': 'atualizado', 'label': 'Atualizado', 'field': 'atualizado', 'align': 'left', 'sortable': True},
]


def _linha(r: Registro) -> dict:
    return {
        'id': r.id,
        'numero': r.numero,
        'vendedor': r.vendedor.nome,
        'comprador': r.comprador.nome,
        'sacas': formatar_inteiro(r.sacas) if r.sacas else '—',
        'valor': valor_total(r),
        'estado': r.estado.value,
        'interno': NOME_INTERNO[r.estado],
        'membro': VISAO_MEMBRO[r.estado],
        'atualizado': r.atualizado_em.astimezone().strftime('%d/%m/%Y %H:%M'),
    }


@pagina('/backoffice/registros', Papel.OPERADOR, 'Todos os registros')
def todos(operador: Usuario):
    with sessao() as s:
        linhas = [_linha(r) for r in registros.listar(s, operador)]

    titulo_pagina(
        'Todos os registros',
        'Contratos de todos os membros. Aqui a situação aparece completa, não a versão simplificada que o membro vê.',
    )
    with ui.row().classes('w-full items-center gap-4'):
        situacao = (
            ui.select({'': 'Todas', **{e.value: NOME_INTERNO[e] for e in Estado}}, value='', label='Situação interna')
            .props('outlined dense')
            .classes('w-60')
        )
        busca = ui.input(placeholder='Buscar por número ou membro').props('outlined dense clearable').classes('w-72')
        contagem = ui.label().classes('text-caption text-grey-7')

    tabela = ui.table(columns=COLUNAS, rows=linhas, row_key='id', pagination=25).props('flat bordered')
    tabela.classes('w-full cursor-pointer')
    tabela.bind_filter_from(busca, 'value')
    tabela.on('rowClick', lambda e: ui.navigate.to(f'/backoffice/registros/{e.args[1]["id"]}'))

    def filtrar():
        tabela.rows = [r for r in linhas if not situacao.value or r['estado'] == situacao.value]
        contagem.text = f'{len(tabela.rows)} de {len(linhas)} registros'

    situacao.on_value_change(filtrar)
    filtrar()


def bloco_prazo(prazo: Prazo | None, estado: Estado):
    if prazo is None or estado in (Estado.REGISTRADO, Estado.CANCELADO):
        return
    cor = 'negative' if prazo.dias_uteis_restantes <= 5 else 'accent'
    with bloco('Prazo legal'):
        with ui.row().classes('items-center gap-3'):
            ui.badge(f'Restam {prazo.dias_uteis_restantes} dias úteis', color=cor).classes('text-body2 q-px-sm')
            ui.label(f'Emitida em {prazo.emissao:%d/%m/%Y} · vence em {prazo.limite:%d/%m/%Y} (30 dias úteis)').classes(
                'text-body2'
            )
        ui.label(
            'Passado o limite, a CPR perde a validade. Enquanto isso, o membro vê "Em processamento" e não sabe '
            'que o prazo está correndo.'
        ).classes('text-caption text-grey-7')


def _executar(fn, sucesso: str) -> bool:
    if notificar_erros(fn):
        ui.notify(sucesso, type='positive')
        ui.navigate.reload()
        return True
    return False


def bloco_resolucao(operador: Usuario, registro: Registro, ultimo: EnvioB3 | None):
    if registro.estado not in (Estado.FALHA_B3, Estado.EM_CORRECAO):
        return

    def acao(fn, *args):
        def executar():
            with sessao() as s:
                fn(s, operador, registro.id, *args)

        return executar

    def confirmar_reenvio():
        with ui.dialog() as dialogo, ui.card().classes('max-w-lg'):
            ui.label('Reenviar à B3').classes('text-h6')
            ui.label(
                'Antes de reenviar, o sistema consulta a B3. Se a CPR já estiver lá (o envio anterior pode ter '
                'chegado mesmo com erro), o registro é confirmado sem mandar de novo. Assim não há CPR duplicada.'
            ).classes('text-body2')
            with ui.row().classes('w-full justify-end'):
                ui.button('Voltar', on_click=dialogo.close).props('flat no-caps')
                ui.button(
                    'Consultar e reenviar',
                    on_click=lambda: (dialogo.close(), _executar(acao(b3.reenviar), 'Reenvio concluído.')),
                ).props('unelevated no-caps')
        dialogo.open()

    def confirmar_cancelamento():
        with ui.dialog() as dialogo, ui.card().classes('w-full max-w-lg'):
            ui.label('Cancelar o registro').classes('text-h6')
            ui.label(
                'O contrato já foi assinado pelas partes. Cancelar encerra o registro sem efeito na B3; '
                'as partes veem "Cancelado". Use só quando reenviar não resolve.'
            ).classes('text-body2')
            motivo = ui.textarea('Motivo (obrigatório, vai para o log)').props('outlined').classes('w-full')
            with ui.row().classes('w-full justify-end'):
                ui.button('Voltar', on_click=dialogo.close).props('flat no-caps')

                def cancelar():
                    if _executar(acao(b3.cancelar, motivo.value), 'Registro cancelado.'):
                        dialogo.close()

                ui.button('Cancelar registro', on_click=cancelar).props('unelevated no-caps color=negative')
        dialogo.open()

    with bloco('Resolver a falha'):
        if ultimo:
            ui.label(f'Última resposta da B3: {ultimo.status_http} · {ultimo.mensagem}').classes(
                'text-subtitle1 text-negative'
            )
        if registro.estado == Estado.FALHA_B3:
            ui.label('Ninguém assumiu ainda. Assuma para liberar as ações de resolução.').classes('text-body2')
            with ui.row().classes('w-full justify-end'):
                ui.button(
                    'Assumir a correção',
                    icon='assignment_ind',
                    on_click=lambda: _executar(acao(b3.assumir), 'Correção assumida.'),
                ).props('unelevated no-caps')
        else:
            responsavel = registro.responsavel.nome if registro.responsavel else '—'
            ui.label(f'Responsável: {responsavel}').classes('text-body2')
            ui.label(
                'Corrigir o envio (payload) e pedir reassinatura são os outros dois caminhos; entram depois do MVP.'
            ).classes('text-caption text-grey-7')
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancelar registro', on_click=confirmar_cancelamento).props('flat no-caps color=negative')
                ui.button('Reenviar à B3', icon='send', on_click=confirmar_reenvio).props('unelevated no-caps')


def bloco_envios(lista: list[EnvioB3]):
    if not lista:
        return
    with bloco('Comunicação com a B3'):
        for envio in lista:
            quem = 'automático' if envio.automatico else 'pelo operador'
            cor = {'sucesso': 'primary', 'encontrado': 'primary', 'nao_encontrado': 'grey-7'}.get(
                envio.resultado, 'negative'
            )
            titulo = f'{hora(envio.momento)} · {envio.operacao} {quem} · {envio.status_http} · {envio.mensagem}'
            with ui.expansion(titulo, icon='swap_horiz').classes(f'w-full text-{cor}').props('dense'):
                if envio.payload:
                    ui.label('Payload').classes('text-caption text-grey-7')
                    ui.code(json.dumps(envio.payload, indent=2, ensure_ascii=False), language='json').classes('w-full')
                ui.label('Resposta').classes('text-caption text-grey-7')
                ui.code(json.dumps(envio.resposta, indent=2, ensure_ascii=False), language='json').classes('w-full')


@pagina('/backoffice/registros/{registro_id}', Papel.OPERADOR, 'Registro')
def detalhe(operador: Usuario, registro_id: int):
    try:
        with sessao() as s:
            registro = registros.obter(s, operador, registro_id)
            _ = registro.responsavel  # carrega antes de fechar a sessão
            lista = b3.envios(s, operador, registro_id)
            linha = eventos.do_registro(s, operador, registro_id)
            prazo = b3.prazo_legal(registro)
    except NaoEncontrado:
        titulo_pagina('Registro não encontrado')
        return
    retrato = (registro.estado, len(lista))

    with ui.row().classes('w-full items-center gap-2'):
        ui.link('Todos os registros', '/backoffice/registros').classes('text-primary')
        ui.label('›').classes('text-grey-6')
        ui.label(registro.numero).classes('text-grey-8')
    with ui.row().classes('w-full items-center justify-between'):
        titulo_pagina(f'Registro {registro.numero}', f'{registro.vendedor.nome} → {registro.comprador.nome}')
        with ui.column().classes('items-end gap-1'):
            selo_estado(registro.estado, interno=True)
            ui.label(f'Membro vê: {VISAO_MEMBRO[registro.estado]}').classes('text-caption text-grey-7')

    bloco_prazo(prazo, registro.estado)
    bloco_resolucao(operador, registro, lista[-1] if lista else None)
    if registro.numero_controle_b3:
        with bloco('Registrado na B3'):
            ui.label(f'Número de controle {registro.numero_controle_b3}, em {hora(registro.registrado_em)}')
    bloco_envios(lista)

    envelope = envelopes.atual(registro)
    if envelope:
        with bloco(f'Envelope (versão {envelope.versao})'):
            documentos_envelope(envelope)
            assinaturas_envelope(envelope)

    with bloco('Linha do tempo completa'), ui.column().classes('gap-3 w-full'):
        for evento, nome in linha:
            with ui.row().classes('no-wrap items-start gap-3'):
                ui.icon('circle', size='10px', color='secondary').classes('q-mt-sm')
                with ui.column().classes('gap-0'):
                    ui.label(evento.descricao).classes('text-body2')
                    ui.label(f'{hora(evento.momento)} · {nome or "Sistema"} · {evento.tipo}').classes(
                        'text-caption text-grey-7'
                    )
    detalhes_registro(registro)

    def acompanhar():
        with sessao() as s:
            atual = registros.obter(s, operador, registro_id)
            agora = (atual.estado, len(b3.envios(s, operador, registro_id)))
        if agora != retrato:
            ui.navigate.reload()

    ui.timer(3, acompanhar)
