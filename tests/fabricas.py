from datetime import UTC, date, datetime
from decimal import Decimal
from itertools import count

from app.domain.formatos import _digito
from app.domain.models import Membro, Papel, PapelNoRegistro, TipoPessoa, Usuario

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


ANO = date.today().year + 1


def partes_com_imovel(s) -> dict:
    """Vendedor com imóvel e matrícula, para passar na pré-validação."""
    vendedor = membro(s)
    vendedor.propriedade = 'Fazenda Santa Luzia'
    vendedor.matricula_imovel = '14.882'
    return {
        'vendedor': vendedor,
        'comprador': membro(s),
        'corretor': membro(s, corretor=True),
        'estranho': membro(s),
    }


def rascunho(s, partes, corretor=False, **objeto):
    from app.services import registros
    from app.services.registros import DadosObjeto, DadosPartes

    r = registros.criar_rascunho(
        s,
        partes['vendedor'].usuario,
        DadosPartes(
            PapelNoRegistro.VENDEDOR,
            partes['vendedor'].id,
            partes['comprador'].id,
            partes['corretor'].id if corretor else None,
        ),
    )
    dados = dict(
        produto='arabica',
        sacas=2000,
        preco_saca=Decimal(1395),
        regiao='Sul de Minas',
        armazem='Armazéns Gerais Varginha',
        entrega_mes=12,
        entrega_ano=ANO,
    )
    registros.salvar_objeto(s, partes['vendedor'].usuario, r.id, DadosObjeto(**{**dados, **objeto}))
    return r


def gerar(s, partes, r):
    from app.services import envelopes

    return envelopes.gerar_envelope(s, partes['vendedor'].usuario, r.id)
