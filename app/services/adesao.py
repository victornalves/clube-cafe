"""Proposta de adesão: envio público, assinatura por link, diligência e decisão do comitê materializada pelo backoffice.

Regras em regras-de-negocio.md §1; decisões do MVP em plano-mvp.md, Marco 4.
"""

import secrets
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, undefer

from app.config import config
from app.domain import adesao
from app.domain.adesao import QuemAdesao, SituacaoProposta
from app.domain.formatos import cnpj_valido, cpf_valido, email_valido, formatar_documento, so_digitos
from app.domain.models import (
    AnexoProposta,
    Atuacao,
    Membro,
    Papel,
    PropostaAdesao,
    SignatarioProposta,
    TipoPessoa,
    Usuario,
)
from app.services import emails, eventos
from app.services.erros import ErroDeNegocio, NaoEncontrado, exigir_papel

S = SituacaoProposta
TAMANHO_MAXIMO = 10 * 1024 * 1024
TIPOS_ACEITOS = {'application/pdf', 'image/jpeg', 'image/png'}
VERSAO_TERMOS = '1'


@dataclass
class Arquivo:
    nome: str
    content_type: str
    conteudo: bytes


@dataclass
class DadosProponente:
    nome: str
    email: str
    telefone: str
    carta: Arquivo | None


@dataclass
class DadosProposta:
    nome: str
    documento: str
    atuacao: Atuacao
    email: str
    telefone: str
    cidade: str
    uf: str
    proponentes: list[DadosProponente]
    propriedade: str | None = None
    sacas_safra: int | None = None
    representante_nome: str | None = None
    representante_cpf: str | None = None
    corretor_nome: str | None = None
    corretor_email: str | None = None
    documentos: list[Arquivo] = field(default_factory=list)


@dataclass
class DadosDecisao:
    decisao: str  # aprovar | recusar
    reuniao_data: date | None
    reuniao_presentes: str = ''
    parecer: str = ''
    motivo_recusa: str = ''


class DocumentoDeMembroAtivo(Exception):
    """RN-07: quem já é membro vai para o login, sem que a tela revele que a conta existe."""


def _agora() -> datetime:
    return datetime.now(UTC)


def _token() -> str:
    return secrets.token_urlsafe(24)


def _telefone_valido(telefone: str) -> bool:
    return len(so_digitos(telefone)) in (10, 11)


def _validar_arquivo(arquivo: Arquivo, rotulo: str) -> list[str]:
    erros = []
    if arquivo.content_type not in TIPOS_ACEITOS:
        erros.append(f'{rotulo}: envie PDF, JPG ou PNG.')
    if len(arquivo.conteudo) > TAMANHO_MAXIMO:
        erros.append(f'{rotulo}: o arquivo passa de 10 MB.')
    return erros


def _validar(dados: DadosProposta) -> list[str]:
    """Reprova formato, nunca aprova mérito (RN-06)."""
    erros = []
    documento = so_digitos(dados.documento)
    if len(documento) == 11 and not cpf_valido(documento) or len(documento) == 14 and not cnpj_valido(documento):
        erros.append('CPF ou CNPJ inválido.')
    elif len(documento) not in (11, 14):
        erros.append('Informe um CPF (11 dígitos) ou CNPJ (14 dígitos).')
    if len(documento) == 14:
        if not (dados.representante_nome or '').strip():
            erros.append('Informe quem assina pela empresa.')
        if not cpf_valido(dados.representante_cpf or ''):
            erros.append('CPF de quem assina pela empresa inválido.')
    for campo, rotulo in [('nome', 'o nome ou a razão social'), ('cidade', 'o município')]:
        if not (getattr(dados, campo) or '').strip():
            erros.append(f'Informe {rotulo}.')
    if len((dados.uf or '').strip()) != 2:
        erros.append('Escolha o estado.')
    if not email_valido(dados.email):
        erros.append('E-mail do candidato inválido.')
    if not _telefone_valido(dados.telefone):
        erros.append('Telefone do candidato precisa ter DDD e 8 ou 9 dígitos.')
    if dados.corretor_email is not None and (
        not (dados.corretor_nome or '').strip() or not email_valido(dados.corretor_email)
    ):
        erros.append('Informe o nome e um e-mail válido do corretor que está preenchendo.')

    # Exatamente 2 proponentes, distintos entre si e do candidato (RN-101)
    if len(dados.proponentes) != 2:
        erros.append('Indique exatamente 2 proponentes.')
    emails_vistos = {dados.email.strip().lower()}
    for i, p in enumerate(dados.proponentes, start=1):
        if not p.nome.strip():
            erros.append(f'Proponente {i}: informe o nome.')
        if not email_valido(p.email):
            erros.append(f'Proponente {i}: e-mail inválido.')
        elif p.email.strip().lower() in emails_vistos:
            erros.append(f'Proponente {i}: o e-mail repete o do candidato ou do outro proponente.')
        emails_vistos.add(p.email.strip().lower())
        if not _telefone_valido(p.telefone):
            erros.append(f'Proponente {i}: telefone precisa ter DDD e 8 ou 9 dígitos.')
        if p.carta is None:
            erros.append(f'Proponente {i}: anexe a carta de recomendação.')
        else:
            erros += _validar_arquivo(p.carta, f'Carta do proponente {i}')
    for arquivo in dados.documentos:
        erros += _validar_arquivo(arquivo, arquivo.nome)
    return erros


def _membro_ativo_por_documento(s: Session, documento: str) -> Membro | None:
    return s.scalar(select(Membro).join(Membro.usuario).where(Membro.documento == documento, Usuario.ativo.is_(True)))


def _membro_por_email(s: Session, email: str) -> Membro | None:
    return s.scalar(select(Membro).join(Membro.usuario).where(Usuario.email == email.strip().lower()))


def _anexo(arquivo: Arquivo, tipo: str, signatario: SignatarioProposta | None = None) -> AnexoProposta:
    return AnexoProposta(
        tipo=tipo,
        signatario=signatario,
        nome_arquivo=arquivo.nome[:200],
        content_type=arquivo.content_type,
        tamanho=len(arquivo.conteudo),
        conteudo=arquivo.conteudo,
    )


def _evento(s: Session, proposta: PropostaAdesao, tipo: str, descricao: str, autor: Usuario | None = None, **dados):
    eventos.registrar(
        s, autor=autor, tipo=tipo, entidade='proposta', entidade_id=proposta.id, descricao=descricao, dados=dados
    )


def _transicionar(s, proposta: PropostaAdesao, acao: str, quem: QuemAdesao, descricao: str, autor=None, **dados):
    origem = S(proposta.situacao)
    t = adesao.transicao(acao, origem, quem)
    proposta.situacao = t.destino.value
    _evento(
        s, proposta, acao, descricao, autor, de=origem.value, para=t.destino.value, referencia=t.referencia, **dados
    )


def _email_assinatura(s: Session, proposta: PropostaAdesao, sig: SignatarioProposta):
    if sig.papel == 'candidato':
        quem = f'por {proposta.corretor_nome}, corretor, ' if proposta.corretor_nome else ''
        corpo = (
            f'Sua proposta de adesão à Câmara do Comércio de Café foi preenchida {quem}e está pronta para você assinar. '
            'Depois das 3 assinaturas (você e os 2 proponentes), ela segue para o comitê de admissão.'
        )
    else:
        corpo = (
            f'{proposta.nome} indicou você como proponente na proposta de adesão à Câmara do Comércio de Café, '
            'com a sua carta de recomendação anexada. Confira e assine, ou recuse se não reconhecer a indicação.'
        )
    emails.enviar(
        s, para_nome=sig.nome, para_email=sig.email, proposta_id=proposta.id,
        assunto=f'{proposta.numero}: assine a proposta de adesão de {proposta.nome}', corpo=corpo,
        link=f'/adesao/assinar/{sig.token}', rotulo_link='Abrir a proposta e assinar',
    )  # fmt: skip


def enviar_proposta(s: Session, dados: DadosProposta) -> PropostaAdesao:
    documento = so_digitos(dados.documento)
    if erros := _validar(dados):
        raise ErroDeNegocio(' '.join(erros))
    if _membro_ativo_por_documento(s, documento):
        raise DocumentoDeMembroAtivo

    pj = len(documento) == 14
    proposta = PropostaAdesao(
        situacao=S.AGUARDANDO_ASSINATURAS.value,
        corretor_nome=(dados.corretor_nome or '').strip() or None,
        corretor_email=(dados.corretor_email or '').strip().lower() or None,
        tipo_pessoa=TipoPessoa.PJ if pj else TipoPessoa.PF,
        documento=documento,
        nome=dados.nome.strip(),
        atuacao=dados.atuacao,
        email=dados.email.strip().lower(),
        telefone=so_digitos(dados.telefone),
        propriedade=(dados.propriedade or '').strip() or None,
        cidade=dados.cidade.strip(),
        uf=dados.uf.strip().upper(),
        sacas_safra=dados.sacas_safra,
        representante_nome=dados.representante_nome.strip() if pj else None,
        representante_cpf=so_digitos(dados.representante_cpf or '') if pj else None,
        assinaturas_vencem_em=_agora() + timedelta(days=config().validade_links_adesao_dias),
    )
    candidato = SignatarioProposta(
        papel='candidato',
        nome=dados.representante_nome.strip() if pj else dados.nome.strip(),
        email=proposta.email,
        telefone=proposta.telefone,
        token=_token(),
    )
    proposta.signatarios.append(candidato)
    for i, p in enumerate(dados.proponentes, start=1):
        sig = SignatarioProposta(
            papel=f'proponente_{i}',
            nome=p.nome.strip(),
            email=p.email.strip().lower(),
            telefone=so_digitos(p.telefone),
            token=_token(),
            membro=_membro_por_email(s, p.email),
        )
        proposta.signatarios.append(sig)
        proposta.anexos.append(_anexo(p.carta, 'carta', sig))
    for arquivo in dados.documentos:
        proposta.anexos.append(_anexo(arquivo, 'documento'))

    s.add(proposta)
    s.flush()
    proposta.numero = f'PROP-{date.today().year}-{proposta.id:04d}'
    por = f', preenchida por {proposta.corretor_nome} (corretor)' if proposta.corretor_nome else ''
    _evento(s, proposta, 'proposta_enviada', f'Proposta enviada{por}, com as 2 cartas anexadas')
    for sig in proposta.signatarios:
        _email_assinatura(s, proposta, sig)
    return proposta


def _por_token(s: Session, token: str) -> SignatarioProposta:
    sig = s.scalar(
        select(SignatarioProposta)
        .options(selectinload(SignatarioProposta.proposta).selectinload(PropostaAdesao.signatarios))
        .where(SignatarioProposta.token == token)
    )
    if sig is None:
        raise NaoEncontrado
    return sig


def abrir_para_assinar(s: Session, token: str) -> SignatarioProposta:
    sig = _por_token(s, token)
    _ = sig.proposta.anexos
    return sig


def _aberta_para_assinar(sig: SignatarioProposta):
    proposta = sig.proposta
    if proposta.situacao != S.AGUARDANDO_ASSINATURAS:
        raise ErroDeNegocio('Esta proposta não está mais recebendo assinaturas.')
    if proposta.assinaturas_vencem_em <= _agora():
        raise ErroDeNegocio('O prazo para assinar esta proposta terminou.')
    if sig.assinado_em or sig.recusado_em:
        raise ErroDeNegocio('Você já respondeu a esta proposta.')


def assinar(s: Session, token: str) -> PropostaAdesao:
    sig = _por_token(s, token)
    _aberta_para_assinar(sig)
    proposta = sig.proposta
    sig.assinado_em = _agora()
    _evento(
        s, proposta, 'assinatura_proposta', f'{sig.nome} assinou como {adesao.PAPEIS[sig.papel].lower()} (simulado)'
    )
    if all(x.assinado_em for x in proposta.signatarios):
        _transicionar(s, proposta, 'completar_assinaturas', QuemAdesao.SISTEMA,
                      'As 3 assinaturas estão reunidas: proposta na fila do comitê')  # fmt: skip
        emails.enviar(
            s, para_nome=proposta.nome, para_email=proposta.email, proposta_id=proposta.id,
            assunto=f'{proposta.numero}: proposta na fila do comitê de admissão',
            corpo='As 3 assinaturas foram reunidas. O comitê de admissão se reúne uma vez por semana; '
            'você recebe outro e-mail com a decisão.',
        )  # fmt: skip
    return proposta


def recusar_assinatura(s: Session, token: str) -> PropostaAdesao:
    sig = _por_token(s, token)
    _aberta_para_assinar(sig)
    proposta = sig.proposta
    sig.recusado_em = _agora()
    _transicionar(s, proposta, 'recusar_assinatura', QuemAdesao.SIGNATARIO,
                  f'{sig.nome} recusou assinar como {adesao.PAPEIS[sig.papel].lower()}')  # fmt: skip
    emails.enviar(
        s, para_nome=proposta.nome, para_email=proposta.email, proposta_id=proposta.id,
        assunto=f'{proposta.numero}: a proposta não seguiu',
        corpo=f'{sig.nome} preferiu não assinar a sua proposta. Ela não segue para o comitê. '
        'Você pode fazer uma nova proposta quando quiser, com outros proponentes.',
        link='/adesao', rotulo_link='Fazer nova proposta',
    )  # fmt: skip
    return proposta


def expirar_vencidas(s: Session, agora: datetime | None = None) -> int:
    agora = agora or _agora()
    vencidas = s.scalars(
        select(PropostaAdesao).where(
            PropostaAdesao.situacao == S.AGUARDANDO_ASSINATURAS, PropostaAdesao.assinaturas_vencem_em <= agora
        )
    ).all()
    for proposta in vencidas:
        _transicionar(s, proposta, 'expirar', QuemAdesao.SISTEMA, 'O prazo de assinatura terminou sem as 3 assinaturas')
    return len(vencidas)


# Backoffice (telas 12, 12b, 12c e 13)


def listar(s: Session, operador: Usuario) -> list[PropostaAdesao]:
    exigir_papel(operador, Papel.OPERADOR)
    return list(
        s.scalars(
            select(PropostaAdesao)
            .options(
                selectinload(PropostaAdesao.signatarios).selectinload(SignatarioProposta.membro),
                selectinload(PropostaAdesao.decidido_por),
            )
            .order_by(PropostaAdesao.id.desc())
        )
    )


def obter(s: Session, operador: Usuario, proposta_id: int) -> PropostaAdesao:
    exigir_papel(operador, Papel.OPERADOR)
    proposta = s.scalar(
        select(PropostaAdesao)
        .options(
            selectinload(PropostaAdesao.signatarios).selectinload(SignatarioProposta.membro),
            selectinload(PropostaAdesao.anexos),
        )
        .where(PropostaAdesao.id == proposta_id)
    )
    if proposta is None:
        raise NaoEncontrado
    _ = proposta.decidido_por, proposta.membro
    return proposta


def conferencias(s: Session, proposta: PropostaAdesao) -> list[tuple[bool, str]]:
    """Checklist automático de apoio ao comitê (RN-13 a RN-17). Consulta à Receita fica fora do MVP."""
    doc = 'CNPJ' if proposta.tipo_pessoa == TipoPessoa.PJ else 'CPF'
    valido = (
        cnpj_valido(proposta.documento) if proposta.tipo_pessoa == TipoPessoa.PJ else cpf_valido(proposta.documento)
    )
    duplicado = _membro_ativo_por_documento(s, proposta.documento)
    anteriores = s.scalars(
        select(PropostaAdesao.numero).where(
            PropostaAdesao.documento == proposta.documento, PropostaAdesao.id != proposta.id
        )
    ).all()
    externos = [p.nome for p in proposta.proponentes() if p.membro_id is None]
    itens = [
        (valido, f'{doc} {formatar_documento(proposta.documento)} com formato válido. Consulta à Receita fora do MVP'),
        (duplicado is None, 'Nenhum membro ativo com este documento' if duplicado is None
         else f'Já existe membro ativo com este documento: {duplicado.nome}'),
        (all(sig.assinado_em for sig in proposta.signatarios),
         'As 3 assinaturas reunidas' if all(sig.assinado_em for sig in proposta.signatarios)
         else 'Faltam assinaturas'),
        (not externos, 'Os 2 proponentes são membros da Câmara' if not externos
         else f'Proponente de fora da Câmara: {", ".join(externos)}. Ponto de atenção para o comitê'),
    ]  # fmt: skip
    if anteriores:
        itens.append(
            (True, f'Propostas anteriores com o mesmo documento: {", ".join(anteriores)} (sem bloqueio, RN-110)')
        )
    return itens


def pedir_diligencia(s: Session, operador: Usuario, proposta_id: int, pedido: str) -> PropostaAdesao:
    if not (pedido or '').strip():
        raise ErroDeNegocio('Descreva o que o candidato precisa esclarecer ou enviar.')
    proposta = obter(s, operador, proposta_id)
    proposta.diligencia_pedido = pedido.strip()
    proposta.diligencia_resposta = None
    proposta.diligencia_token = _token()
    _transicionar(s, proposta, 'pedir_diligencia', QuemAdesao.BACKOFFICE,
                  f'{operador.nome} pediu diligência: {pedido.strip()}', operador)  # fmt: skip
    emails.enviar(
        s, para_nome=proposta.nome, para_email=proposta.email, proposta_id=proposta.id,
        assunto=f'{proposta.numero}: o comitê pediu mais informações',
        corpo=f'Antes de decidir, o comitê de admissão precisa do seguinte: {pedido.strip()}',
        link=f'/adesao/diligencia/{proposta.diligencia_token}', rotulo_link='Responder ao comitê',
    )  # fmt: skip
    return proposta


def abrir_diligencia(s: Session, token: str) -> PropostaAdesao:
    proposta = s.scalar(select(PropostaAdesao).where(PropostaAdesao.diligencia_token == token))
    if proposta is None:
        raise NaoEncontrado
    return proposta


def responder_diligencia(s: Session, token: str, resposta: str, arquivos: list[Arquivo]) -> PropostaAdesao:
    proposta = abrir_diligencia(s, token)
    if proposta.situacao != S.EM_DILIGENCIA:
        raise ErroDeNegocio('Este pedido já foi respondido.')
    if not (resposta or '').strip() and not arquivos:
        raise ErroDeNegocio('Escreva uma resposta ou anexe um documento.')
    erros = [e for a in arquivos for e in _validar_arquivo(a, a.nome)]
    if erros:
        raise ErroDeNegocio(' '.join(erros))
    proposta.diligencia_resposta = (resposta or '').strip() or None
    for arquivo in arquivos:
        proposta.anexos.append(_anexo(arquivo, 'diligencia'))
    _transicionar(s, proposta, 'responder_diligencia', QuemAdesao.CANDIDATO,
                  f'{proposta.nome} respondeu à diligência; proposta de volta à fila do comitê')  # fmt: skip
    return proposta


def registrar_decisao(s: Session, operador: Usuario, proposta_id: int, dados: DadosDecisao) -> PropostaAdesao:
    """Materializa a decisão já tomada pelo comitê na reunião (RN-106, RN-109): a referência da reunião é obrigatória."""
    proposta = obter(s, operador, proposta_id)
    if dados.reuniao_data is None:
        raise ErroDeNegocio('Informe a data da reunião do comitê em que a decisão foi tomada.')
    if dados.decisao not in ('aprovar', 'recusar'):
        raise ErroDeNegocio('Escolha aprovar ou recusar.')
    if dados.decisao == 'recusar' and not dados.motivo_recusa.strip():
        raise ErroDeNegocio('Recusar exige o motivo (RN-24).')
    if dados.decisao == 'aprovar' and _membro_ativo_por_documento(s, proposta.documento):
        raise ErroDeNegocio('Já existe membro ativo com este documento.')

    proposta.reuniao_data = dados.reuniao_data
    proposta.reuniao_presentes = dados.reuniao_presentes.strip() or None
    proposta.parecer = dados.parecer.strip() or None
    proposta.decidido_por_id = operador.id
    proposta.decidido_em = _agora()
    reuniao = f'reunião de {dados.reuniao_data:%d/%m/%Y}'

    if dados.decisao == 'recusar':
        proposta.motivo_recusa = dados.motivo_recusa.strip()
        _transicionar(s, proposta, 'recusar', QuemAdesao.BACKOFFICE,
                      f'Recusada pelo comitê na {reuniao}, lançado por {operador.nome}. Motivo: {proposta.motivo_recusa}',
                      operador)  # fmt: skip
        # O candidato recebe aviso curto; o motivo e o parecer ficam internos (RN-30)
        emails.enviar(
            s, para_nome=proposta.nome, para_email=proposta.email, proposta_id=proposta.id,
            assunto=f'{proposta.numero}: resultado da proposta de adesão',
            corpo='O comitê de admissão avaliou a sua proposta, e ela não foi aceita desta vez. '
            'Você pode propor de novo quando quiser.',
        )  # fmt: skip
        return proposta

    membro = _criar_membro(s, proposta)
    proposta.membro = membro
    _transicionar(s, proposta, 'aprovar', QuemAdesao.BACKOFFICE,
                  f'Aprovada pelo comitê na {reuniao}, lançado por {operador.nome}. Conta de membro criada',
                  operador)  # fmt: skip
    emails.enviar(
        s, para_nome=proposta.nome, para_email=proposta.email, proposta_id=proposta.id,
        assunto=f'{proposta.numero}: bem-vindo à Câmara do Comércio de Café',
        corpo='Sua proposta foi aprovada pelo comitê de admissão. Crie a sua senha pelo link abaixo. '
        'No primeiro acesso, você assina os termos da Câmara; depois disso, já pode registrar contratos.',
        link=f'/acesso/{membro.usuario.convite_token}', rotulo_link='Criar minha senha',
    )  # fmt: skip
    return proposta


def _criar_membro(s: Session, proposta: PropostaAdesao) -> Membro:
    """RN-32: a conta nasce sem senha e sem sessão; o aprovado define a senha pelo link."""
    candidato = proposta.candidato()
    if s.scalar(select(Usuario).where(Usuario.email == proposta.email)):
        raise ErroDeNegocio('Já existe um usuário com o e-mail do candidato. Ajuste o cadastro antes de aprovar.')
    usuario = Usuario(
        email=proposta.email,
        nome=candidato.nome,
        senha_hash=None,
        papel=Papel.MEMBRO,
        convite_token=_token(),
        convite_expira_em=_agora() + timedelta(days=config().validade_links_adesao_dias),
    )
    membro = Membro(
        usuario=usuario,
        tipo_pessoa=proposta.tipo_pessoa,
        documento=proposta.documento,
        nome=proposta.nome,
        cidade=proposta.cidade,
        uf=proposta.uf,
        propriedade=proposta.propriedade,
        representante_nome=proposta.representante_nome,
        representante_cpf=proposta.representante_cpf,
        representante_cargo='Representante' if proposta.tipo_pessoa == TipoPessoa.PJ else None,
        corretor=proposta.atuacao == Atuacao.CORRETOR,
    )
    s.add(membro)
    s.flush()
    eventos.registrar(
        s, autor=None, tipo='membro_criado', entidade='membro', entidade_id=membro.id,
        descricao=f'Membro criado pela aprovação da proposta {proposta.numero}',
    )  # fmt: skip
    return membro


# Primeiro acesso do aprovado


def abrir_convite(s: Session, token: str) -> Usuario:
    usuario = s.scalar(select(Usuario).where(Usuario.convite_token == token))
    if usuario is None:
        raise NaoEncontrado
    if usuario.convite_expira_em and usuario.convite_expira_em <= _agora():
        raise ErroDeNegocio('Este link expirou. Peça um novo ao backoffice.')
    return usuario


def criar_senha(s: Session, token: str, senha: str, confirmacao: str) -> Usuario:
    from app.services.auth import gerar_hash

    usuario = abrir_convite(s, token)
    if len(senha or '') < 8:
        raise ErroDeNegocio('A senha precisa ter pelo menos 8 caracteres.')
    if senha != confirmacao:
        raise ErroDeNegocio('As duas senhas não conferem.')
    usuario.senha_hash = gerar_hash(senha)
    usuario.convite_token = None
    usuario.convite_expira_em = None
    eventos.registrar(
        s, autor=usuario, tipo='senha_criada', entidade='usuario', entidade_id=usuario.id, descricao='Senha criada'
    )
    return usuario


def precisa_assinar_termos(s: Session, usuario: Usuario) -> bool:
    if usuario.papel != Papel.MEMBRO:
        return False
    membro = s.scalar(select(Membro).where(Membro.usuario_id == usuario.id))
    return membro is not None and membro.termos_aceitos_em is None


def assinar_termos(s: Session, usuario: Usuario) -> Membro:
    exigir_papel(usuario, Papel.MEMBRO)
    membro = s.scalar(select(Membro).where(Membro.usuario_id == usuario.id))
    if membro is None:
        raise NaoEncontrado
    if membro.termos_aceitos_em is None:
        membro.termos_aceitos_em = _agora()
        membro.termos_versao = VERSAO_TERMOS
        eventos.registrar(
            s, autor=usuario, tipo='termos_assinados', entidade='membro', entidade_id=membro.id,
            descricao=f'{usuario.nome} assinou os termos da Câmara, versão {VERSAO_TERMOS} (assinatura simulada)',
        )  # fmt: skip
    return membro


# Anexos: o backoffice vê todos; cada signatário vê os da proposta que recebeu


def anexo_para_backoffice(s: Session, operador: Usuario, anexo_id: int) -> AnexoProposta:
    exigir_papel(operador, Papel.OPERADOR)
    anexo = s.scalar(select(AnexoProposta).options(undefer(AnexoProposta.conteudo)).where(AnexoProposta.id == anexo_id))
    if anexo is None:
        raise NaoEncontrado
    return anexo


def anexo_para_signatario(s: Session, token: str, anexo_id: int) -> AnexoProposta:
    sig = _por_token(s, token)
    anexo = s.scalar(select(AnexoProposta).options(undefer(AnexoProposta.conteudo)).where(AnexoProposta.id == anexo_id))
    if anexo is None or anexo.proposta_id != sig.proposta_id or anexo.tipo == 'diligencia':
        raise NaoEncontrado
    return anexo
