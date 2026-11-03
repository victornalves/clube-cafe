"""Prazo legal: 30 dias úteis entre a emissão e o registro na B3 (art. 12 da Lei 8.929/1994, CPR cláusula 6.1).

Feriados nacionais e de Minas Gerais. Feriado municipal de Varginha fica de fora até alguém confirmar a regra
(o prazo é de quem registra, e a B3 fica em São Paulo).
"""

from datetime import date, timedelta
from functools import lru_cache

import holidays


@lru_cache
def _feriados(ano: int) -> holidays.HolidayBase:
    return holidays.Brazil(subdiv='MG', years=ano)


def dia_util(dia: date) -> bool:
    return dia.weekday() < 5 and dia not in _feriados(dia.year)


def somar_dias_uteis(inicio: date, dias: int) -> date:
    dia = inicio
    while dias > 0:
        dia += timedelta(days=1)
        if dia_util(dia):
            dias -= 1
    return dia


def dias_uteis_entre(inicio: date, fim: date) -> int:
    """Dias úteis depois de `inicio` até `fim`, inclusive. Negativo se `fim` já passou."""
    if fim < inicio:
        return -dias_uteis_entre(fim, inicio)
    return sum(1 for n in range(1, (fim - inicio).days + 1) if dia_util(inicio + timedelta(days=n)))


def limite_legal(emissao: date, prazo_dias_uteis: int) -> date:
    return somar_dias_uteis(emissao, prazo_dias_uteis)
