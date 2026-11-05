import pytest
from sqlalchemy import delete, update
from sqlalchemy.exc import DBAPIError

from app.domain.models import Evento, Papel, Usuario
from app.services import auth, eventos


@pytest.fixture
def jose(s):
    usuario = Usuario(email='jose@teste', nome='José', senha_hash=auth.gerar_hash('certa'), papel=Papel.MEMBRO)
    s.add(usuario)
    s.flush()
    return usuario


def test_autentica_com_senha_certa(s, jose):
    assert auth.autenticar(s, ' JOSE@teste ', 'certa') == jose


def test_recusa_senha_errada_e_email_inexistente(s, jose):
    assert auth.autenticar(s, 'jose@teste', 'errada') is None
    assert auth.autenticar(s, 'ninguem@teste', 'certa') is None


def test_recusa_usuario_inativo(s, jose):
    jose.ativo = False
    assert auth.autenticar(s, 'jose@teste', 'certa') is None


@pytest.mark.parametrize('comando', [update(Evento).values(descricao='alterado'), delete(Evento)])
def test_log_de_eventos_e_append_only(s, jose, comando):
    eventos.registrar(s, autor=jose, tipo='teste', entidade='usuario', entidade_id=jose.id, descricao='criado')
    with pytest.raises(DBAPIError, match='append-only'):
        s.execute(comando)


def test_login_demo_so_para_personas_e_com_a_flag(s, monkeypatch):
    from app.config import config

    jose = Usuario(email='jose@membro.demo', nome='José', senha_hash='x', papel=Papel.MEMBRO)
    intruso = Usuario(email='intruso@teste.com', nome='Intruso', senha_hash='x', papel=Papel.MEMBRO)
    s.add_all([jose, intruso])
    s.flush()
    monkeypatch.setattr(config(), 'login_demo', True)
    assert auth.autenticar_demo(s, 'jose@membro.demo') == jose
    assert auth.autenticar_demo(s, 'intruso@teste.com') is None  # fora da lista de personas
    monkeypatch.setattr(config(), 'login_demo', False)
    assert auth.autenticar_demo(s, 'jose@membro.demo') is None
