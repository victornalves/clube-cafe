from decimal import Decimal

import pytest

from app.domain import estados
from app.domain.estados import Estado, Quem, TransicaoInvalida
from app.domain.formatos import cnpj_valido, cpf_valido, formatar_documento, formatar_reais


def test_todo_estado_tem_visao_do_membro_e_nome_interno():
    assert set(estados.VISAO_MEMBRO) == set(Estado)
    assert set(estados.NOME_INTERNO) == set(Estado)


def test_membro_ve_so_cinco_estados():
    assert set(estados.VISAO_MEMBRO.values()) == {
        'Rascunho',
        'Aguardando assinaturas',
        'Em processamento',
        'Registrado',
        'Cancelado',
    }


def test_registrado_e_terminal():
    assert not [t for t in estados.TRANSICOES if Estado.REGISTRADO in t.origens]


def test_transicao_valida():
    assert estados.transicao('descartar', Estado.RASCUNHO, Quem.AUTOR).destino == Estado.CANCELADO


@pytest.mark.parametrize(
    ('acao', 'origem', 'quem'),
    [
        ('descartar', Estado.AGUARDANDO_ASSINATURAS, Quem.AUTOR),  # origem errada
        ('reenviar', Estado.EM_CORRECAO, Quem.AUTOR),  # só o operador reenvia
        ('cancelar_expirado', Estado.JANELA_EXPIRADA, Quem.SISTEMA),  # nunca automático (RN-120)
        ('inventada', Estado.RASCUNHO, Quem.AUTOR),
    ],
)
def test_transicao_invalida(acao, origem, quem):
    with pytest.raises(TransicaoInvalida):
        estados.transicao(acao, origem, quem)


def test_documentos():
    assert cpf_valido('482.913.760-69')
    assert not cpf_valido('482.913.760-68')
    assert not cpf_valido('111.111.111-11')
    assert cnpj_valido('09.455.218/0001-05')
    assert not cnpj_valido('09.455.218/0001-06')
    assert formatar_documento('09455218000105') == '09.455.218/0001-05'


def test_reais():
    assert formatar_reais(Decimal(2790000)) == '2.790.000,00'
    assert formatar_reais(Decimal('1395.5')) == '1.395,50'
