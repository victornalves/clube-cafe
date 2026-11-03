import pytest

from app.domain.models import Papel, TipoPessoa
from app.services import membros
from app.services.erros import AcessoNegado, ErroDeNegocio
from app.services.membros import DadosMembro
from tests import fabricas


def dados(**kwargs) -> DadosMembro:
    base = dict(
        email='novo@teste.com',
        nome_usuario='Ana Souza',
        tipo_pessoa=TipoPessoa.PF,
        documento='529.982.247-25',
        nome='Ana Souza',
        cidade='Varginha',
        uf='mg',
    )
    return DadosMembro(**{**base, **kwargs})


@pytest.fixture
def operador(s):
    return fabricas.usuario(s, papel=Papel.OPERADOR)


def test_operador_cadastra_membro(s, operador):
    m = membros.criar(s, operador, dados(), 'senha123')
    assert m.documento == '52998224725'
    assert m.uf == 'MG'
    assert m.usuario.papel == Papel.MEMBRO
    assert m.termos_aceitos_em is None


def test_membro_nao_cadastra(s):
    membro = fabricas.membro(s)
    with pytest.raises(AcessoNegado):
        membros.criar(s, membro.usuario, dados(), 'senha123')


def test_pj_exige_representante(s, operador):
    with pytest.raises(ErroDeNegocio, match='quem assina pela empresa'):
        membros.criar(s, operador, dados(tipo_pessoa=TipoPessoa.PJ, documento='09455218000105'), 'senha123')


def test_documento_e_email_unicos(s, operador):
    membros.criar(s, operador, dados(), 'senha123')
    with pytest.raises(ErroDeNegocio, match='documento') as erro:
        membros.criar(s, operador, dados(email='NOVO@teste.com'), 'senha123')
    assert 'e-mail' in str(erro.value)


def test_editar_nao_conflita_consigo_mesmo(s, operador):
    m = membros.criar(s, operador, dados(), 'senha123')
    membros.editar(s, operador, m.id, dados(cidade='Três Pontas', termos_aceitos=True))
    assert m.cidade == 'Três Pontas'
    assert m.termos_aceitos_em is not None


def test_desativado_nao_e_selecionavel(s, operador):
    m = membros.criar(s, operador, dados(termos_aceitos=True), 'senha123')
    assert m in membros.selecionaveis(s)
    membros.alterar_ativo(s, operador, m.id, False)
    assert m not in membros.selecionaveis(s)
