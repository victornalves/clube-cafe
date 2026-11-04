from datetime import UTC, date, datetime, timedelta

import pytest
from pypdf import PdfReader
from sqlalchemy import update

from app.domain.estados import Estado
from app.domain.models import DominioB3, PapelNoRegistro, SituacaoEnvelope, TipoDocumento
from app.services import documentos, envelopes, registros
from app.services.erros import ErroDeNegocio, NaoEncontrado
from tests.fabricas import ANO, gerar, rascunho


def test_prevalidacao_barra_e_volta_para_rascunho(s, partes):
    partes['vendedor'].matricula_imovel = None
    r = rascunho(s, partes)
    erros = gerar(s, partes, r)
    assert any('matrícula' in e for e in erros)
    assert r.estado == Estado.RASCUNHO
    assert r.envelopes == []
    assert r.enviado_as_partes_em is None


def test_prevalidacao_barra_produto_fora_do_dominio(s, partes):
    # A lista de domínios é dado: desativar o conilon na tabela basta para a B3 "recusar" o produto
    s.execute(update(DominioB3).where(DominioB3.codigo == 'conilon').values(ativo=False))
    r = rascunho(s, partes, produto='conilon')
    assert any('Produto' in e for e in gerar(s, partes, r))


def test_envelope_com_contrato_e_cpr_assinaveis(s, partes):
    r = rascunho(s, partes, corretor=True)
    assert gerar(s, partes, r) == []
    assert r.estado == Estado.AGUARDANDO_ASSINATURAS
    envelope = envelopes.atual(r)
    assert [d.tipo for d in envelope.documentos] == [TipoDocumento.CONTRATO, TipoDocumento.CPR]
    assert all(d.pdf.startswith(b'%PDF') and len(d.sha256) == 64 for d in envelope.documentos)
    papeis = {a.papel: a.documentos for a in envelope.assinaturas}
    assert papeis[PapelNoRegistro.CORRETOR] == [TipoDocumento.CONTRATO]
    assert papeis[PapelNoRegistro.VENDEDOR] == [TipoDocumento.CONTRATO, TipoDocumento.CPR]
    # A partir daqui as outras partes enxergam o registro
    assert registros.obter(s, partes['comprador'].usuario, r.id) == r


def test_cpr_sai_com_os_dados_do_registro(s, partes):
    r = rascunho(s, partes)
    pdf = documentos.gerar_pdf(TipoDocumento.CPR, r, date.today())
    texto = ''.join(p.extract_text() for p in PdfReader(__import__('io').BytesIO(pdf)).pages)
    assert r.numero in texto
    assert '2.000 sacas de 60 kg' in texto
    assert 'Fazenda Santa Luzia' in texto
    assert f'31/12/{ANO}' in texto


def test_todos_assinam_e_registro_fica_assinado(s, partes):
    r = rascunho(s, partes, corretor=True)
    gerar(s, partes, r)
    for quem in ('comprador', 'vendedor'):
        envelopes.assinar(s, partes[quem].usuario, r.id)
        assert r.estado == Estado.AGUARDANDO_ASSINATURAS
    with pytest.raises(ErroDeNegocio, match='pendente'):
        envelopes.assinar(s, partes['vendedor'].usuario, r.id)
    envelopes.assinar(s, partes['corretor'].usuario, r.id)
    assert r.estado == Estado.ASSINADO
    assert envelopes.atual(r).situacao == SituacaoEnvelope.CONCLUIDO


def test_estranho_nao_assina(s, partes):
    r = rascunho(s, partes)
    gerar(s, partes, r)
    with pytest.raises(NaoEncontrado):
        envelopes.assinar(s, partes['estranho'].usuario, r.id)


def test_janela_expira_e_autor_reabre_com_assinaturas_zeradas(s, partes):
    r = rascunho(s, partes)
    gerar(s, partes, r)
    envelopes.assinar(s, partes['comprador'].usuario, r.id)
    depois = datetime.now(UTC) + timedelta(hours=1)
    assert envelopes.expirar_vencidos(s, depois) >= 1
    assert r.estado == Estado.JANELA_EXPIRADA
    assert envelopes.expirar_vencidos(s, depois) == 0  # idempotente

    with pytest.raises(NaoEncontrado):
        envelopes.reabrir_janela(s, partes['comprador'].usuario, r.id)
    envelopes.reabrir_janela(s, partes['vendedor'].usuario, r.id)
    assert r.estado == Estado.AGUARDANDO_ASSINATURAS
    assert envelopes.atual(r).versao == 2
    assert len(envelopes.atual(r).pendentes()) == 2


def test_assinar_depois_do_prazo_e_recusado(s, partes):
    r = rascunho(s, partes)
    gerar(s, partes, r)
    envelopes.atual(r).expira_em = datetime.now(UTC) - timedelta(seconds=1)
    with pytest.raises(ErroDeNegocio, match='janela'):
        envelopes.assinar(s, partes['comprador'].usuario, r.id)


def test_autor_cancela_so_antes_da_primeira_assinatura(s, partes):
    r = rascunho(s, partes)
    gerar(s, partes, r)
    envelopes.assinar(s, partes['comprador'].usuario, r.id)
    with pytest.raises(ErroDeNegocio, match='backoffice'):
        envelopes.cancelar_envelope(s, partes['vendedor'].usuario, r.id)

    outro = rascunho(s, partes)
    gerar(s, partes, outro)
    envelopes.cancelar_envelope(s, partes['vendedor'].usuario, outro.id)
    assert outro.estado == Estado.CANCELADO


def test_linha_do_tempo_esconde_o_rascunho_da_outra_parte(s, partes):
    partes['vendedor'].matricula_imovel = None
    r = rascunho(s, partes)
    gerar(s, partes, r)  # falha na pré-validação
    partes['vendedor'].matricula_imovel = '14.882'
    gerar(s, partes, r)
    envelopes.assinar(s, partes['comprador'].usuario, r.id)

    do_autor = [e.tipo for e in envelopes.linha_do_tempo(s, partes['vendedor'].usuario, r.id)]
    da_outra_parte = [e.tipo for e in envelopes.linha_do_tempo(s, partes['comprador'].usuario, r.id)]
    assert do_autor == ['registro_criado', 'prevalidacao_falhou', 'prevalidacao_passou', 'assinatura']
    assert da_outra_parte == ['registro_criado', 'prevalidacao_passou', 'assinatura']
