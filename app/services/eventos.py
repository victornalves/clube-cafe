from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import Evento, Papel, Registro, Usuario
from app.services.erros import exigir_papel


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


def listar(s: Session, operador: Usuario, limite: int = 1000) -> list[tuple[Evento, str | None, str | None]]:
    """Tela 17: o log inteiro, mais recente primeiro, com quem fez (None se foi o sistema) e o nº do registro."""
    exigir_papel(operador, Papel.OPERADOR)
    consulta = (
        select(Evento, Usuario.nome, Registro.numero)
        .outerjoin(Usuario, Usuario.id == Evento.usuario_id)
        .outerjoin(Registro, (Evento.entidade == 'registro') & (Registro.id == Evento.entidade_id))
        .order_by(Evento.id.desc())
        .limit(limite)
    )
    return [tuple(linha) for linha in s.execute(consulta)]


def do_registro(s: Session, operador: Usuario, registro_id: int) -> list[tuple[Evento, str | None]]:
    """Linha do tempo completa do backoffice, inclusive o que o membro não vê."""
    exigir_papel(operador, Papel.OPERADOR)
    consulta = (
        select(Evento, Usuario.nome)
        .outerjoin(Usuario, Usuario.id == Evento.usuario_id)
        .where(Evento.entidade == 'registro', Evento.entidade_id == registro_id)
        .order_by(Evento.momento, Evento.id)
    )
    return [tuple(linha) for linha in s.execute(consulta)]
