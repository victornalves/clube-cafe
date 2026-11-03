import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, LargeBinary, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.catalogos import KG_POR_SACA
from app.domain.estados import Estado


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


class PapelNoRegistro(enum.StrEnum):
    VENDEDOR = 'vendedor'  # emitente da CPR
    COMPRADOR = 'comprador'  # credor
    CORRETOR = 'corretor'  # intermediário, interveniente só no contrato


class Registro(Base):
    __tablename__ = 'registro'

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str | None] = mapped_column(String(20), unique=True)  # CRTC-AAAA-NNNN, definido após o insert
    estado: Mapped[Estado] = mapped_column(Enum(Estado, native_enum=False, length=30), default=Estado.RASCUNHO)

    autor_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'))
    papel_autor: Mapped[PapelNoRegistro] = mapped_column(Enum(PapelNoRegistro, native_enum=False, length=20))
    vendedor_id: Mapped[int] = mapped_column(ForeignKey('membro.id'))
    comprador_id: Mapped[int] = mapped_column(ForeignKey('membro.id'))
    corretor_id: Mapped[int | None] = mapped_column(ForeignKey('membro.id'))

    # Objeto, preço e entrega: vazios enquanto o rascunho não passou da etapa 2
    produto: Mapped[str | None] = mapped_column(String(30))
    sacas: Mapped[int | None]
    preco_saca: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    regiao: Mapped[str | None] = mapped_column(String(50))
    armazem: Mapped[str | None] = mapped_column(String(100))
    entrega_mes: Mapped[int | None]
    entrega_ano: Mapped[int | None]
    pagamento_adiantado: Mapped[bool] = mapped_column(default=False)

    # Primeira vez que o envelope abriu: a partir daí as outras partes enxergam o registro
    enviado_as_partes_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Registro na B3
    numero_controle_b3: Mapped[str | None] = mapped_column(String(30))
    registrado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Operador que assumiu a correção (tela 15, coluna "Responsável")
    responsavel_id: Mapped[int | None] = mapped_column(ForeignKey('usuario.id'))

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    autor: Mapped[Usuario] = relationship(foreign_keys=[autor_id])
    responsavel: Mapped[Usuario | None] = relationship(foreign_keys=[responsavel_id])
    vendedor: Mapped[Membro] = relationship(foreign_keys=[vendedor_id])
    comprador: Mapped[Membro] = relationship(foreign_keys=[comprador_id])
    corretor: Mapped[Membro | None] = relationship(foreign_keys=[corretor_id])
    envelopes: Mapped[list['Envelope']] = relationship(back_populates='registro', order_by='Envelope.versao')

    @property
    def peso_kg(self) -> int | None:
        return self.sacas * KG_POR_SACA if self.sacas else None

    @property
    def valor_total(self) -> Decimal | None:
        return self.sacas * self.preco_saca if self.sacas and self.preco_saca else None

    def membro_ids(self) -> set[int]:
        return {i for i in (self.vendedor_id, self.comprador_id, self.corretor_id) if i}


class SituacaoEnvelope(enum.StrEnum):
    ABERTO = 'aberto'
    CONCLUIDO = 'concluido'
    EXPIRADO = 'expirado'
    CANCELADO = 'cancelado'


class Envelope(Base):
    """Envelope único (contrato + CPR), com janela curta (RN-119). Reabrir a janela cria uma versão nova."""

    __tablename__ = 'envelope'
    __table_args__ = (UniqueConstraint('registro_id', 'versao'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    registro_id: Mapped[int] = mapped_column(ForeignKey('registro.id'))
    versao: Mapped[int]
    situacao: Mapped[SituacaoEnvelope] = mapped_column(
        Enum(SituacaoEnvelope, native_enum=False, length=20), default=SituacaoEnvelope.ABERTO
    )
    aberto_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    encerrado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    registro: Mapped[Registro] = relationship(back_populates='envelopes')
    documentos: Mapped[list['Documento']] = relationship(back_populates='envelope', order_by='Documento.id')
    assinaturas: Mapped[list['Assinatura']] = relationship(back_populates='envelope', order_by='Assinatura.id')

    def pendentes(self) -> list['Assinatura']:
        return [a for a in self.assinaturas if a.assinado_em is None]


class TipoDocumento(enum.StrEnum):
    CONTRATO = 'contrato'
    CPR = 'cpr'


class Documento(Base):
    """PDF guardado no banco no MVP. Na Fase 1, storage privado com URL assinada curta."""

    __tablename__ = 'documento'

    id: Mapped[int] = mapped_column(primary_key=True)
    envelope_id: Mapped[int] = mapped_column(ForeignKey('envelope.id'))
    tipo: Mapped[TipoDocumento] = mapped_column(Enum(TipoDocumento, native_enum=False, length=20))
    pdf: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    sha256: Mapped[str] = mapped_column(String(64))

    envelope: Mapped[Envelope] = relationship(back_populates='documentos')


class Assinatura(Base):
    __tablename__ = 'assinatura'
    __table_args__ = (UniqueConstraint('envelope_id', 'membro_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    envelope_id: Mapped[int] = mapped_column(ForeignKey('envelope.id'))
    membro_id: Mapped[int] = mapped_column(ForeignKey('membro.id'))
    papel: Mapped[PapelNoRegistro] = mapped_column(Enum(PapelNoRegistro, native_enum=False, length=20))
    nome_assinante: Mapped[str] = mapped_column(String(200))  # na PJ, quem assina pela empresa
    assinado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    envelope: Mapped[Envelope] = relationship(back_populates='assinaturas')
    membro: Mapped[Membro] = relationship()

    @property
    def documentos(self) -> list[TipoDocumento]:
        # O corretor é interveniente só no contrato, não na CPR (pendência 1.45)
        if self.papel == PapelNoRegistro.CORRETOR:
            return [TipoDocumento.CONTRATO]
        return [TipoDocumento.CONTRATO, TipoDocumento.CPR]


class DominioB3(Base):
    """Lista provisória dos domínios fechados da B3 (produto, unidade). Troca-se sem mexer no código."""

    __tablename__ = 'dominio_b3'
    __table_args__ = (UniqueConstraint('tipo', 'codigo'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30))
    codigo: Mapped[str] = mapped_column(String(30))
    descricao: Mapped[str] = mapped_column(String(100))
    ativo: Mapped[bool] = mapped_column(default=True)


class EnvioB3(Base):
    """Cada chamada à B3, envio ou consulta, com payload e resposta inteiros (tela 16)."""

    __tablename__ = 'envio_b3'

    id: Mapped[int] = mapped_column(primary_key=True)
    registro_id: Mapped[int] = mapped_column(ForeignKey('registro.id'))
    momento: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    operacao: Mapped[str] = mapped_column(String(20))  # envio | consulta
    automatico: Mapped[bool]
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('usuario.id'))
    status_http: Mapped[int]
    resultado: Mapped[str] = mapped_column(
        String(20)
    )  # sucesso | transitorio | definitivo | encontrado | nao_encontrado
    mensagem: Mapped[str] = mapped_column(String(300))
    payload: Mapped[dict | None] = mapped_column(JSON)
    resposta: Mapped[dict] = mapped_column(JSON)


# Simulação da B3: some na Fase 3, quando a integração real entrar


class SimuladorB3(Base):
    """Uma linha só: o que a B3 simulada responde nos próximos envios."""

    __tablename__ = 'simulador_b3'

    id: Mapped[int] = mapped_column(primary_key=True)
    modo: Mapped[str] = mapped_column(String(30), default='sucesso')


class CprNaB3Simulada(Base):
    """O "lado da B3": o que ela registrou. Permite consultar antes de reenviar."""

    __tablename__ = 'cpr_na_b3_simulada'

    id: Mapped[int] = mapped_column(primary_key=True)
    chave: Mapped[str] = mapped_column(String(40), unique=True)
    numero_controle: Mapped[str] = mapped_column(String(30))
    registrado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
