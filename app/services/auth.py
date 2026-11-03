from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select
from sqlalchemy.orm import Session

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
