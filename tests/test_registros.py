from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.domain.estados import Estado
from app.domain.models import Papel, PapelNoRegistro
from app.services import registros
from app.services.erros import ErroDeNegocio, NaoEncontrado
from app.services.registros import DadosObjeto, DadosPartes
from tests import fabricas

V, C, CO = PapelNoRegistro.VENDEDOR, PapelNoRegistro.COMPRADOR, PapelNoRegistro.CORRETOR


@pytest.fixture
def partes(s):
    return {
        'vendedor': fabricas.membro(s),
        'comprador': fabricas.membro(s),
        'corretor': fabricas.membro(s, corretor=True),
        'estranho': fabricas.membro(s),
    }


def criar(s, partes, autor='vendedor', papel=V, corretor=False):
    return registros.criar_rascunho(
        s,
        partes[autor].usuario,
        DadosPartes(
            papel,
            partes['vendedor'].id,
            partes['comprador'].id,
            partes['corretor'].id if corretor else None,
        ),
    )


def test_cria_rascunho_com_numero(s, partes):
    r = criar(s, partes)
    assert r.estado == Estado.RASCUNHO
    assert r.numero == f'CRTC-{date.today().year}-{r.id:04d}'


def test_corretor_preenche_pelos_dois_lados(s, partes):
    r = criar(s, partes, autor='corretor', papel=CO, corretor=True)
    assert r.corretor_id == partes['corretor'].id


@pytest.mark.parametrize(
    ('dados', 'mensagem'),
    [
        (lambda p: DadosPartes(C, p['vendedor'].id, p['comprador'].id), 'papel que escolheu'),
        (lambda p: DadosPartes(V, p['vendedor'].id, p['vendedor'].id), 'dois papéis'),
        (lambda p: DadosPartes(CO, p['vendedor'].id, p['comprador'].id, p['vendedor'].id), 'não é de corretor'),
        (lambda p: DadosPartes(V, p['vendedor'].id, p['comprador'].id, p['estranho'].id), 'não é corretor'),
    ],
)
def test_partes_invalidas(s, partes, dados, mensagem):
    with pytest.raises(ErroDeNegocio, match=mensagem):
        registros.criar_rascunho(s, partes['vendedor'].usuario, dados(partes))


def test_contraparte_sem_termos_aceitos_nao_pode_ser_escolhida(s, partes):
    sem_termos = fabricas.membro(s, termos=False)
    with pytest.raises(ErroDeNegocio, match='aceitaram os termos'):
        registros.criar_rascunho(s, partes['vendedor'].usuario, DadosPartes(V, partes['vendedor'].id, sem_termos.id))


# Isolamento por registro (arquitetura-seguranca.md, controle 1)


def test_rascunho_so_o_autor_ve(s, partes):
    r = criar(s, partes)
    assert registros.obter(s, partes['vendedor'].usuario, r.id) == r
    for quem in ('comprador', 'estranho'):
        assert registros.listar(s, partes[quem].usuario) == []
        with pytest.raises(NaoEncontrado):
            registros.obter(s, partes[quem].usuario, r.id)


def test_envelope_enviado_as_partes_ve_e_estranho_nao(s, partes):
    r = criar(s, partes, corretor=True)
    r.enviado_as_partes_em = datetime.now(UTC)
    for quem in ('comprador', 'corretor'):
        assert registros.obter(s, partes[quem].usuario, r.id) == r
    with pytest.raises(NaoEncontrado):
        registros.obter(s, partes['estranho'].usuario, r.id)


def test_operador_ve_tudo(s, partes):
    r = criar(s, partes)
    operador = fabricas.usuario(s, papel=Papel.OPERADOR)
    assert registros.obter(s, operador, r.id) == r


def test_so_o_autor_altera_e_so_em_rascunho(s, partes):
    r = criar(s, partes)
    r.enviado_as_partes_em = datetime.now(UTC)
    objeto = DadosObjeto('arabica', 10, Decimal(1500), 'Mogiana', 'Armazém Geral Franca', 12, 2099)
    with pytest.raises(NaoEncontrado):
        registros.salvar_objeto(s, partes['comprador'].usuario, r.id, objeto)
    r.estado = Estado.AGUARDANDO_ASSINATURAS
    with pytest.raises(ErroDeNegocio, match='rascunho'):
        registros.salvar_objeto(s, partes['vendedor'].usuario, r.id, objeto)


def test_pendencias_do_objeto(s, partes):
    r = criar(s, partes)
    assert len(registros.pendencias_objeto(r)) == 5
    registros.salvar_objeto(
        s,
        partes['vendedor'].usuario,
        r.id,
        DadosObjeto('arabica', 2000, Decimal(1395), 'Sul de Minas', 'Armazéns Gerais Varginha', 12, 2026),
    )
    assert registros.pendencias_objeto(r, hoje=date(2026, 11, 3)) == []
    assert registros.pendencias_objeto(r, hoje=date(2027, 1, 10)) == ['O mês de entrega já passou.']
    assert r.valor_total == Decimal(2790000)
    assert r.peso_kg == 120_000


def test_descartar_rascunho(s, partes):
    r = criar(s, partes)
    registros.descartar(s, partes['vendedor'].usuario, r.id)
    assert r.estado == Estado.CANCELADO
    assert registros.listar(s, partes['comprador'].usuario) == []
