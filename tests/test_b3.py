from datetime import date

import pytest

from app.domain import prazos
from app.domain.estados import Estado
from app.domain.models import EnvioB3, Papel
from app.services import b3, envelopes, eventos
from app.services.erros import AcessoNegado, ErroDeNegocio
from tests import fabricas
from tests.fabricas import gerar, rascunho


@pytest.fixture
def operador(s):
    return fabricas.usuario(s, papel=Papel.OPERADOR)


def assinado(s, partes, modo='sucesso', operador=None):
    if modo != 'sucesso':
        b3.definir_modo_simulador(s, operador, modo)
    r = rascunho(s, partes)
    gerar(s, partes, r)
    for quem in ('vendedor', 'comprador'):
        envelopes.assinar(s, partes[quem].usuario, r.id)
    assert r.estado == Estado.ASSINADO
    b3.processar_assinados(s)
    return r


def operacoes(s, r) -> list[tuple[str, int]]:
    return [(e.operacao, e.status_http) for e in s.query(EnvioB3).filter_by(registro_id=r.id).order_by(EnvioB3.id)]


def test_sucesso_registra_com_numero_de_controle(s, partes):
    r = assinado(s, partes)
    outro = assinado(s, partes)  # mesmo job, mesmo instante: o número não pode repetir
    assert r.estado == outro.estado == Estado.REGISTRADO
    assert len(r.numero_controle_b3) == 16
    assert r.numero_controle_b3 != outro.numero_controle_b3
    assert operacoes(s, r) == [('envio', 201)]


def test_instavel_consulta_antes_de_reenviar(s, partes, operador):
    r = assinado(s, partes, 'instavel', operador)
    assert r.estado == Estado.REGISTRADO
    assert operacoes(s, r) == [('envio', 503), ('consulta', 404), ('envio', 201)]


def test_tempo_esgotado_mas_registrou_nao_duplica(s, partes, operador):
    r = assinado(s, partes, 'registrou_sem_responder', operador)
    assert r.estado == Estado.REGISTRADO
    assert operacoes(s, r) == [('envio', 504), ('consulta', 200)]


def test_fora_do_ar_esgota_tentativas_e_vai_para_a_fila(s, partes, operador):
    r = assinado(s, partes, 'indisponivel', operador)
    assert r.estado == Estado.FALHA_B3
    assert [op for op in operacoes(s, r) if op[0] == 'envio'] == [('envio', 503)] * 3
    fila = b3.pendencias(s, operador)
    assert [p.registro for p in fila] == [r]
    assert fila[0].tentativas == 3


def test_recusa_definitiva_nao_tenta_de_novo(s, partes, operador):
    r = assinado(s, partes, 'recusa', operador)
    assert r.estado == Estado.FALHA_B3
    assert operacoes(s, r) == [('envio', 422)]


def test_operador_assume_e_reenvia_consultando_antes(s, partes, operador):
    r = assinado(s, partes, 'indisponivel', operador)
    with pytest.raises(ErroDeNegocio):
        b3.reenviar(s, operador, r.id)  # precisa assumir antes
    b3.assumir(s, operador, r.id)
    assert r.responsavel_id == operador.id
    b3.definir_modo_simulador(s, operador, 'sucesso')
    b3.reenviar(s, operador, r.id)
    assert r.estado == Estado.REGISTRADO
    assert operacoes(s, r)[-2:] == [('consulta', 404), ('envio', 201)]


def test_cancelar_exige_motivo(s, partes, operador):
    r = assinado(s, partes, 'recusa', operador)
    b3.assumir(s, operador, r.id)
    with pytest.raises(ErroDeNegocio, match='motivo'):
        b3.cancelar(s, operador, r.id, '  ')
    b3.cancelar(s, operador, r.id, 'Partes desistiram')
    assert r.estado == Estado.CANCELADO


def test_membro_nao_usa_o_backoffice(s, partes, operador):
    r = assinado(s, partes, 'recusa', operador)
    membro = partes['vendedor'].usuario
    for chamada in (
        lambda: b3.assumir(s, membro, r.id),
        lambda: b3.pendencias(s, membro),
        lambda: b3.envios(s, membro, r.id),
        lambda: b3.definir_modo_simulador(s, membro, 'sucesso'),
        lambda: eventos.listar(s, membro),
    ):
        with pytest.raises(AcessoNegado):
            chamada()


def test_membro_ve_registro_mas_nao_a_falha():
    # A falha na B3 aparece para o membro como "Em processamento" (camada 1)
    from app.domain.estados import VISAO_MEMBRO

    assert VISAO_MEMBRO[Estado.FALHA_B3] == VISAO_MEMBRO[Estado.EM_CORRECAO] == 'Em processamento'


def test_prazo_legal_em_dias_uteis():
    # 03/11/2026, terça. 30 dias úteis, pulando 15/11 (domingo) e 20/11 (sexta, Consciência Negra)
    assert prazos.limite_legal(date(2026, 11, 3), 30) == date(2026, 12, 16)
    assert prazos.dias_uteis_entre(date(2026, 11, 19), date(2026, 11, 23)) == 1
    assert prazos.dias_uteis_entre(date(2026, 11, 23), date(2026, 11, 19)) == -1
