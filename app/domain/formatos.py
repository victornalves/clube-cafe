"""Validação e formatação de CPF, CNPJ e valores. Validar formato nunca aprova mérito (RN-06)."""

import re
from decimal import Decimal


def so_digitos(texto: str) -> str:
    return re.sub(r'\D', '', texto or '')


def _digito(numeros: str, pesos: list[int]) -> str:
    resto = sum(int(n) * p for n, p in zip(numeros, pesos, strict=True)) % 11
    return '0' if resto < 2 else str(11 - resto)


def cpf_valido(cpf: str) -> bool:
    cpf = so_digitos(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    d1 = _digito(cpf[:9], list(range(10, 1, -1)))
    d2 = _digito(cpf[:9] + d1, list(range(11, 1, -1)))
    return cpf[9:] == d1 + d2


def cnpj_valido(cnpj: str) -> bool:
    cnpj = so_digitos(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = _digito(cnpj[:12], pesos)
    d2 = _digito(cnpj[:12] + d1, [6, *pesos])
    return cnpj[12:] == d1 + d2


def formatar_documento(documento: str) -> str:
    d = so_digitos(documento)
    if len(d) == 11:
        return f'{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}'
    if len(d) == 14:
        return f'{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}'
    return documento


def formatar_inteiro(n: int) -> str:
    return f'{n:,}'.replace(',', '.')


def formatar_reais(valor: Decimal) -> str:
    """Sem o prefixo R$, para o chamador decidir onde ele vai."""
    inteiro, centavos = f'{valor:.2f}'.split('.')
    return f'{formatar_inteiro(int(inteiro))},{centavos}'


def email_valido(email: str) -> bool:
    return re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email or '') is not None
