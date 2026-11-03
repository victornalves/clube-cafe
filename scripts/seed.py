"""Dados fictícios de demonstração. Pode rodar mais de uma vez: quem já existe é mantido.

uv run python -m scripts.seed
"""

from datetime import UTC, datetime

from sqlalchemy import select

from app.db import sessao
from app.domain.models import Membro, Papel, TipoPessoa, Usuario
from app.services.auth import gerar_hash

SENHA_DEMO = 'cafe123'

OPERADORES = [('claudia@backoffice.demo', 'Cláudia Bittencourt Salgado')]

MEMBROS = [
    dict(
        email='jose@membro.demo',
        nome='José Ribamar Andrade',
        tipo_pessoa=TipoPessoa.PF,
        documento='48291376015',
        cidade='Varginha',
        uf='MG',
        propriedade='Fazenda Santa Luzia — Sul de Minas',
        matricula_imovel='14.882 — 1º Ofício de Registro de Imóveis de Varginha/MG',
    ),
    dict(
        email='rodrigo@membro.demo',
        nome='Tostado Brasil Comércio de Café Ltda',
        nome_usuario='Rodrigo Sampaio Leite',
        tipo_pessoa=TipoPessoa.PJ,
        documento='09455218000173',
        cidade='Santos',
        uf='SP',
        representante_nome='Rodrigo Sampaio Leite',
        representante_cpf='14822037706',
        representante_cargo='Procurador',
    ),
    dict(
        email='marta@membro.demo',
        nome='Marta Yumi Sakamoto',
        tipo_pessoa=TipoPessoa.PF,
        documento='31845207968',
        cidade='Patrocínio',
        uf='MG',
        propriedade='Sítio Bela Vista — Cerrado Mineiro',
    ),
    dict(
        email='rogerio@membro.demo',
        nome='Rogério Pacheco Vilela',
        tipo_pessoa=TipoPessoa.PF,
        documento='70531928406',
        cidade='Três Pontas',
        uf='MG',
        corretor=True,
    ),
]


def main():
    hash_demo = gerar_hash(SENHA_DEMO)
    with sessao() as s:
        existentes = set(s.scalars(select(Usuario.email)))
        for email, nome in OPERADORES:
            if email not in existentes:
                s.add(Usuario(email=email, nome=nome, senha_hash=hash_demo, papel=Papel.OPERADOR))
        for dados in MEMBROS:
            dados = dict(dados)
            email = dados.pop('email')
            if email in existentes:
                continue
            nome_usuario = dados.pop('nome_usuario', dados['nome'])
            usuario = Usuario(email=email, nome=nome_usuario, senha_hash=hash_demo, papel=Papel.MEMBRO)
            usuario.membro = Membro(**dados, termos_aceitos_em=datetime.now(UTC))
            s.add(usuario)
    print(f'Pronto. Senha de todos os usuários de demonstração: {SENHA_DEMO}')


if __name__ == '__main__':
    main()
