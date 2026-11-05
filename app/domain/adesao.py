"""Máquina de estados da proposta de adesão (maquina-de-estados.md, "A proposta de adesão").

Mesma forma da máquina do registro: tabela de transições, nunca `if` espalhado. Em relação à rev. 3 do documento,
PREENCHENDO some (o formulário é enviado de uma vez) e entra ASSINATURA_RECUSADA (proponente que recusa encerra
a proposta; o candidato faz outra).
"""

import enum
from dataclasses import dataclass


class SituacaoProposta(enum.StrEnum):
    AGUARDANDO_ASSINATURAS = 'aguardando_assinaturas'
    ASSINATURA_RECUSADA = 'assinatura_recusada'
    EXPIRADA = 'expirada'
    EM_FILA_COMITE = 'em_fila_comite'
    EM_DILIGENCIA = 'em_diligencia'
    APROVADA = 'aprovada'
    RECUSADA = 'recusada'


class QuemAdesao(enum.StrEnum):
    SIGNATARIO = 'signatario'
    CANDIDATO = 'candidato'
    SISTEMA = 'sistema'
    BACKOFFICE = 'backoffice'


@dataclass(frozen=True)
class TransicaoAdesao:
    acao: str
    origens: frozenset[SituacaoProposta]
    destino: SituacaoProposta
    quem: QuemAdesao
    referencia: str


P, Q = SituacaoProposta, QuemAdesao
TRANSICOES = [
    TransicaoAdesao(
        'recusar_assinatura', frozenset({P.AGUARDANDO_ASSINATURAS}), P.ASSINATURA_RECUSADA, Q.SIGNATARIO, ''
    ),
    TransicaoAdesao(
        'completar_assinaturas', frozenset({P.AGUARDANDO_ASSINATURAS}), P.EM_FILA_COMITE, Q.SISTEMA, 'RN-103'
    ),
    TransicaoAdesao('expirar', frozenset({P.AGUARDANDO_ASSINATURAS}), P.EXPIRADA, Q.SISTEMA, ''),
    TransicaoAdesao('pedir_diligencia', frozenset({P.EM_FILA_COMITE}), P.EM_DILIGENCIA, Q.BACKOFFICE, 'RN-108'),
    TransicaoAdesao('responder_diligencia', frozenset({P.EM_DILIGENCIA}), P.EM_FILA_COMITE, Q.CANDIDATO, 'RN-108'),
    TransicaoAdesao('aprovar', frozenset({P.EM_FILA_COMITE}), P.APROVADA, Q.BACKOFFICE, 'RN-109, RN-32'),
    TransicaoAdesao('recusar', frozenset({P.EM_FILA_COMITE}), P.RECUSADA, Q.BACKOFFICE, 'RN-24, RN-110'),
]
_POR_ACAO = {t.acao: t for t in TRANSICOES}

ROTULO = {
    P.AGUARDANDO_ASSINATURAS: 'Aguardando assinaturas',
    P.ASSINATURA_RECUSADA: 'Proponente recusou',
    P.EXPIRADA: 'Link expirou',
    P.EM_FILA_COMITE: 'Pronta para o comitê',
    P.EM_DILIGENCIA: 'Em diligência',
    P.APROVADA: 'Aprovada',
    P.RECUSADA: 'Recusada',
}

PAPEIS = {'candidato': 'Candidato', 'proponente_1': 'Proponente 1', 'proponente_2': 'Proponente 2'}


class TransicaoInvalida(Exception):
    pass


def transicao(acao: str, origem: SituacaoProposta, quem: QuemAdesao) -> TransicaoAdesao:
    t = _POR_ACAO.get(acao)
    if t is None or origem not in t.origens or quem != t.quem:
        raise TransicaoInvalida(f'{acao} não é permitido a partir de {origem} por {quem}')
    return t
