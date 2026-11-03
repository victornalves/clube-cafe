import os

# Antes de importar qualquer coisa de app/: os testes rodam no banco de teste
os.environ['CLUBE_DATABASE_URL'] = os.environ.get(
    'CLUBE_TEST_DATABASE_URL', 'postgresql+psycopg://clube:clube@localhost:5433/clube_cafe_teste'
)

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy.orm import Session

from app.db import engine


@pytest.fixture(scope='session', autouse=True)
def banco():
    command.upgrade(AlembicConfig('alembic.ini'), 'head')


@pytest.fixture
def s():
    """Sessão dentro de uma transação desfeita no fim de cada teste."""
    with engine.connect() as conexao:
        transacao = conexao.begin()
        sessao = Session(bind=conexao, join_transaction_mode='create_savepoint')
        yield sessao
        sessao.close()
        transacao.rollback()
