from datetime import UTC, datetime
from itertools import count

from app.domain.models import Membro, Papel, TipoPessoa, Usuario

# CPFs válidos, fictícios
CPFS = ['48291376069', '31845207904', '70531928497', '14822037746', '52998224725', '11144477735']
_seq = count()


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
        documento=CPFS[n % len(CPFS)] if n < len(CPFS) else f'{n:011d}',
        nome=f'Membro {n}',
        cidade='Varginha',
        uf='MG',
        corretor=corretor,
        termos_aceitos_em=datetime.now(UTC) if termos else None,
    )
    s.add(m)
    s.flush()
    return m
