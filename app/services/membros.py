from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domain.formatos import cnpj_valido, cpf_valido, email_valido, so_digitos
from app.domain.models import Membro, Papel, TipoPessoa, Usuario
from app.services import eventos
from app.services.auth import gerar_hash
from app.services.erros import ErroDeNegocio, NaoEncontrado, exigir_papel


@dataclass
class DadosMembro:
    email: str
    nome_usuario: str  # quem faz login; na PJ, normalmente o representante
    tipo_pessoa: TipoPessoa
    documento: str
    nome: str  # nome ou razão social
    cidade: str
    uf: str
    propriedade: str | None = None
    matricula_imovel: str | None = None
    representante_nome: str | None = None
    representante_cpf: str | None = None
    representante_cargo: str | None = None
    corretor: bool = False
    termos_aceitos: bool = False


def _validar(s: Session, dados: DadosMembro, membro_id: int | None = None) -> list[str]:
    erros = []
    documento = so_digitos(dados.documento)
    if dados.tipo_pessoa == TipoPessoa.PF and not cpf_valido(documento):
        erros.append('CPF inválido.')
    if dados.tipo_pessoa == TipoPessoa.PJ:
        if not cnpj_valido(documento):
            erros.append('CNPJ inválido.')
        if not dados.representante_nome:
            erros.append('Informe quem assina pela empresa.')
        if not cpf_valido(dados.representante_cpf or ''):
            erros.append('CPF de quem assina pela empresa inválido.')
    if not email_valido(dados.email):
        erros.append('E-mail inválido.')
    for campo, rotulo in [('nome_usuario', 'nome de quem acessa'), ('nome', 'nome'), ('cidade', 'cidade')]:
        if not (getattr(dados, campo) or '').strip():
            erros.append(f'Informe o {rotulo}.')
    if len((dados.uf or '').strip()) != 2:
        erros.append('UF precisa ter 2 letras.')

    mesmo_documento = s.scalar(select(Membro).where(Membro.documento == documento, Membro.id != membro_id))
    if mesmo_documento:
        erros.append(f'Já existe membro com este documento: {mesmo_documento.nome}.')
    usuario_atual = s.get(Membro, membro_id).usuario_id if membro_id else None
    mesmo_email = s.scalar(
        select(Usuario).where(Usuario.email == dados.email.strip().lower(), Usuario.id != usuario_atual)
    )
    if mesmo_email:
        erros.append('Já existe usuário com este e-mail.')
    return erros


def _aplicar(membro: Membro, dados: DadosMembro):
    pj = dados.tipo_pessoa == TipoPessoa.PJ
    membro.tipo_pessoa = dados.tipo_pessoa
    membro.documento = so_digitos(dados.documento)
    membro.nome = dados.nome.strip()
    membro.cidade = dados.cidade.strip()
    membro.uf = dados.uf.strip().upper()
    membro.propriedade = dados.propriedade or None
    membro.matricula_imovel = dados.matricula_imovel or None
    membro.representante_nome = dados.representante_nome if pj else None
    membro.representante_cpf = so_digitos(dados.representante_cpf or '') if pj else None
    membro.representante_cargo = dados.representante_cargo if pj else None
    membro.corretor = dados.corretor
    if dados.termos_aceitos and membro.termos_aceitos_em is None:
        membro.termos_aceitos_em = datetime.now(UTC)
    elif not dados.termos_aceitos:
        membro.termos_aceitos_em = None
    membro.usuario.email = dados.email.strip().lower()
    membro.usuario.nome = dados.nome_usuario.strip()


def listar(s: Session, operador: Usuario) -> list[Membro]:
    exigir_papel(operador, Papel.OPERADOR)
    return list(s.scalars(select(Membro).options(joinedload(Membro.usuario)).order_by(Membro.nome)))


def obter(s: Session, operador: Usuario, membro_id: int) -> Membro:
    exigir_papel(operador, Papel.OPERADOR)
    membro = s.get(Membro, membro_id)
    if membro is None:
        raise NaoEncontrado
    return membro


def criar(s: Session, operador: Usuario, dados: DadosMembro, senha_inicial: str) -> Membro:
    exigir_papel(operador, Papel.OPERADOR)
    erros = _validar(s, dados)
    if len(senha_inicial or '') < 6:
        erros.append('A senha inicial precisa ter pelo menos 6 caracteres.')
    if erros:
        raise ErroDeNegocio(' '.join(erros))
    membro = Membro(usuario=Usuario(senha_hash=gerar_hash(senha_inicial), papel=Papel.MEMBRO))
    _aplicar(membro, dados)
    s.add(membro)
    s.flush()
    eventos.registrar(
        s, autor=operador, tipo='membro_criado', entidade='membro', entidade_id=membro.id, descricao='Membro cadastrado'
    )
    return membro


def editar(s: Session, operador: Usuario, membro_id: int, dados: DadosMembro) -> Membro:
    membro = obter(s, operador, membro_id)
    if erros := _validar(s, dados, membro_id):
        raise ErroDeNegocio(' '.join(erros))
    _aplicar(membro, dados)
    eventos.registrar(
        s,
        autor=operador,
        tipo='membro_editado',
        entidade='membro',
        entidade_id=membro.id,
        descricao='Cadastro alterado',
    )
    return membro


def alterar_ativo(s: Session, operador: Usuario, membro_id: int, ativo: bool) -> Membro:
    membro = obter(s, operador, membro_id)
    membro.usuario.ativo = ativo
    eventos.registrar(
        s,
        autor=operador,
        tipo='membro_ativado' if ativo else 'membro_desativado',
        entidade='membro',
        entidade_id=membro.id,
        descricao='Acesso reativado' if ativo else 'Acesso desativado',
    )
    return membro


def selecionaveis(s: Session) -> list[Membro]:
    """Quem pode ser parte de um registro: ativo e com os termos aceitos (reunião 4, tela 05c)."""
    return list(
        s.scalars(
            select(Membro)
            .join(Membro.usuario)
            .where(Usuario.ativo, Membro.termos_aceitos_em.is_not(None))
            .order_by(Membro.nome)
        )
    )


def do_usuario(s: Session, usuario: Usuario) -> Membro:
    exigir_papel(usuario, Papel.MEMBRO)
    membro = s.scalar(select(Membro).where(Membro.usuario_id == usuario.id))
    if membro is None:
        raise NaoEncontrado
    return membro
