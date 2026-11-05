"""Telas 12, 12b, 12c e 13: propostas de adesão no backoffice. O comitê decide fora; o backoffice materializa."""

from datetime import UTC, date, datetime, timedelta

from fastapi import Response
from fastapi.responses import RedirectResponse
from nicegui import app, ui

from app.db import sessao
from app.domain import adesao as dominio
from app.domain.adesao import SituacaoProposta as S
from app.domain.formatos import formatar_documento, formatar_inteiro, formatar_telefone
from app.domain.models import Papel, PropostaAdesao, TipoPessoa, Usuario
from app.services import adesao, emails, eventos
from app.services.adesao import DadosDecisao
from app.services.erros import AcessoNegado, NaoEncontrado
from app.ui.componentes import bloco, campo, notificar_erros
from app.ui.tema import aviso_simulado, pagina, titulo_pagina, usuario_logado

COR = {
    S.AGUARDANDO_ASSINATURAS: 'grey-7',
    S.ASSINATURA_RECUSADA: 'grey-5',
    S.EXPIRADA: 'grey-5',
    S.EM_FILA_COMITE: 'accent',
    S.EM_DILIGENCIA: 'secondary',
    S.APROVADA: 'primary',
    S.RECUSADA: 'negative',
}


def _hora(momento) -> str:
    return momento.astimezone().strftime('%d/%m/%Y %H:%M') if momento else '—'


def _ha(momento) -> str:
    dias = (datetime.now(UTC) - momento).days
    return 'hoje' if dias == 0 else f'{dias} dia(s)'


def selo(situacao: str):
    s = S(situacao)
    ui.badge(dominio.ROTULO[s], color=COR[s]).classes('text-body2 q-px-sm')


def _vinculo(sig) -> str:
    if sig.membro_id:
        return f'membro desde {sig.membro.membro_desde:%m/%Y}'
    return 'de fora da Câmara'


def _proponentes(p: PropostaAdesao) -> str:
    membros = sum(1 for x in p.proponentes() if x.membro_id)
    return {2: '2 membros', 1: '1 membro, 1 externo', 0: '2 externos'}[membros]


def _tabela(titulo: str, explicacao: str | None, colunas: list[tuple[str, str]], linhas: list[dict]):
    with ui.column().classes('w-full gap-1'):
        ui.label(f'{titulo} ({len(linhas)})').classes('text-subtitle1 text-weight-medium text-primary')
        if explicacao:
            ui.label(explicacao).classes('text-caption text-grey-7')
        if not linhas:
            ui.label('Nenhuma.').classes('text-body2 text-grey-6 q-mb-sm')
            return
        cols = [{'name': c, 'label': rotulo, 'field': c, 'align': 'left'} for c, rotulo in colunas]
        tabela = ui.table(columns=cols, rows=linhas, row_key='id').props('flat bordered dense').classes('w-full')
        tabela.classes('cursor-pointer')
        tabela.on('rowClick', lambda e: ui.navigate.to(f'/backoffice/propostas/{e.args[1]["id"]}'))


@pagina('/backoffice/propostas', Papel.OPERADOR, 'Propostas de adesão')
def fila(operador: Usuario):
    with sessao() as s:
        todas = adesao.listar(s, operador)
    por = {situacao: [p for p in todas if p.situacao == situacao] for situacao in S}
    limite = datetime.now(UTC) - timedelta(days=30)

    with ui.row().classes('w-full items-end justify-between'):
        titulo_pagina(
            'Propostas de adesão',
            'O comitê de admissão decide na reunião semanal; esta tela organiza o que ele precisa ver e registra a '
            'decisão depois.',
        )
        prontas = len(por[S.EM_FILA_COMITE])
        ui.button(f'Relatório para a reunião ({prontas})', icon='print',
                  on_click=lambda: ui.navigate.to('/backoffice/propostas/relatorio')).props(
            'unelevated no-caps' + ('' if prontas else ' disable'))  # fmt: skip

    def assinatura(sig) -> str:
        return 'Assinou' if sig.assinado_em else ('Recusou' if sig.recusado_em else 'Aguardando')

    _tabela(
        'Prontas para o comitê', 'As 3 assinaturas reunidas.',
        [('numero', 'Número'), ('candidato', 'Candidato'), ('local', 'Propriedade e município'), ('sacas', 'Sacas/safra'),
         ('proponentes', 'Proponentes'), ('ha', 'Na fila há')],
        [{'id': p.id, 'numero': p.numero, 'candidato': p.nome,
          'local': f'{p.propriedade or "—"} · {p.cidade}/{p.uf}',
          'sacas': formatar_inteiro(p.sacas_safra) if p.sacas_safra else '—',
          'proponentes': _proponentes(p), 'ha': _ha(p.atualizado_em)} for p in por[S.EM_FILA_COMITE]],
    )  # fmt: skip
    _tabela(
        'Aguardando assinaturas', 'Candidato e proponentes assinam pelo link recebido por e-mail.',
        [('numero', 'Número'), ('candidato', 'Candidato'), ('c', 'Candidato assinou?'), ('p1', 'Proponente 1'),
         ('p2', 'Proponente 2'), ('vence', 'Link vence em')],
        [{'id': p.id, 'numero': p.numero, 'candidato': p.nome, 'c': assinatura(p.signatarios[0]),
          'p1': assinatura(p.signatarios[1]), 'p2': assinatura(p.signatarios[2]),
          'vence': _hora(p.assinaturas_vencem_em)} for p in por[S.AGUARDANDO_ASSINATURAS]],
    )  # fmt: skip
    _tabela(
        'Em diligência', 'Volta para "prontas" quando o candidato responder.',
        [('numero', 'Número'), ('candidato', 'Candidato'), ('pedido', 'O que foi pedido'), ('ha', 'Pedido há')],
        [{'id': p.id, 'numero': p.numero, 'candidato': p.nome, 'pedido': p.diligencia_pedido,
          'ha': _ha(p.atualizado_em)} for p in por[S.EM_DILIGENCIA]],
    )  # fmt: skip
    nao_seguiram = por[S.ASSINATURA_RECUSADA] + por[S.EXPIRADA]
    _tabela(
        'Não seguiram', 'Proponente recusou ou o prazo venceu. O candidato pode fazer nova proposta.',
        [('numero', 'Número'), ('candidato', 'Candidato'), ('motivo', 'O que aconteceu'), ('quando', 'Quando')],
        [{'id': p.id, 'numero': p.numero, 'candidato': p.nome, 'motivo': dominio.ROTULO[S(p.situacao)],
          'quando': _hora(p.atualizado_em)} for p in nao_seguiram],
    )  # fmt: skip
    decididas = [p for p in por[S.APROVADA] + por[S.RECUSADA] if p.decidido_em and p.decidido_em >= limite]
    _tabela(
        'Decididas nos últimos 30 dias', None,
        [('numero', 'Número'), ('candidato', 'Candidato'), ('decisao', 'Decisão do comitê'),
         ('reuniao', 'Reunião'), ('por', 'Lançado por')],
        [{'id': p.id, 'numero': p.numero, 'candidato': p.nome, 'decisao': dominio.ROTULO[S(p.situacao)],
          'reuniao': f'{p.reuniao_data:%d/%m/%Y}', 'por': p.decidido_por.nome if p.decidido_por else '—'}
         for p in sorted(decididas, key=lambda p: p.decidido_em, reverse=True)],
    )  # fmt: skip


# Registrada antes de /backoffice/propostas/{proposta_id}, que capturaria "relatorio"
@pagina('/backoffice/propostas/relatorio', Papel.OPERADOR, 'Relatório do comitê')
def relatorio(operador: Usuario):
    """Tela 12b: para imprimir e levar à reunião semanal."""
    with sessao() as s:
        prontas = [
            adesao.obter(s, operador, p.id) for p in adesao.listar(s, operador) if p.situacao == S.EM_FILA_COMITE
        ]
        checagens = {p.id: adesao.conferencias(s, p) for p in prontas}
    with ui.row().classes('w-full items-end justify-between'):
        titulo_pagina(
            'Relatório para a reunião do comitê de admissão',
            f'{len(prontas)} proposta(s) prontas · gerado por {operador.nome} em {datetime.now():%d/%m/%Y %H:%M}',
        )
        ui.button('Imprimir', icon='print', on_click=lambda: ui.run_javascript('window.print()')).props(
            'unelevated no-caps'
        ).classes('nao-imprimir')
    for i, p in enumerate(prontas, start=1):
        with bloco(f'{i}. {p.numero} — {p.nome}'):
            with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-3 gap-4 w-full'):
                campo('Propriedade', f'{p.propriedade or "—"} · {p.cidade}/{p.uf}')
                campo('Volume por safra', f'{formatar_inteiro(p.sacas_safra)} sacas' if p.sacas_safra else '')
                campo('Atuação', p.atuacao.value.capitalize())
            for sig in p.proponentes():
                ui.label(f'{dominio.PAPEIS[sig.papel]}: {sig.nome} · {_vinculo(sig)} · carta anexada · '
                         f'assinou em {_hora(sig.assinado_em)}').classes('text-body2')  # fmt: skip
            if p.diligencia_resposta:
                ui.label(f'Diligência: {p.diligencia_pedido} → {p.diligencia_resposta}').classes('text-body2')
            for ok, texto in checagens[p.id]:
                ui.label(('✓ ' if ok else '⚠ ') + texto).classes(
                    'text-caption ' + ('text-grey-8' if ok else 'text-accent')
                )


@app.get('/backoffice/anexos/{anexo_id}')
def baixar_anexo(anexo_id: int):
    usuario = usuario_logado()
    if usuario is None:
        return RedirectResponse('/login')
    try:
        with sessao() as s:
            anexo = adesao.anexo_para_backoffice(s, usuario, anexo_id)
    except (NaoEncontrado, AcessoNegado):
        return Response('Arquivo não encontrado.', status_code=404)
    return Response(
        anexo.conteudo, media_type=anexo.content_type,
        headers={'Content-Disposition': f'inline; filename="{anexo.nome_arquivo}"'},
    )  # fmt: skip


def dados_candidato(p: PropostaAdesao):
    grade = 'grid grid-cols-1 sm:grid-cols-3 gap-4 w-full'
    with bloco('O que o candidato informou'), ui.element('div').classes(grade):
        campo('Nome ou razão social', p.nome)
        campo('CPF ou CNPJ', formatar_documento(p.documento))
        campo('Atuação', p.atuacao.value.capitalize())
        campo('E-mail', p.email)
        campo('Telefone', formatar_telefone(p.telefone))
        campo('Propriedade ou empresa', p.propriedade)
        campo('Município', f'{p.cidade}/{p.uf}')
        campo('Volume por safra', f'{formatar_inteiro(p.sacas_safra)} sacas' if p.sacas_safra else '')
        if p.tipo_pessoa == TipoPessoa.PJ:
            campo(
                'Quem assina pela empresa', f'{p.representante_nome}, {formatar_documento(p.representante_cpf or "")}'
            )
        if p.corretor_nome:
            campo('Preenchida por', f'{p.corretor_nome} (corretor), {p.corretor_email}')


def proponentes(p: PropostaAdesao, com_links: bool = True):
    with bloco('Assinaturas e proponentes'):
        for sig in p.signatarios:
            carta = next((a for a in p.anexos if a.signatario_id == sig.id), None)
            with ui.row().classes('w-full items-start no-wrap gap-2'):
                if sig.assinado_em:
                    ui.icon('check_circle', color='primary').classes('q-mt-xs')
                elif sig.recusado_em:
                    ui.icon('cancel', color='negative').classes('q-mt-xs')
                else:
                    ui.icon('radio_button_unchecked', color='grey-6').classes('q-mt-xs')
                with ui.column().classes('gap-0'):
                    vinculo = '' if sig.papel == 'candidato' else f' · {_vinculo(sig)}'
                    ui.label(f'{sig.nome} · {dominio.PAPEIS[sig.papel]}{vinculo}').classes('text-body2')
                    if sig.assinado_em:
                        ui.label(f'Assinou em {_hora(sig.assinado_em)}').classes('text-caption text-grey-7')
                    elif sig.recusado_em:
                        ui.label(f'Recusou em {_hora(sig.recusado_em)}').classes('text-caption text-negative')
                    else:
                        ui.label('Assinatura pendente').classes('text-caption text-grey-7')
                    if carta and com_links:
                        ui.link(f'Carta: {carta.nome_arquivo}', f'/backoffice/anexos/{carta.id}', new_tab=True).classes(
                            'text-caption'
                        )


@pagina('/backoffice/propostas/{proposta_id}', Papel.OPERADOR, 'Proposta de adesão')
def detalhe(operador: Usuario, proposta_id: int):
    try:
        with sessao() as s:
            p = adesao.obter(s, operador, proposta_id)
            checagens = adesao.conferencias(s, p)
            historico = eventos.da_entidade(s, operador, 'proposta', proposta_id)
            enviados = emails.da_proposta(s, proposta_id)
    except NaoEncontrado:
        titulo_pagina('Proposta não encontrada')
        return

    with ui.row().classes('w-full items-center gap-2'):
        ui.link('Propostas de adesão', '/backoffice/propostas').classes('text-primary')
        ui.label('›').classes('text-grey-6')
        ui.label(p.numero).classes('text-grey-8')
    with ui.row().classes('w-full items-center justify-between'):
        titulo_pagina(p.nome, f'Proposta {p.numero} · recebida em {_hora(p.criado_em)}')
        selo(p.situacao)

    if p.situacao == S.EM_FILA_COMITE:
        with bloco('Próximo passo'):
            ui.label('A decisão de mérito é do comitê, na reunião semanal. Antes dela, o backoffice pode pedir mais '
                     'dados ao candidato; depois, registra o que o comitê decidiu.')  # fmt: skip
            with ui.row().classes('w-full justify-end'):
                ui.button(
                    'Pedir diligência', icon='help_outline', on_click=lambda: dialogo_diligencia(operador, p.id)
                ).props('flat no-caps')
                ui.button('Registrar a decisão do comitê', icon='gavel',
                          on_click=lambda: ui.navigate.to(f'/backoffice/propostas/{p.id}/decisao')).props(
                    'unelevated no-caps')  # fmt: skip

    if p.situacao in (S.APROVADA, S.RECUSADA):
        with bloco('Decisão do comitê'), ui.element('div').classes('grid grid-cols-1 sm:grid-cols-3 gap-4 w-full'):
            campo('Decisão', dominio.ROTULO[S(p.situacao)])
            campo('Reunião', f'{p.reuniao_data:%d/%m/%Y}' if p.reuniao_data else '')
            campo('Presentes', p.reuniao_presentes)
            campo('Parecer', p.parecer)
            if p.motivo_recusa:
                campo('Motivo da recusa (interno)', p.motivo_recusa)
            campo('Lançado por', f'{p.decidido_por.nome if p.decidido_por else "—"}, em {_hora(p.decidido_em)}')
            if p.membro:
                campo(
                    'Membro criado',
                    f'{p.membro.nome} · termos {"assinados" if p.membro.termos_aceitos_em else "pendentes"}',
                )

    with bloco('Conferências automáticas'):
        for ok, texto in checagens:
            with ui.row().classes('no-wrap items-start gap-2'):
                ui.icon('check' if ok else 'warning', color='primary' if ok else 'accent').classes('q-mt-xs')
                ui.label(texto).classes('text-body2')

    dados_candidato(p)
    proponentes(p)

    if p.diligencia_pedido:
        with bloco('Diligência'):
            campo('Pedido', p.diligencia_pedido)
            campo(
                'Resposta', p.diligencia_resposta or ('Aguardando' if p.situacao == S.EM_DILIGENCIA else 'Com anexos')
            )

    outros = [a for a in p.anexos if a.tipo != 'carta']
    if outros:
        with bloco('Outros documentos'):
            for a in outros:
                origem = 'resposta à diligência' if a.tipo == 'diligencia' else 'enviado com a proposta'
                ui.link(f'{a.nome_arquivo} ({origem})', f'/backoffice/anexos/{a.id}', new_tab=True)

    with bloco('E-mails enviados (simulado)'):
        aviso_simulado(
            'Na versão final, estes e-mails saem de verdade. Aqui, o link abre a tela que o destinatário veria.'
        )
        for e in enviados:
            with ui.row().classes('w-full items-center no-wrap gap-2'):
                with ui.column().classes('gap-0 col'):
                    ui.label(e.assunto).classes('text-body2')
                    ui.label(f'Para {e.para_nome} <{e.para_email}> · {_hora(e.criado_em)}').classes(
                        'text-caption text-grey-7'
                    )
                if e.link:
                    ui.button(e.rotulo_link or 'Abrir', on_click=lambda link=e.link: ui.navigate.to(link)).props(
                        'flat dense no-caps color=accent'
                    )

    with bloco('Histórico'), ui.column().classes('gap-3 w-full'):
        for evento, nome in historico:
            with ui.row().classes('no-wrap items-start gap-3'):
                ui.icon('circle', size='10px', color='secondary').classes('q-mt-sm')
                with ui.column().classes('gap-0'):
                    ui.label(evento.descricao).classes('text-body2')
                    ui.label(f'{_hora(evento.momento)} · {nome or "Sistema"}').classes('text-caption text-grey-7')


def dialogo_diligencia(operador: Usuario, proposta_id: int):
    with ui.dialog() as dialogo, ui.card().classes('w-full max-w-lg'):
        ui.label('Pedir diligência').classes('text-h6')
        ui.label('O candidato recebe um e-mail com o pedido e responde por um link. A proposta sai da fila do comitê '
                 'até a resposta.').classes('text-body2')  # fmt: skip
        pedido = ui.textarea('O que precisa ser esclarecido ou enviado').props('outlined autogrow').classes('w-full')

        def enviar():
            def gravar():
                with sessao() as s:
                    adesao.pedir_diligencia(s, operador, proposta_id, pedido.value)

            if notificar_erros(gravar):
                dialogo.close()
                ui.notify('Diligência pedida.', type='positive')
                ui.navigate.reload()

        with ui.row().classes('w-full justify-end'):
            ui.button('Voltar', on_click=dialogo.close).props('flat no-caps')
            ui.button('Enviar pedido', on_click=enviar).props('unelevated no-caps')
    dialogo.open()


@pagina('/backoffice/propostas/{proposta_id}/decisao', Papel.OPERADOR, 'Registrar decisão')
def decisao(operador: Usuario, proposta_id: int):
    """Tela 12c: materializa uma decisão já tomada pelo comitê. Não é o backoffice decidindo o mérito."""
    try:
        with sessao() as s:
            p = adesao.obter(s, operador, proposta_id)
    except NaoEncontrado:
        titulo_pagina('Proposta não encontrada')
        return
    with ui.row().classes('w-full items-center gap-2'):
        ui.link('Propostas de adesão', '/backoffice/propostas').classes('text-primary')
        ui.label('›').classes('text-grey-6')
        ui.link(p.numero, f'/backoffice/propostas/{p.id}').classes('text-primary')
        ui.label('›').classes('text-grey-6')
        ui.label('Registrar decisão').classes('text-grey-8')
    titulo_pagina('Registrar a decisão do comitê', f'{p.numero} · {p.nome}')
    if p.situacao != S.EM_FILA_COMITE:
        ui.label(f'Esta proposta está em "{dominio.ROTULO[S(p.situacao)]}" e não aceita decisão agora.')
        return
    aviso_simulado('Esta tela materializa uma decisão já tomada pelo comitê na reunião. A referência à reunião é '
                   'obrigatória.')  # fmt: skip

    with ui.card().classes('w-full'):
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
            data = ui.input('Data da reunião', value=date.today().isoformat()).props('outlined type=date')
            presentes = ui.input('Presentes').props('outlined')
        parecer = ui.textarea('Parecer do comitê (opcional, interno)').props('outlined autogrow').classes('w-full')
        escolha = ui.radio({'aprovar': 'Aprovar', 'recusar': 'Recusar'}, value='aprovar').props('inline')
        motivo = ui.textarea('Motivo da recusa (obrigatório, interno; o candidato recebe só um aviso curto)')
        motivo.props('outlined autogrow').classes('w-full').bind_visibility_from(escolha, 'value', value='recusar')
        ui.label('Ao aprovar, a conta de membro é criada sem senha e o candidato recebe o link para criar a senha. '
                 'No primeiro acesso, ele assina os termos da Câmara.').classes('text-caption text-grey-7')  # fmt: skip

        def materializar():
            def gravar():
                with sessao() as s:
                    adesao.registrar_decisao(
                        s, operador, proposta_id,
                        DadosDecisao(
                            decisao=escolha.value,
                            reuniao_data=date.fromisoformat(data.value) if data.value else None,
                            reuniao_presentes=presentes.value or '',
                            parecer=parecer.value or '',
                            motivo_recusa=motivo.value or '',
                        ),
                    )  # fmt: skip

            if notificar_erros(gravar):
                ui.notify('Decisão registrada.', type='positive')
                ui.navigate.to(f'/backoffice/propostas/{proposta_id}')

        with ui.row().classes('w-full justify-end'):
            ui.button('Voltar', on_click=lambda: ui.navigate.to(f'/backoffice/propostas/{proposta_id}')).props(
                'flat no-caps'
            )
            ui.button('Materializar decisão', icon='gavel', on_click=materializar).props('unelevated no-caps')
