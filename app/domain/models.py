import enum
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Papel(enum.StrEnum):
    # Membro e backoffice nunca na mesma conta (RN-40). Aprovador e auditor entram depois.
    MEMBRO = 'membro'
    OPERADOR = 'operador'


class TipoPessoa(enum.StrEnum):
    PF = 'PF'
    PJ = 'PJ'


class Usuario(Base):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    nome: Mapped[str] = mapped_column(String(200))
    senha_hash: Mapped[str] = mapped_column(String(200))
    papel: Mapped[Papel] = mapped_column(Enum(Papel, native_enum=False, length=20))
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    membro: Mapped['Membro | None'] = relationship(back_populates='usuario')


class Membro(Base):
    """Quem pode ser parte de um registro. Cadastrado pelo backoffice enquanto a proposta de adesão está fora do MVP."""

    __tablename__ = 'membro'

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'), unique=True)
    tipo_pessoa: Mapped[TipoPessoa] = mapped_column(Enum(TipoPessoa, native_enum=False, length=2))
    documento: Mapped[str] = mapped_column(String(14), unique=True)  # CPF ou CNPJ, só dígitos
    nome: Mapped[str] = mapped_column(String(200))  # nome ou razão social
    cidade: Mapped[str] = mapped_column(String(100))
    uf: Mapped[str] = mapped_column(String(2))
    propriedade: Mapped[str | None] = mapped_column(String(200))
    matricula_imovel: Mapped[str | None] = mapped_column(String(200))
    # Pessoa jurídica: quem assina pela empresa
    representante_nome: Mapped[str | None] = mapped_column(String(200))
    representante_cpf: Mapped[str | None] = mapped_column(String(11))
    representante_cargo: Mapped[str | None] = mapped_column(String(100))
    corretor: Mapped[bool] = mapped_column(default=False)
    # Flag marcada pelo backoffice até o fluxo de termos existir (pendência 1.43)
    termos_aceitos_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    membro_desde: Mapped[date] = mapped_column(Date, server_default=func.current_date())

    usuario: Mapped[Usuario] = relationship(back_populates='membro')


class Evento(Base):
    """Log de eventos, append-only (RN-44). Uma trigger no banco recusa UPDATE e DELETE."""

    __tablename__ = 'evento'

    id: Mapped[int] = mapped_column(primary_key=True)
    momento: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('usuario.id'))  # None quando é o sistema
    tipo: Mapped[str] = mapped_column(String(50))
    entidade: Mapped[str] = mapped_column(String(50))
    entidade_id: Mapped[int] = mapped_column()
    descricao: Mapped[str] = mapped_column(String(500))
    dados: Mapped[dict] = mapped_column(JSON, default=dict)
