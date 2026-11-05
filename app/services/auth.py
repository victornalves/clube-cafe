from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import config
from app.domain.models import Usuario

_hasher = PasswordHasher()


def gerar_hash(senha: str) -> str:
    return _hasher.hash(senha)


def autenticar(s: Session, email: str, senha: str) -> Usuario | None:
    usuario = s.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario is None or not usuario.ativo:
        # Mesmo custo de hash com ou sem usuário, para não revelar quais e-mails existem
        _hasher.hash(senha)
        return None
    try:
        _hasher.verify(usuario.senha_hash, senha)
    except VerificationError:
        return None
    return usuario


def buscar(s: Session, usuario_id: int) -> Usuario | None:
    usuario = s.get(Usuario, usuario_id)
    return usuario if usuario and usuario.ativo else None


# Personas de demonstração (scripts.seed). Só elas entram sem senha, e só com CLUBE_LOGIN_DEMO ligado
PERSONAS_DEMO = [
    ('jose@membro.demo', 'José', 'Produtor, vende'),
    ('rodrigo@membro.demo', 'Rodrigo', 'Tostado Brasil, compra'),
    ('rogerio@membro.demo', 'Rogério', 'Corretor'),
    ('helena@membro.demo', 'Helena', 'Cooperativa, vende'),
    ('claudia.ferraz@membro.demo', 'Cláudia F.', 'Monte Verde, compra'),
    ('paulo@membro.demo', 'Paulo', 'Café Aurora, compra'),
    ('marta@membro.demo', 'Marta', 'Produtora sem matrícula'),
    ('claudia@backoffice.demo', 'Cláudia', 'Backoffice, operadora'),
]


def login_demo_ligado() -> bool:
    return config().login_demo


def autenticar_demo(s: Session, email: str) -> Usuario | None:
    if not login_demo_ligado() or email not in {e for e, _, _ in PERSONAS_DEMO}:
        return None
    usuario = s.scalar(select(Usuario).where(Usuario.email == email))
    return usuario if usuario and usuario.ativo else None
