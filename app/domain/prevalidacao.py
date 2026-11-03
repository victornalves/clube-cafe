"""Pré-validação antes do envelope (T-08): pega localmente o que daria 422 na B3, sem chamar a B3.

Tamanhos e formatos do Layout CPR 2.0 (estudo-api-b3.md §2). Os domínios fechados vêm da tabela provisória
`dominio_b3`. A CPR do clube também exige o imóvel de produção e a matrícula (Quadro, "Local onde será
desenvolvido o produto").
"""

import calendar
from datetime import date
from decimal import Decimal

from app.domain.formatos import cnpj_valido, cpf_valido
from app.domain.models import Membro, Registro, TipoPessoa

UNIDADE_SACA = 'SC60'
PRAZO_MAXIMO_DIAS = 999  # "Prazo do Documento", numérico 3


def vencimento(registro: Registro) -> date:
    """Último dia do mês de entrega: a entrega pode acontecer em qualquer dia do mês."""
    ultimo = calendar.monthrange(registro.entrega_ano, registro.entrega_mes)[1]
    return date(registro.entrega_ano, registro.entrega_mes, ultimo)


def _cabe(texto: str | None, limite: int) -> bool:
    return bool(texto) and len(texto) <= limite


def _parte(rotulo: str, m: Membro) -> list[str]:
    erros = []
    documento_ok = cpf_valido(m.documento) if m.tipo_pessoa == TipoPessoa.PF else cnpj_valido(m.documento)
    if not documento_ok:
        erros.append(f'{rotulo}: CPF/CNPJ inválido no cadastro.')
    if not _cabe(m.nome, 100):
        erros.append(f'{rotulo}: o nome passa de 100 caracteres, limite da B3.')
    if not _cabe(m.cidade, 50):
        erros.append(f'{rotulo}: o município passa de 50 caracteres, limite da B3.')
    return erros


def prevalidar(registro: Registro, dominios: set[tuple[str, str]], emissao: date) -> list[str]:
    """Lista de problemas; vazia quando o registro pode seguir para assinatura."""
    erros = []
    erros += _parte('Vendedor', registro.vendedor)
    erros += _parte('Comprador', registro.comprador)

    if not registro.vendedor.propriedade or not registro.vendedor.matricula_imovel:
        erros.append(
            'Vendedor: falta o imóvel de produção ou a matrícula no cadastro. A CPR exige os dois. '
            'Peça ao backoffice para completar.'
        )
    elif len(registro.vendedor.propriedade) > 35:
        erros.append('Vendedor: o nome do imóvel passa de 35 caracteres, limite da B3.')

    if ('produto', registro.produto) not in dominios:
        erros.append('Produto fora da lista de produtos aceitos pela B3.')
    if ('unidade', UNIDADE_SACA) not in dominios:
        erros.append('Unidade "saca de 60 kg" fora da lista de unidades aceitas pela B3.')

    if not registro.sacas or registro.sacas <= 0 or registro.sacas >= 10**10:
        erros.append('Quantidade de sacas fora do formato da B3 (inteiro, até 10 dígitos).')
    if not registro.preco_saca or registro.preco_saca <= 0 or registro.preco_saca >= Decimal(10**10):
        erros.append('Preço por saca fora do formato da B3 (até 10 dígitos inteiros).')
    elif registro.valor_total >= Decimal(10**16):
        erros.append('Valor total fora do formato da B3 (até 16 dígitos inteiros).')

    if not _cabe(registro.armazem, 35):
        erros.append('Local de entrega vazio ou com mais de 35 caracteres, limite da B3.')
    if not registro.entrega_mes or not registro.entrega_ano:
        erros.append('Falta o mês de entrega.')
    else:
        prazo = (vencimento(registro) - emissao).days
        if prazo <= 0:
            erros.append('A data de entrega precisa ser posterior à data de emissão.')
        elif prazo > PRAZO_MAXIMO_DIAS:
            erros.append(f'O prazo entre emissão e entrega passa de {PRAZO_MAXIMO_DIAS} dias, limite da B3.')
    return erros
