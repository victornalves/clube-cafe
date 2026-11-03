from collections.abc import Callable

from nicegui import ui

from app.domain.catalogos import MESES, PRODUTOS
from app.domain.estados import NOME_INTERNO, VISAO_MEMBRO, Estado
from app.domain.formatos import formatar_documento, formatar_inteiro, formatar_reais
from app.domain.models import Membro, Registro
from app.services.erros import ErroDeNegocio

COR_VISAO_MEMBRO = {
    'Rascunho': 'grey-7',
    'Aguardando assinaturas': 'accent',
    'Em processamento': 'secondary',
    'Registrado': 'primary',
    'Cancelado': 'grey-5',
}


def selo_estado(estado: Estado, interno: bool = False):
    visao = VISAO_MEMBRO[estado]
    texto = NOME_INTERNO[estado] if interno else visao
    ui.badge(texto, color=COR_VISAO_MEMBRO[visao]).classes('text-body2 q-px-sm')


def notificar_erros(fn: Callable[[], None]) -> bool:
    """Roda a ação e mostra o erro de negócio, se houver. Devolve True se deu certo."""
    try:
        fn()
    except ErroDeNegocio as erro:
        ui.notify(str(erro), type='negative', multi_line=True, position='top')
        return False
    return True


def rotulo_membro(m: Membro) -> str:
    return f'{m.nome} · {formatar_documento(m.documento)} · {m.cidade}/{m.uf}'


def entrega_por_extenso(registro: Registro) -> str:
    if not registro.entrega_mes or not registro.entrega_ano:
        return '—'
    return f'{MESES[registro.entrega_mes - 1]} de {registro.entrega_ano}'.capitalize()


def resumo_objeto(registro: Registro) -> str:
    if not registro.sacas:
        return 'Objeto ainda não preenchido'
    produto = PRODUTOS.get(registro.produto or '', '')
    return f'{produto} · {formatar_inteiro(registro.sacas)} sacas'


def valor_total(registro: Registro) -> str:
    return f'R$ {formatar_reais(registro.valor_total)}' if registro.valor_total else '—'


def campo(rotulo: str, valor: str):
    with ui.column().classes('gap-0'):
        ui.label(rotulo).classes('text-caption text-grey-7')
        ui.label(valor or '—').classes('text-body1')


def bloco(titulo: str, corrigir: Callable[[], None] | None = None):
    """Cartão de seção, com o link "Corrigir" da revisão (tela 07)."""
    cartao = ui.card().classes('w-full')
    with cartao, ui.row().classes('w-full items-center justify-between'):
        ui.label(titulo).classes('text-subtitle1 text-weight-medium text-primary')
        if corrigir:
            ui.button('Corrigir', on_click=corrigir).props('flat dense no-caps color=accent')
    return cartao


def parte(titulo: str, m: Membro | None):
    with ui.column().classes('gap-0'):
        ui.label(titulo).classes('text-caption text-grey-7')
        if m is None:
            ui.label('Sem corretor neste contrato').classes('text-body1 text-grey-7')
            return
        ui.label(m.nome).classes('text-body1')
        ui.label(f'{formatar_documento(m.documento)} · {m.cidade}/{m.uf}').classes('text-body2 text-grey-8')
        if m.representante_nome:
            ui.label(f'Assina: {m.representante_nome}, {(m.representante_cargo or "").lower()}').classes(
                'text-body2 text-grey-8'
            )


def detalhes_registro(registro: Registro, corrigir: Callable[[int], None] | None = None):
    grade = 'grid grid-cols-1 sm:grid-cols-3 gap-4 w-full'
    with bloco('Partes', corrigir and (lambda: corrigir(1))), ui.element('div').classes(grade):
        parte('Vendedor (emitente da CPR)', registro.vendedor)
        parte('Comprador (credor)', registro.comprador)
        parte('Intermediário', registro.corretor)
    with bloco('Objeto, preço e entrega', corrigir and (lambda: corrigir(2))), ui.element('div').classes(grade):
        campo('Produto', PRODUTOS.get(registro.produto or '', ''))
        campo(
            'Quantidade',
            f'{formatar_inteiro(registro.sacas)} sacas de 60 kg · {formatar_inteiro(registro.peso_kg)} kg'
            if registro.sacas
            else '',
        )
        campo('Preço por saca', f'R$ {formatar_reais(registro.preco_saca)}' if registro.preco_saca else '')
        campo('Valor total', valor_total(registro))
        campo('Região e armazém', f'{registro.regiao} · {registro.armazem}' if registro.armazem else '')
        campo('Prazo de entrega', entrega_por_extenso(registro))
        campo('Pagamento adiantado', 'Sim' if registro.pagamento_adiantado else 'Não')
