from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.adesao import SituacaoProposta as S
from app.domain.models import Atuacao, EmailSimulado, Papel
from app.services import adesao, auth, emails
from app.services.adesao import Arquivo, DadosDecisao, DadosProponente, DadosProposta, DocumentoDeMembroAtivo
from app.services.erros import AcessoNegado, ErroDeNegocio, NaoEncontrado
from tests import fabricas

PDF = Arquivo('carta.pdf', 'application/pdf', b'%PDF-1.4 carta')


def dados(**kwargs) -> DadosProposta:
    base = dict(
        nome='Sebastião Ferraz de Almeida',
        documento='529.982.247-25',
        atuacao=Atuacao.PRODUTOR,
        email='sebastiao@teste.com',
        telefone='(35) 99999-0000',
        cidade='Varginha',
        uf='MG',
        propriedade='Fazenda Boa Esperança',
        sacas_safra=4500,
        proponentes=[
            DadosProponente('Helena Prado', 'helena@teste.com', '(35) 98888-0000', PDF),
            DadosProponente('Raimundo Castilho', 'raimundo@teste.com', '(35) 97777-0000', PDF),
        ],
    )
    return DadosProposta(**{**base, **kwargs})


@pytest.fixture
def operador(s):
    return fabricas.usuario(s, papel=Papel.OPERADOR)


def assinada(s, **kwargs):
    p = adesao.enviar_proposta(s, dados(**kwargs))
    for sig in p.signatarios:
        adesao.assinar(s, sig.token)
    return p


def aprovar(s, operador, p):
    return adesao.registrar_decisao(s, operador, p.id, DadosDecisao('aprovar', date(2026, 11, 5)))


def test_envio_cria_proposta_com_3_signatarios_e_emails(s):
    p = adesao.enviar_proposta(s, dados())
    assert p.situacao == S.AGUARDANDO_ASSINATURAS
    assert p.numero.startswith('PROP-')
    assert [x.papel for x in p.signatarios] == ['candidato', 'proponente_1', 'proponente_2']
    assert len([a for a in p.anexos if a.tipo == 'carta']) == 2
    links = [e.link for e in emails.da_proposta(s, p.id)]
    assert links == [f'/adesao/assinar/{x.token}' for x in p.signatarios]


@pytest.mark.parametrize(
    ('mudanca', 'mensagem'),
    [
        (dict(documento='111.111.111-11'), 'CPF ou CNPJ inválido'),
        (dict(email='sem-arroba'), 'E-mail do candidato'),
        (dict(telefone='123'), 'Telefone do candidato'),
        (dict(proponentes=[DadosProponente('Helena', 'helena@teste.com', '35988880000', PDF)]), 'exatamente 2'),
        (
            dict(
                proponentes=[
                    DadosProponente('Helena', 'sebastiao@teste.com', '35988880000', PDF),
                    DadosProponente('Raimundo', 'raimundo@teste.com', '35977770000', PDF),
                ]
            ),
            'repete',
        ),
        (
            dict(
                proponentes=[
                    DadosProponente('Helena', 'helena@teste.com', '35988880000', None),
                    DadosProponente('Raimundo', 'raimundo@teste.com', '35977770000', PDF),
                ]
            ),
            'anexe a carta',
        ),
        (dict(documentos=[Arquivo('x.exe', 'application/octet-stream', b'x')]), 'PDF, JPG ou PNG'),
        (dict(documento='09.455.218/0001-05'), 'quem assina pela empresa'),
    ],
)
def test_validacao_de_formato(s, mudanca, mensagem):
    with pytest.raises(ErroDeNegocio, match=mensagem):
        adesao.enviar_proposta(s, dados(**mudanca))


def test_documento_de_membro_ativo_vai_para_o_login(s):
    membro = fabricas.membro(s)
    with pytest.raises(DocumentoDeMembroAtivo):
        adesao.enviar_proposta(s, dados(documento=membro.documento))


def test_mesmo_documento_pode_repetir_entre_propostas(s):
    adesao.enviar_proposta(s, dados())
    adesao.enviar_proposta(s, dados())  # RN-112


def test_proponente_membro_e_reconhecido(s):
    helena = fabricas.membro(s)
    p = adesao.enviar_proposta(
        s,
        dados(
            proponentes=[
                DadosProponente('Helena', helena.usuario.email, '35988880000', PDF),
                DadosProponente('Raimundo', 'raimundo@teste.com', '35977770000', PDF),
            ]
        ),
    )
    assert [x.membro_id for x in p.proponentes()] == [helena.id, None]


def test_tres_assinaturas_levam_a_fila_do_comite(s):
    p = adesao.enviar_proposta(s, dados())
    for sig in p.signatarios[:2]:
        adesao.assinar(s, sig.token)
        assert p.situacao == S.AGUARDANDO_ASSINATURAS
    with pytest.raises(ErroDeNegocio, match='já respondeu'):
        adesao.assinar(s, p.signatarios[0].token)
    adesao.assinar(s, p.signatarios[2].token)
    assert p.situacao == S.EM_FILA_COMITE


def test_proponente_que_recusa_encerra_a_proposta(s):
    p = adesao.enviar_proposta(s, dados())
    adesao.recusar_assinatura(s, p.signatarios[2].token)
    assert p.situacao == S.ASSINATURA_RECUSADA
    with pytest.raises(ErroDeNegocio, match='não está mais'):
        adesao.assinar(s, p.signatarios[0].token)


def test_link_vencido_expira_a_proposta(s):
    p = adesao.enviar_proposta(s, dados())
    with pytest.raises(ErroDeNegocio, match='prazo'):
        p.assinaturas_vencem_em = datetime.now(UTC) - timedelta(seconds=1)
        adesao.assinar(s, p.signatarios[0].token)
    assert adesao.expirar_vencidas(s) >= 1
    assert p.situacao == S.EXPIRADA


def test_token_desconhecido(s):
    with pytest.raises(NaoEncontrado):
        adesao.assinar(s, 'nao-existe')


def test_diligencia_vai_e_volta(s, operador):
    p = assinada(s)
    adesao.pedir_diligencia(s, operador, p.id, 'Comprovante de propriedade atualizado')
    assert p.situacao == S.EM_DILIGENCIA
    with pytest.raises(ErroDeNegocio, match='resposta'):
        adesao.responder_diligencia(s, p.diligencia_token, '', [])
    adesao.responder_diligencia(s, p.diligencia_token, 'Segue o comprovante', [PDF])
    assert p.situacao == S.EM_FILA_COMITE
    assert any(a.tipo == 'diligencia' for a in p.anexos)


def test_decisao_exige_reuniao_e_motivo_para_recusar(s, operador):
    p = assinada(s)
    with pytest.raises(ErroDeNegocio, match='data da reunião'):
        adesao.registrar_decisao(s, operador, p.id, DadosDecisao('aprovar', None))
    with pytest.raises(ErroDeNegocio, match='motivo'):
        adesao.registrar_decisao(s, operador, p.id, DadosDecisao('recusar', date(2026, 11, 5)))
    adesao.registrar_decisao(
        s, operador, p.id, DadosDecisao('recusar', date(2026, 11, 5), motivo_recusa='Fora do perfil')
    )
    assert p.situacao == S.RECUSADA
    # O candidato recebe aviso curto, sem o motivo (RN-30)
    assert 'Fora do perfil' not in emails.da_proposta(s, p.id)[-1].corpo


def test_so_decide_proposta_na_fila(s, operador):
    p = adesao.enviar_proposta(s, dados())
    with pytest.raises(Exception, match='não é permitido'):
        aprovar(s, operador, p)


def test_aprovacao_cria_membro_sem_senha_e_o_primeiro_acesso_completa(s, operador):
    p = assinada(s)
    aprovar(s, operador, p)
    assert p.situacao == S.APROVADA
    usuario = p.membro.usuario
    assert usuario.senha_hash is None
    assert auth.autenticar(s, usuario.email, 'qualquer') is None  # sem senha, sem sessão (RN-32)
    assert p.membro.termos_aceitos_em is None  # ainda não pode ser parte de registro

    token = usuario.convite_token
    assert emails.da_proposta(s, p.id)[-1].link == f'/acesso/{token}'
    with pytest.raises(ErroDeNegocio, match='conferem'):
        adesao.criar_senha(s, token, 'senha-forte-1', 'outra-senha')
    adesao.criar_senha(s, token, 'senha-forte-1', 'senha-forte-1')
    assert auth.autenticar(s, usuario.email, 'senha-forte-1') == usuario
    assert usuario.convite_token is None

    assert adesao.precisa_assinar_termos(s, usuario)
    adesao.assinar_termos(s, usuario)
    assert not adesao.precisa_assinar_termos(s, usuario)


def test_backoffice_so_para_operador(s):
    p = assinada(s)
    membro = fabricas.membro(s).usuario
    for chamada in (
        lambda: adesao.listar(s, membro),
        lambda: adesao.obter(s, membro, p.id),
        lambda: adesao.pedir_diligencia(s, membro, p.id, 'x'),
        lambda: aprovar(s, membro, p),
        lambda: adesao.anexo_para_backoffice(s, membro, p.anexos[0].id),
    ):
        with pytest.raises(AcessoNegado):
            chamada()


def test_signatario_ve_so_anexos_da_propria_proposta(s):
    p1 = adesao.enviar_proposta(s, dados())
    p2 = adesao.enviar_proposta(s, dados(email='outro@teste.com'))
    token = p1.signatarios[1].token
    assert adesao.anexo_para_signatario(s, token, p1.anexos[0].id).conteudo.startswith(b'%PDF')
    with pytest.raises(NaoEncontrado):
        adesao.anexo_para_signatario(s, token, p2.anexos[0].id)


def test_caixa_de_emails_so_com_login_demo(s, monkeypatch):
    from app.config import config

    adesao.enviar_proposta(s, dados())
    monkeypatch.setattr(config(), 'login_demo', True)
    assert isinstance(emails.caixa(s)[0], EmailSimulado)
    monkeypatch.setattr(config(), 'login_demo', False)
    with pytest.raises(AcessoNegado):
        emails.caixa(s)
