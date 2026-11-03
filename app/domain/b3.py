"""O que vai para a B3 e como ler o que volta. Nomes de campo do Layout CPR 2.0 (estudo-api-b3.md §2).

O nome JSON real só vem com o pacote de acesso; até lá, o payload usa os nomes do layout em snake_case.
"""

from dataclasses import dataclass
from datetime import date

from app.domain.models import Registro
from app.domain.prevalidacao import UNIDADE_SACA, vencimento

# Erros em que a B3 pode ter registrado mesmo assim: consulta antes de reenviar (T-05, T-06)
TRANSITORIOS = {408, 429, 500, 502, 503, 504}


@dataclass
class RespostaB3:
    status: int
    corpo: dict

    @property
    def sucesso(self) -> bool:
        return 200 <= self.status < 300

    @property
    def transitorio(self) -> bool:
        return self.status in TRANSITORIOS

    @property
    def mensagem(self) -> str:
        return self.corpo.get('mensagem') or self.corpo.get('message') or ''


def chave(registro: Registro) -> str:
    """Chave de consulta. Na B3 real, a chave de unicidade inclui emissão, emitente e credor."""
    return registro.numero


def payload(registro: Registro, emissao: date) -> dict:
    return {
        'tipo_cpr': 'P',
        'codigo_contrato': registro.numero,
        'data_emissao': emissao.strftime('%Y%m%d'),
        'data_vencimento': vencimento(registro).strftime('%Y%m%d'),
        'emitente': {
            'nome': registro.vendedor.nome,
            'cpf_cnpj': registro.vendedor.documento,
            'natureza': registro.vendedor.tipo_pessoa.value,
            'uf': registro.vendedor.uf,
            'municipio': registro.vendedor.cidade,
        },
        'credor_original': {
            'nome': registro.comprador.nome,
            'cpf_cnpj': registro.comprador.documento,
        },
        'produto': {
            'codigo_produto': registro.produto,
            'quantidade': registro.sacas,
            'unidade_medida': UNIDADE_SACA,
            'imovel': registro.vendedor.propriedade,
            'local_entrega': registro.armazem,
        },
        'valor_emissao': str(registro.preco_saca),
        'valor_financeiro_emissao': str(registro.valor_total),
        'tipo_garantia': 7,  # alienação fiduciária
        'emissao_eletronica': 'S',
    }
