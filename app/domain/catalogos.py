"""Listas fixas do MVP. Armazéns viram cadastro na Fase 4; produtos vêm dos domínios da B3 (pendência 2.4)."""

PRODUTOS = {
    'arabica': 'Café arábica',
    'conilon': 'Café conilon',
}

# Região → armazéns gerais credenciados (lista fixa até o cadastro de armazéns existir)
ARMAZENS_POR_REGIAO = {
    'Sul de Minas': ['Armazéns Gerais Varginha', 'Armazéns Gerais Três Pontas'],
    'Cerrado Mineiro': ['Armazém Geral Patrocínio'],
    'Mogiana': ['Armazém Geral Franca'],
}

MESES = [
    'janeiro',
    'fevereiro',
    'março',
    'abril',
    'maio',
    'junho',
    'julho',
    'agosto',
    'setembro',
    'outubro',
    'novembro',
    'dezembro',
]

KG_POR_SACA = 60
