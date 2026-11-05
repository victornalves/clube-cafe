"""Casos de uso do registro. Toda função recebe o usuário e filtra na origem (arquitetura-seguranca.md, controle 1)."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.domain import estados
from app.domain.catalogos import ARMAZENS_POR_REGIAO, PRODUTOS
from app.domain.estados import Estado, Quem
from app.domain.models import Envelope, Membro, Papel, PapelNoRegistro, Registro, Usuario
from app.services import eventos, membros
from app.services.erros import ErroDeNegocio, NaoEncontrado


@dataclass
class DadosPartes:
    papel_autor: PapelNoRegistro
    vendedor_id: int | None
    comprador_id: int | None
    corretor_id: int | None = None


@dataclass
class DadosObjeto:
    produto: str | None
    sacas: int | None
    preco_saca: Decimal | None
    regiao: str | None
    armazem: str | None
    entrega_mes: int | None
    entrega_ano: int | None
    pagamento_adiantado: bool = False


def _visiveis(usuario: Usuario) -> Select:
    consulta = select(Registro).options(
        joinedload(Registro.vendedor),
        joinedload(Registro.comprador),
        joinedload(Registro.corretor),
        selectinload(Registro.envelopes).selectinload(Envelope.assinaturas),
        selectinload(Registro.envelopes).selectinload(Envelope.documentos),
    )
    if usuario.papel == Papel.OPERADOR:
        return consulta
    # Membro: o autor vê sempre; as outras partes, só depois que o envelope chegou até elas.
    # Rascunho descartado nunca aparece para quem não o criou.
    membro_id = select(Membro.id).where(Membro.usuario_id == usuario.id).scalar_subquery()
    e_parte = or_(
        Registro.vendedor_id == membro_id, Registro.comprador_id == membro_id, Registro.corretor_id == membro_id
    )
    return consulta.where(
        or_(Registro.autor_id == usuario.id, and_(e_parte, Registro.enviado_as_partes_em.is_not(None)))
    )


def listar(s: Session, usuario: Usuario) -> list[Registro]:
    return list(s.scalars(_visiveis(usuario).order_by(Registro.atualizado_em.desc())).unique())


def obter(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    registro = s.scalars(_visiveis(usuario).where(Registro.id == registro_id)).unique().one_or_none()
    if registro is None:
        raise NaoEncontrado
    return registro


def rascunho_do_autor(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    registro = obter(s, usuario, registro_id)
    if registro.autor_id != usuario.id:
        raise NaoEncontrado
    if registro.estado != Estado.RASCUNHO:
        raise ErroDeNegocio('Só é possível alterar um registro em rascunho.')
    return registro


def _validar_partes(s: Session, usuario: Usuario, dados: DadosPartes) -> list[str]:
    eu = membros.do_usuario(s, usuario)
    erros = []
    esperado = {
        PapelNoRegistro.VENDEDOR: dados.vendedor_id,
        PapelNoRegistro.COMPRADOR: dados.comprador_id,
        PapelNoRegistro.CORRETOR: dados.corretor_id,
    }[dados.papel_autor]
    if esperado != eu.id:
        erros.append('Você precisa ocupar o papel que escolheu.')
    if dados.papel_autor == PapelNoRegistro.CORRETOR and not eu.corretor:
        erros.append('Seu cadastro não é de corretor.')
    if not dados.vendedor_id:
        erros.append('Informe o vendedor.')
    if not dados.comprador_id:
        erros.append('Informe o comprador.')
    ids = [i for i in (dados.vendedor_id, dados.comprador_id, dados.corretor_id) if i]
    if len(ids) != len(set(ids)):
        erros.append('A mesma pessoa não pode ocupar dois papéis.')

    selecionaveis = {m.id: m for m in membros.selecionaveis(s)}
    for i in ids:
        if i not in selecionaveis:
            erros.append('Todas as partes precisam ser membros ativos que já aceitaram os termos da Câmara.')
            break
    if dados.corretor_id in selecionaveis and not selecionaveis[dados.corretor_id].corretor:
        erros.append('O intermediário escolhido não é corretor.')
    return erros


def criar_rascunho(s: Session, usuario: Usuario, dados: DadosPartes) -> Registro:
    if erros := _validar_partes(s, usuario, dados):
        raise ErroDeNegocio(' '.join(erros))
    registro = Registro(
        autor_id=usuario.id,
        papel_autor=dados.papel_autor,
        vendedor_id=dados.vendedor_id,
        comprador_id=dados.comprador_id,
        corretor_id=dados.corretor_id,
    )
    s.add(registro)
    s.flush()
    registro.numero = f'CRTC-{date.today().year}-{registro.id:04d}'
    eventos.registrar(
        s, autor=usuario, tipo='registro_criado', entidade='registro', entidade_id=registro.id,
        descricao=f'{usuario.nome} criou o registro',
    )  # fmt: skip
    return registro


def salvar_partes(s: Session, usuario: Usuario, registro_id: int, dados: DadosPartes) -> Registro:
    registro = rascunho_do_autor(s, usuario, registro_id)
    if erros := _validar_partes(s, usuario, dados):
        raise ErroDeNegocio(' '.join(erros))
    registro.papel_autor = dados.papel_autor
    registro.vendedor_id = dados.vendedor_id
    registro.comprador_id = dados.comprador_id
    registro.corretor_id = dados.corretor_id
    eventos.registrar(
        s, autor=usuario, tipo='partes_alteradas', entidade='registro', entidade_id=registro.id,
        descricao='Partes alteradas',
    )  # fmt: skip
    return registro


def salvar_objeto(s: Session, usuario: Usuario, registro_id: int, dados: DadosObjeto) -> Registro:
    """Grava mesmo incompleto: o rascunho é salvo a cada etapa (conexão fraca no campo)."""
    registro = rascunho_do_autor(s, usuario, registro_id)
    for campo, valor in vars(dados).items():
        setattr(registro, campo, valor)
    eventos.registrar(
        s, autor=usuario, tipo='objeto_alterado', entidade='registro', entidade_id=registro.id,
        descricao='Objeto, preço e entrega alterados',
    )  # fmt: skip
    return registro


def pendencias_objeto(registro: Registro, hoje: date | None = None) -> list[str]:
    """O que falta para o rascunho seguir para a revisão."""
    hoje = hoje or date.today()
    erros = []
    if registro.produto not in PRODUTOS:
        erros.append('Escolha o produto.')
    if not registro.sacas or registro.sacas <= 0:
        erros.append('Informe a quantidade de sacas.')
    if not registro.preco_saca or registro.preco_saca <= 0:
        erros.append('Informe o preço por saca.')
    if registro.regiao not in ARMAZENS_POR_REGIAO:
        erros.append('Escolha a região.')
    elif registro.armazem not in ARMAZENS_POR_REGIAO[registro.regiao]:
        erros.append('Escolha o armazém de entrega.')
    if not registro.entrega_mes or not registro.entrega_ano:
        erros.append('Informe o mês e o ano de entrega.')
    elif (registro.entrega_ano, registro.entrega_mes) < (hoje.year, hoje.month):
        erros.append('O mês de entrega já passou.')
    return erros


def transicionar(
    s: Session,
    registro: Registro,
    acao: str,
    quem: Quem,
    *,
    autor: Usuario | None,
    descricao: str,
    dados: dict | None = None,
) -> estados.Transicao:
    """Única porta de mudança de estado: valida na tabela e grava o evento."""
    origem = registro.estado
    t = estados.transicao(acao, origem, quem)
    registro.estado = t.destino
    eventos.registrar(
        s, autor=autor, tipo=acao, entidade='registro', entidade_id=registro.id, descricao=descricao,
        dados={'de': origem.value, 'para': t.destino.value, 'referencia': t.referencia, **(dados or {})},
    )  # fmt: skip
    return t


def descartar(s: Session, usuario: Usuario, registro_id: int) -> Registro:
    registro = rascunho_do_autor(s, usuario, registro_id)
    transicionar(s, registro, 'descartar', Quem.AUTOR, autor=usuario, descricao=f'{usuario.nome} descartou o rascunho')
    return registro
