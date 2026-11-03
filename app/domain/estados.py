"""Máquina de estados do registro (docs/maquina-de-estados.md, rev. 3), como dado e não como `if` espalhado.

A camada 2 inteira está declarada, para o modelo não mudar na Fase 1. As transições cobrem o recorte do MVP;
reassinatura e recusa por parte entram depois, acrescentando linhas à tabela.
"""

import enum
from dataclasses import dataclass


class Estado(enum.StrEnum):
    RASCUNHO = 'rascunho'
    PRE_VALIDANDO = 'pre_validando'
    AGUARDANDO_ASSINATURAS = 'aguardando_assinaturas'
    JANELA_EXPIRADA = 'janela_expirada'
    RECUSADO_POR_PARTE = 'recusado_por_parte'
    ASSINADO = 'assinado'
    ENVIANDO_B3 = 'enviando_b3'
    FALHA_B3 = 'falha_b3'
    EM_CORRECAO = 'em_correcao'
    AGUARDANDO_REASSINATURA = 'aguardando_reassinatura'
    REGISTRADO = 'registrado'
    CANCELADO = 'cancelado'


class Quem(enum.StrEnum):
    AUTOR = 'autor'
    SISTEMA = 'sistema'
    OPERADOR = 'operador'


@dataclass(frozen=True)
class Transicao:
    acao: str
    origens: frozenset[Estado]
    destino: Estado
    quem: Quem
    referencia: str


def _t(acao: str, origens: set[Estado], destino: Estado, quem: Quem, referencia: str) -> Transicao:
    return Transicao(acao, frozenset(origens), destino, quem, referencia)


E = Estado
TRANSICOES = [
    _t('descartar', {E.RASCUNHO}, E.CANCELADO, Quem.AUTOR, 'T-01'),
    _t('gerar_envelope', {E.RASCUNHO}, E.PRE_VALIDANDO, Quem.AUTOR, 'T-08'),
    _t('prevalidacao_falhou', {E.PRE_VALIDANDO}, E.RASCUNHO, Quem.SISTEMA, 'T-08'),
    _t('prevalidacao_passou', {E.PRE_VALIDANDO}, E.AGUARDANDO_ASSINATURAS, Quem.SISTEMA, 'T-08'),
    _t('cancelar_envelope', {E.AGUARDANDO_ASSINATURAS}, E.CANCELADO, Quem.AUTOR, 'T-02, RN-71'),
    _t('expirar_janela', {E.AGUARDANDO_ASSINATURAS}, E.JANELA_EXPIRADA, Quem.SISTEMA, 'T-09'),
    _t('reabrir_janela', {E.JANELA_EXPIRADA}, E.AGUARDANDO_ASSINATURAS, Quem.AUTOR, 'T-09, RN-120'),
    _t('cancelar_expirado', {E.JANELA_EXPIRADA}, E.CANCELADO, Quem.AUTOR, 'T-09, RN-120'),
    _t('concluir_assinaturas', {E.AGUARDANDO_ASSINATURAS}, E.ASSINADO, Quem.SISTEMA, ''),
    _t('enviar_b3', {E.ASSINADO}, E.ENVIANDO_B3, Quem.SISTEMA, ''),
    _t('confirmar_b3', {E.ENVIANDO_B3}, E.REGISTRADO, Quem.SISTEMA, ''),
    _t('falhar_b3', {E.ENVIANDO_B3}, E.FALHA_B3, Quem.SISTEMA, 'T-05'),
    _t('assumir_correcao', {E.FALHA_B3}, E.EM_CORRECAO, Quem.OPERADOR, ''),
    _t('reenviar', {E.EM_CORRECAO}, E.ENVIANDO_B3, Quem.OPERADOR, 'T-06'),
    _t('cancelar_correcao', {E.EM_CORRECAO}, E.CANCELADO, Quem.OPERADOR, ''),
]
_POR_ACAO = {t.acao: t for t in TRANSICOES}

# Camada 1: o que o membro vê
VISAO_MEMBRO = {
    E.RASCUNHO: 'Rascunho',
    E.PRE_VALIDANDO: 'Rascunho',
    E.AGUARDANDO_ASSINATURAS: 'Aguardando assinaturas',
    E.JANELA_EXPIRADA: 'Aguardando assinaturas',
    E.RECUSADO_POR_PARTE: 'Cancelado',
    E.ASSINADO: 'Em processamento',
    E.ENVIANDO_B3: 'Em processamento',
    E.FALHA_B3: 'Em processamento',
    E.EM_CORRECAO: 'Em processamento',
    E.AGUARDANDO_REASSINATURA: 'Aguardando assinaturas',
    E.REGISTRADO: 'Registrado',
    E.CANCELADO: 'Cancelado',
}

NOME_INTERNO = {
    E.RASCUNHO: 'Rascunho',
    E.PRE_VALIDANDO: 'Pré-validando',
    E.AGUARDANDO_ASSINATURAS: 'Aguardando assinaturas',
    E.JANELA_EXPIRADA: 'Janela expirada',
    E.RECUSADO_POR_PARTE: 'Recusado por parte',
    E.ASSINADO: 'Assinado',
    E.ENVIANDO_B3: 'Enviando à B3',
    E.FALHA_B3: 'Falha no envio',
    E.EM_CORRECAO: 'Em correção',
    E.AGUARDANDO_REASSINATURA: 'Aguardando reassinatura',
    E.REGISTRADO: 'Registrado',
    E.CANCELADO: 'Cancelado',
}


class TransicaoInvalida(Exception):
    pass


def transicao(acao: str, origem: Estado, quem: Quem) -> Transicao:
    t = _POR_ACAO.get(acao)
    if t is None:
        raise TransicaoInvalida(f'Ação desconhecida: {acao}')
    if origem not in t.origens:
        raise TransicaoInvalida(f'{acao} não é permitido a partir de {origem}')
    if quem != t.quem:
        raise TransicaoInvalida(f'{acao} é ação de {t.quem}, não de {quem}')
    return t


def acoes_possiveis(origem: Estado, quem: Quem) -> list[str]:
    return [t.acao for t in TRANSICOES if origem in t.origens and t.quem == quem]
