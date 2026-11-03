from datetime import UTC, datetime

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
        # Horário real, não o da transação: o now() do Postgres repete o início da transação
        momento=datetime.now(UTC),
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
