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
        documento='48291376069',
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
        documento='09455218000105',
        cidade='Santos',
        uf='SP',
        representante_nome='Rodrigo Sampaio Leite',
        representante_cpf='14822037746',
        representante_cargo='Procurador',
    ),
    dict(
        email='marta@membro.demo',
        nome='Marta Yumi Sakamoto',
        tipo_pessoa=TipoPessoa.PF,
        documento='31845207904',
        cidade='Patrocínio',
        uf='MG',
        propriedade='Sítio Bela Vista — Cerrado Mineiro',
    ),
    dict(
        email='rogerio@membro.demo',
        nome='Rogério Pacheco Vilela',
        tipo_pessoa=TipoPessoa.PF,
        documento='70531928497',
        cidade='Três Pontas',
        uf='MG',
        corretor=True,
    ),
    dict(
        email='helena@membro.demo',
        nome='Cooperativa Agrária do Sul de Minas',
        nome_usuario='Helena Duarte Ribeiro',
        tipo_pessoa=TipoPessoa.PJ,
        documento='21884653000150',
        cidade='Varginha',
        uf='MG',
        propriedade='Lavouras dos cooperados',  # até 35 caracteres (B3)
        matricula_imovel='Diversas — 1º Ofício de Varginha/MG',
        representante_nome='Helena Duarte Ribeiro',
        representante_cpf='26371845071',
        representante_cargo='Diretora comercial',
    ),
    dict(
        email='claudia.ferraz@membro.demo',
        nome='Exportadora Monte Verde Ltda',
        nome_usuario='Cláudia Ferraz Pimentel',
        tipo_pessoa=TipoPessoa.PJ,
        documento='13772046000170',
        cidade='Santos',
        uf='SP',
        representante_nome='Cláudia Ferraz Pimentel',
        representante_cpf='59401728305',
        representante_cargo='Sócia-administradora',
    ),
    dict(
        email='paulo@membro.demo',
        nome='Café Aurora Exportação S.A.',
        nome_usuario='Paulo Henrique Tamashiro',
        tipo_pessoa=TipoPessoa.PJ,
        documento='05661328000172',
        cidade='São Paulo',
        uf='SP',
        representante_nome='Paulo Henrique Tamashiro',
        representante_cpf='38120657462',
        representante_cargo='Diretor de originação',
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
