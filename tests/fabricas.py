from datetime import UTC, datetime
from itertools import count

from app.domain.formatos import _digito
from app.domain.models import Membro, Papel, TipoPessoa, Usuario

_seq = count(1)


def cpf_valido(n: int) -> str:
    """CPF fictício com dígitos verificadores corretos, único por n."""
    base = f'{n:09d}'
    d1 = _digito(base, list(range(10, 1, -1)))
    return base + d1 + _digito(base + d1, list(range(11, 1, -1)))


def usuario(s, papel=Papel.MEMBRO, **kwargs) -> Usuario:
    n = next(_seq)
    u = Usuario(email=f'u{n}@teste', nome=f'Usuário {n}', senha_hash='x', papel=papel, **kwargs)
    s.add(u)
    s.flush()
    return u


def membro(s, *, corretor=False, termos=True, ativo=True) -> Membro:
    n = next(_seq)
    m = Membro(
        usuario=Usuario(email=f'm{n}@teste', nome=f'Membro {n}', senha_hash='x', papel=Papel.MEMBRO, ativo=ativo),
        tipo_pessoa=TipoPessoa.PF,
        documento=cpf_valido(n + 100_000),
        nome=f'Membro {n}',
        cidade='Varginha',
        uf='MG',
        corretor=corretor,
        termos_aceitos_em=datetime.now(UTC) if termos else None,
    )
    s.add(m)
    s.flush()
    return m
