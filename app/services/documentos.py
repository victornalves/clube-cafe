import hashlib
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session, undefer
from weasyprint import HTML

from app.domain.catalogos import MESES, PRODUTOS
from app.domain.formatos import formatar_documento, formatar_inteiro, formatar_reais
from app.domain.models import Documento, Envelope, Membro, Registro, TipoDocumento, TipoPessoa, Usuario
from app.domain.prevalidacao import vencimento
from app.services import registros
from app.services.erros import NaoEncontrado

_jinja = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / 'templates'),
    autoescape=select_autoescape(['html']),
)


def _parte(m: Membro | None) -> dict | None:
    if m is None:
        return None
    pj = m.tipo_pessoa == TipoPessoa.PJ
    return {
        'nome': m.nome,
        'pj': pj,
        'rotulo_documento': 'CNPJ' if pj else 'CPF',
        'documento_formatado': formatar_documento(m.documento),
        'cidade': m.cidade,
        'uf': m.uf,
        'email': m.usuario.email,
        'numero_cliente': m.id,
        'representante': f'{m.representante_nome}, {(m.representante_cargo or "").lower()}' if pj else None,
        'propriedade': m.propriedade,
        'matricula': m.matricula_imovel,
    }


def contexto(registro: Registro, emissao: date) -> dict:
    return {
        'registro': {
            'numero': registro.numero,
            'produto': PRODUTOS[registro.produto],
            'sacas_formatado': formatar_inteiro(registro.sacas),
            'peso_formatado': formatar_inteiro(registro.peso_kg),
            'preco_formatado': formatar_reais(registro.preco_saca),
            'valor_total_formatado': formatar_reais(registro.valor_total),
            'regiao': registro.regiao,
            'armazem': registro.armazem,
            'mes_entrega': f'{MESES[registro.entrega_mes - 1]} de {registro.entrega_ano}',
            'vencimento': vencimento(registro).strftime('%d/%m/%Y'),
            'pagamento_adiantado': registro.pagamento_adiantado,
            'emissao': emissao.strftime('%d/%m/%Y'),
            'emissao_extenso': f'{emissao.day} de {MESES[emissao.month - 1]} de {emissao.year}',
        },
        'vendedor': _parte(registro.vendedor),
        'comprador': _parte(registro.comprador),
        'corretor': _parte(registro.corretor),
    }


def gerar_pdf(tipo: TipoDocumento, registro: Registro, emissao: date) -> bytes:
    html = _jinja.get_template(f'{tipo.value}.html').render(contexto(registro, emissao))
    return HTML(string=html).write_pdf()


def gerar(registro: Registro, emissao: date) -> list[Documento]:
    documentos = []
    for tipo in (TipoDocumento.CONTRATO, TipoDocumento.CPR):
        pdf = gerar_pdf(tipo, registro, emissao)
        documentos.append(Documento(tipo=tipo, pdf=pdf, sha256=hashlib.sha256(pdf).hexdigest()))
    return documentos


def obter_pdf(s: Session, usuario: Usuario, documento_id: int) -> tuple[Documento, str]:
    """PDF com o nome do arquivo. Só para quem enxerga o registro (mesmo isolamento do registro)."""
    documento = s.scalar(select(Documento).options(undefer(Documento.pdf)).where(Documento.id == documento_id))
    if documento is None:
        raise NaoEncontrado
    envelope = s.get(Envelope, documento.envelope_id)
    registro = registros.obter(s, usuario, envelope.registro_id)
    nome = 'Contrato' if documento.tipo == TipoDocumento.CONTRATO else 'CPR'
    return documento, f'{nome} {registro.numero} v{envelope.versao}.pdf'
