"""Telas 08, 09 e 10 juntas: envelope, assinatura simulada e detalhe com linha do tempo."""

from datetime import UTC, datetime

from fastapi import Response
from fastapi.responses import RedirectResponse
from nicegui import app, ui

from app.db import sessao
from app.domain.estados import Estado
from app.domain.models import Assinatura, Envelope, PapelNoRegistro, Registro, SituacaoEnvelope, TipoDocumento, Usuario
from app.services import documentos, envelopes, membros, registros
from app.services.erros import NaoEncontrado
from app.ui.componentes import bloco, detalhes_registro, notificar_erros, selo_estado
from app.ui.tema import titulo_pagina, usuario_logado

PAPEL = {
    PapelNoRegistro.VENDEDOR: 'Vendedor (emitente)',
    PapelNoRegistro.COMPRADOR: 'Comprador (credor)',
    PapelNoRegistro.CORRETOR: 'Corretor (interveniente)',
}
NOME_DOCUMENTO = {TipoDocumento.CONTRATO: 'Contrato', TipoDocumento.CPR: 'CPR'}


@app.get('/documentos/{documento_id}')
def baixar_documento(documento_id: int):
    usuario = usuario_logado()
    if usuario is None:
        return RedirectResponse('/login')
    try:
        with sessao() as s:
            documento, nome = documentos.obter_pdf(s, usuario, documento_id)
    except NaoEncontrado:
        return Response('Documento não encontrado.', status_code=404)
    return Response(
        documento.pdf, media_type='application/pdf', headers={'Content-Disposition': f'inline; filename="{nome}"'}
    )


def hora(momento: datetime) -> str:
    return momento.astimezone().strftime('%d/%m/%Y, às %H:%M')


def _assinatura_label(a: Assinatura) -> str:
    docs = ' e '.join(NOME_DOCUMENTO[t] for t in a.documentos)
    return f'{a.nome_assinante} · {PAPEL[a.papel]} · assina {docs}'


def documentos_envelope(envelope: Envelope):
    with ui.row().classes('gap-2'):
        for d in envelope.documentos:
            ui.button(
                f'Abrir {"contrato" if d.tipo == TipoDocumento.CONTRATO else "CPR"} (PDF)',
                icon='picture_as_pdf',
                on_click=lambda d=d: ui.navigate.to(f'/documentos/{d.id}', new_tab=True),
            ).props('outline no-caps color=secondary')


def assinaturas_envelope(envelope: Envelope):
    for a in envelope.assinaturas:
        with ui.row().classes('w-full items-center no-wrap gap-2'):
            if a.assinado_em:
                ui.icon('check_circle', color='primary')
            else:
                ui.icon('radio_button_unchecked', color='grey-6')
            with ui.column().classes('gap-0'):
                ui.label(_assinatura_label(a)).classes('text-body2')
                if a.assinado_em:
                    ui.label(f'Assinou em {hora(a.assinado_em)}').classes('text-caption text-grey-7')
                else:
                    ui.label('Assinatura pendente').classes('text-caption text-grey-7')


def _contagem(envelope: Envelope):
    rotulo = ui.label().classes('text-subtitle1 text-weight-medium text-accent')

    def atualizar():
        restante = int((envelope.expira_em - datetime.now(UTC)).total_seconds())
        if restante <= 0:
            rotulo.text = 'A janela de assinatura terminou.'
            return
        horas, resto = divmod(restante, 3600)
        relogio = f'{horas}:{resto // 60:02d}:{resto % 60:02d}' if horas else f'{resto // 60:02d}:{resto % 60:02d}'
        rotulo.text = f'Faltam {relogio} para a janela de assinatura fechar'

    atualizar()
    ui.timer(1, atualizar)


def _acao(usuario: Usuario, registro: Registro, fn, sucesso: str):
    def executar():
        with sessao() as s:
            fn(s, usuario, registro.id)

    if notificar_erros(executar):
        ui.notify(sucesso, type='positive')
        ui.navigate.reload()


def _confirmar_assinatura(usuario: Usuario, registro: Registro, minha: Assinatura):
    with ui.dialog() as dialogo, ui.card().classes('max-w-lg'):
        ui.label('Assinar o envelope').classes('text-h6')
        docs = ' e a '.join(NOME_DOCUMENTO[t] for t in minha.documentos)
        ui.label(f'Você vai assinar o {docs} do registro {registro.numero}, como {PAPEL[minha.papel].lower()}.')
        with ui.card().classes('w-full bg-orange-1 q-pa-sm').props('flat'):
            ui.label(
                'Assinatura simulada. Na versão final, este passo abre o aplicativo do seu certificado digital '
                '(token, nuvem ou arquivo A1) e você volta para cá depois de confirmar.'
            ).classes('text-body2 text-secondary')
        with ui.row().classes('w-full justify-end'):
            ui.button('Voltar', on_click=dialogo.close).props('flat no-caps')
            ui.button(
                'Assinar (simulado)',
                icon='draw',
                on_click=lambda: (
                    dialogo.close(),
                    _acao(usuario, registro, envelopes.assinar, 'Assinatura registrada.'),
                ),
            ).props('unelevated no-caps')
    dialogo.open()


def _painel_envelope(usuario: Usuario, registro: Registro, eu_id: int):
    envelope = envelopes.atual(registro)
    autor = registro.autor_id == usuario.id

    if registro.estado == Estado.AGUARDANDO_ASSINATURAS:
        minha = next((a for a in envelope.pendentes() if a.membro_id == eu_id), None)
        with bloco('Envelope para assinatura'):
            _contagem(envelope)
            ui.label(
                'Contrato e CPR vão juntos num envelope só. Cada parte assina na própria conta, dentro da janela.'
            ).classes('text-body2 text-grey-8')
            documentos_envelope(envelope)
            ui.separator()
            assinaturas_envelope(envelope)
            with ui.row().classes('w-full items-center q-mt-sm'):
                if autor and not any(a.assinado_em for a in envelope.assinaturas):
                    ui.button(
                        'Cancelar envelope',
                        on_click=lambda: _acao(usuario, registro, envelopes.cancelar_envelope, 'Envelope cancelado.'),
                    ).props('flat no-caps color=negative')
                ui.space()
                if minha:
                    ui.button(
                        'Assinar', icon='draw', on_click=lambda: _confirmar_assinatura(usuario, registro, minha)
                    ).props('unelevated no-caps size=lg')
                else:
                    ui.label('Sua parte está feita. Aguardando as outras assinaturas.').classes('text-grey-8')

    elif registro.estado == Estado.JANELA_EXPIRADA:
        with bloco('A janela de assinatura terminou'):
            ui.label('Nem todas as partes assinaram a tempo.').classes('text-body1')
            assinaturas_envelope(envelope)
            if autor:
                ui.label(
                    'Reabrir gera o envelope de novo, com nova janela, e todas as partes assinam outra vez.'
                ).classes('text-body2 text-grey-8')
                with ui.row().classes('w-full justify-end'):
                    ui.button(
                        'Cancelar registro',
                        on_click=lambda: _acao(usuario, registro, envelopes.cancelar_expirado, 'Registro cancelado.'),
                    ).props('flat no-caps color=negative')
                    ui.button(
                        'Reabrir janela',
                        icon='refresh',
                        on_click=lambda: _acao(usuario, registro, envelopes.reabrir_janela, 'Janela reaberta.'),
                    ).props('unelevated no-caps')
            else:
                ui.label('Quem criou o registro decide se reabre a janela ou cancela.').classes('text-grey-8')

    elif registro.estado == Estado.REGISTRADO:
        with bloco('Registrado na B3'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('verified', color='primary', size='md')
                ui.label(f'Registrado em {hora(registro.registrado_em)}').classes('text-subtitle1')
            ui.label(f'Número de controle na B3: {registro.numero_controle_b3}').classes('text-body1')
            documentos_envelope(envelope)
            assinaturas_envelope(envelope)

    elif registro.estado == Estado.CANCELADO:
        with bloco('Registro cancelado'):
            ui.label('Este registro foi cancelado. A linha do tempo mostra quando e por quê.')

    elif envelope is not None and envelope.situacao == SituacaoEnvelope.CONCLUIDO:
        # Assinado, enviando, falha ou correção: para o membro, tudo é "em processamento"
        with bloco('Envelope assinado'):
            ui.label(
                'Contrato assinado por todas as partes. O registro na B3 está em processamento; '
                'você não precisa fazer nada.'
            )
            assinaturas_envelope(envelope)
            documentos_envelope(envelope)


def _linha_do_tempo(usuario: Usuario, registro: Registro):
    with sessao() as s:
        linha = envelopes.linha_do_tempo(s, usuario, registro.id)
    with bloco('Linha do tempo'), ui.column().classes('gap-3 w-full'):
        for evento in linha:
            with ui.row().classes('no-wrap items-start gap-3'):
                ui.icon('circle', size='10px', color='primary').classes('q-mt-sm')
                with ui.column().classes('gap-0'):
                    ui.label(evento.descricao).classes('text-body2')
                    ui.label(hora(evento.momento)).classes('text-caption text-grey-7')


def detalhe(usuario: Usuario, registro: Registro):
    with sessao() as s:
        eu = membros.do_usuario(s, usuario)
    envelope = envelopes.atual(registro)
    retrato = (registro.estado, envelope.versao if envelope else 0, len(envelope.pendentes()) if envelope else 0)

    with ui.row().classes('w-full items-center gap-2'):
        ui.link('Meus registros', '/').classes('text-primary')
        ui.label('›').classes('text-grey-6')
        ui.label(registro.numero).classes('text-grey-8')
    with ui.row().classes('w-full items-center justify-between'):
        titulo_pagina(f'Contrato {registro.numero}', f'{registro.vendedor.nome} → {registro.comprador.nome}')
        selo_estado(registro.estado)

    _painel_envelope(usuario, registro, eu.id)
    _linha_do_tempo(usuario, registro)
    detalhes_registro(registro)

    def acompanhar():
        """As outras partes assinam em outras telas: recarrega quando o envelope muda."""
        with sessao() as s:
            try:
                atual = registros.obter(s, usuario, registro.id)
            except NaoEncontrado:
                return
            env = envelopes.atual(atual)
            agora = (atual.estado, env.versao if env else 0, len(env.pendentes()) if env else 0)
        if agora != retrato:
            ui.navigate.reload()

    ui.timer(3, acompanhar)
