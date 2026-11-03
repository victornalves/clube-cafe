"""Envelope único com janela curta (RN-118 a RN-120) e assinatura simulada, modo embutido.

Na Fase 2, `assinar` passa a ser o retorno do fornecedor (webhook ou consulta); o resto não muda.
"""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import config
from app.domain.estados import Estado, Quem
from app.domain.models import (
    Assinatura,
    DominioB3,
    Envelope,
    Evento,
    Membro,
    PapelNoRegistro,
    Registro,
    SituacaoEnvelope,
    TipoPessoa,
    Usuario,
)
from app.domain.prevalidacao import prevalidar
from app.services import documentos, eventos, membros, registros
from app.services.erros import ErroDeNegocio, NaoEncontrado
from app.services.registros import transicionar


def _agora() -> datetime:
    return datetime.now(UTC)


def atual(registro: Registro) -> Envelope | None:
    return registro.envelopes[-1] if registro.envelopes else None


def _assinatura(m: Membro, papel: PapelNoRegistro) -> Assinatura:
    nome = m.representante_nome if m.tipo_pessoa == TipoPessoa.PJ and m.representante_nome else m.nome
    return Assinatura(membro_id=m.id, papel=papel, nome_assinante=nome)


def _abrir(s: Session, registro: Registro, agora: datetime) -> Envelope:
    versao = len(registro.envelopes) + 1
    signatarios = [
        _assinatura(registro.vendedor, PapelNoRegistro.VENDEDOR),
        _assinatura(registro.comprador, PapelNoRegistro.COMPRADOR),
    ]
    if registro.corretor:
        signatarios.append(_assinatura(registro.corretor, PapelNoRegistro.CORRETOR))
    envelope = Envelope(
        versao=versao,
        aberto_em=agora,
        expira_em=agora + timedelta(minutes=config().janela_assinatura_minutos),
        documentos=documentos.gerar(registro, agora.astimezone().date()),
        assinaturas=signatarios,
    )
    registro.envelopes.append(envelope)
    if registro.enviado_as_partes_em is None:
        registro.enviado_as_partes_em = agora
    s.flush()
    return envelope


def _hora(momento: datetime) -> str:
    return momento.astimezone().strftime('%H:%M')


def gerar_envelope(s: Session, usuario: Usuario, registro_id: int) -> list[str]:
    """Pré-valida e, se passar, abre o envelope. Devolve os problemas da pré-validação (vazio se abriu)."""
    registro = registros.rascunho_do_autor(s, usuario, registro_id)
    if pendencias := registros.pendencias_objeto(registro):
        raise ErroDeNegocio(' '.join(pendencias))

    transicionar(s, registro, 'gerar_envelope', Quem.AUTOR, autor=usuario, descricao=f'{usuario.nome} pediu o envelope')
    dominios = set(s.execute(select(DominioB3.tipo, DominioB3.codigo).where(DominioB3.ativo)).all())
    if erros := prevalidar(registro, dominios, date.today()):
        transicionar(
            s, registro, 'prevalidacao_falhou', Quem.SISTEMA, autor=None,
            descricao='A pré-validação encontrou problemas e o registro voltou para rascunho', dados={'erros': erros},
        )  # fmt: skip
        return erros

    envelope = _abrir(s, registro, _agora())
    transicionar(
        s, registro, 'prevalidacao_passou', Quem.SISTEMA, autor=None,
        descricao=f'Contrato e CPR gerados e enviados para assinatura, janela até {_hora(envelope.expira_em)}',
        dados={'envelope': envelope.versao, 'documentos': {d.tipo.value: d.sha256 for d in envelope.documentos}},
    )  # fmt: skip
    return []


def assinar(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    registro = registros.obter(s, usuario, registro_id)
    envelope = atual(registro)
    if registro.estado != Estado.AGUARDANDO_ASSINATURAS or envelope is None:
        raise ErroDeNegocio('Este envelope não está aberto para assinatura.')
    agora = _agora()
    if envelope.expira_em <= agora:
        raise ErroDeNegocio('A janela de assinatura terminou. Quem criou o registro pode reabrir.')

    eu = membros.do_usuario(s, usuario)
    assinatura = next((a for a in envelope.pendentes() if a.membro_id == eu.id), None)
    if assinatura is None:
        raise ErroDeNegocio('Não há assinatura sua pendente neste envelope.')
    assinatura.assinado_em = agora
    pela = f' pela {eu.nome}' if eu.tipo_pessoa == TipoPessoa.PJ else ''
    documentos_assinados = {d.tipo.value: d.sha256 for d in envelope.documentos if d.tipo in assinatura.documentos}
    eventos.registrar(
        s, autor=usuario, tipo='assinatura', entidade='registro', entidade_id=registro.id,
        descricao=f'{assinatura.nome_assinante} assinou{pela} (assinatura simulada)',
        dados={'envelope': envelope.versao, 'papel': assinatura.papel.value, 'documentos': documentos_assinados},
    )  # fmt: skip

    if not envelope.pendentes():
        envelope.situacao = SituacaoEnvelope.CONCLUIDO
        envelope.encerrado_em = agora
        transicionar(
            s, registro, 'concluir_assinaturas', Quem.SISTEMA, autor=None,
            descricao='Contrato assinado por todas as partes',
        )  # fmt: skip
    return registro


def _do_autor(s: Session, usuario: Usuario, registro_id: int, estado: Estado) -> Registro:
    registro = registros.obter(s, usuario, registro_id)
    if registro.autor_id != usuario.id:
        raise NaoEncontrado
    if registro.estado != estado:
        raise ErroDeNegocio('Esta ação não está disponível na situação atual do registro.')
    return registro


def cancelar_envelope(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    """O autor cancela enquanto ninguém assinou. Depois disso, vira pedido ao backoffice (RN-71)."""
    registro = _do_autor(s, usuario, registro_id, Estado.AGUARDANDO_ASSINATURAS)
    envelope = atual(registro)
    if any(a.assinado_em for a in envelope.assinaturas):
        raise ErroDeNegocio('Alguém já assinou. Para cancelar agora, fale com o backoffice.')
    envelope.situacao = SituacaoEnvelope.CANCELADO
    envelope.encerrado_em = _agora()
    transicionar(
        s, registro, 'cancelar_envelope', Quem.AUTOR, autor=usuario, descricao=f'{usuario.nome} cancelou o envelope'
    )
    return registro


def reabrir_janela(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    """Nova janela com envelope novo: documentos gerados de novo e todas as assinaturas recomeçam."""
    registro = _do_autor(s, usuario, registro_id, Estado.JANELA_EXPIRADA)
    envelope = _abrir(s, registro, _agora())
    transicionar(
        s, registro, 'reabrir_janela', Quem.AUTOR, autor=usuario,
        descricao=f'{usuario.nome} reabriu a janela de assinatura, até {_hora(envelope.expira_em)}. '
        'Todas as partes assinam de novo',
        dados={'envelope': envelope.versao},
    )  # fmt: skip
    return registro


def cancelar_expirado(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    registro = _do_autor(s, usuario, registro_id, Estado.JANELA_EXPIRADA)
    transicionar(
        s, registro, 'cancelar_expirado', Quem.AUTOR, autor=usuario, descricao=f'{usuario.nome} cancelou o registro'
    )
    return registro


def expirar_vencidos(s: Session, agora: datetime | None = None) -> int:
    """Job do sistema: fecha as janelas vencidas (T-09). Reabrir ou cancelar fica com uma pessoa (RN-120)."""
    agora = agora or _agora()
    vencidos = s.scalars(
        select(Envelope)
        .join(Envelope.registro)
        .where(
            Envelope.situacao == SituacaoEnvelope.ABERTO,
            Envelope.expira_em <= agora,
            Registro.estado == Estado.AGUARDANDO_ASSINATURAS,
        )
    ).all()
    for envelope in vencidos:
        envelope.situacao = SituacaoEnvelope.EXPIRADO
        envelope.encerrado_em = agora
        transicionar(
            s, envelope.registro, 'expirar_janela', Quem.SISTEMA, autor=None,
            descricao='A janela de assinatura terminou sem todas as assinaturas',
        )  # fmt: skip
    return len(vencidos)


# Eventos que viram linha do tempo para o membro; o resto fica só na auditoria
TIPOS_LINHA_DO_TEMPO = {
    'registro_criado',
    'prevalidacao_falhou',
    'prevalidacao_passou',
    'assinatura',
    'concluir_assinaturas',
    'expirar_janela',
    'reabrir_janela',
    'cancelar_envelope',
    'cancelar_expirado',
    'confirmar_b3',
    'cancelar_correcao',
}


def linha_do_tempo(s: Session, usuario: Usuario, registro_id: int) -> list[Evento]:
    registro = registros.obter(s, usuario, registro_id)
    consulta = select(Evento).where(
        Evento.entidade == 'registro', Evento.entidade_id == registro.id, Evento.tipo.in_(TIPOS_LINHA_DO_TEMPO)
    )
    if registro.autor_id != usuario.id and registro.enviado_as_partes_em:
        # O que aconteceu no rascunho, antes do envelope, é só do autor
        consulta = consulta.where(
            (Evento.momento >= registro.enviado_as_partes_em) | (Evento.tipo == 'registro_criado')
        )
    return list(s.scalars(consulta.order_by(Evento.momento, Evento.id)))
