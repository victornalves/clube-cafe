from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import config

engine = create_engine(config().database_url)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


@contextmanager
def sessao() -> Iterator[Session]:
    """Uma transação por caso de uso: commit no fim, rollback se der erro."""
    with SessionLocal() as s:
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
