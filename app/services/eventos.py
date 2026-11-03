from sqlalchemy.orm import Session

from app.domain.models import Evento, Usuario


def registrar(
    s: Session,
    *,
    autor: Usuario | None,
    tipo: str,
    entidade: str,
    entidade_id: int,
    descricao: str,
    dados: dict | None = None,
) -> Evento:
    evento = Evento(
        usuario_id=autor.id if autor else None,
        tipo=tipo,
        entidade=entidade,
        entidade_id=entidade_id,
        descricao=descricao,
        dados=dados or {},
    )
    s.add(evento)
    s.flush()
    return evento
