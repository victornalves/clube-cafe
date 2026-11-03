from nicegui import ui

from app.db import sessao
from app.domain.estados import Estado
from app.domain.formatos import formatar_documento
from app.domain.models import Membro, Papel, Registro, Usuario
from app.services import membros, registros
from app.ui.componentes import campo, resumo_objeto, selo_estado, valor_total
from app.ui.tema import pagina, titulo_pagina


def _contraparte(registro: Registro, eu: Membro) -> str:
    if eu.id == registro.corretor_id:
        return f'{registro.vendedor.nome} → {registro.comprador.nome}'
    outro = registro.comprador if eu.id == registro.vendedor_id else registro.vendedor
    lado = 'Comprador' if outro is registro.comprador else 'Vendedor'
    return f'{lado}: {outro.nome}'


def _meu_papel(registro: Registro, eu: Membro) -> str:
    if eu.id == registro.vendedor_id:
        return 'Você vende'
    if eu.id == registro.comprador_id:
        return 'Você compra'
    return 'Você intermedeia'


@pagina('/', Papel.MEMBRO, 'Meus registros')
def meus_registros(usuario: Usuario):
    with sessao() as s:
        eu = membros.do_usuario(s, usuario)
        # Rascunho descartado (cancelado antes de chegar às partes) sai da lista
        lista = [
            r
            for r in registros.listar(s, usuario)
            if not (r.estado == Estado.CANCELADO and r.enviado_as_partes_em is None)
        ]

    with ui.row().classes('w-full items-end justify-between'):
        titulo_pagina('Meus registros', 'Contratos em que você é parte.')
        ui.button('Novo registro', icon='add', on_click=lambda: ui.navigate.to('/registros/novo')).props(
            'unelevated no-caps'
        )

    if not lista:
        with ui.card().classes('w-full items-center q-pa-xl'):
            ui.icon('description', size='xl').classes('text-grey-5')
            ui.label('Você ainda não tem registros.').classes('text-grey-8')
        return

    for r in lista:
        with (
            ui.card()
            .classes('w-full cursor-pointer hover:shadow-md')
            .on('click', lambda r=r: ui.navigate.to(f'/registros/{r.id}'))
        ):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.row().classes('items-center gap-2'):
                    ui.label(r.numero).classes('text-subtitle1 text-weight-medium')
                    ui.label(_meu_papel(r, eu)).classes('text-caption text-grey-7')
                selo_estado(r.estado)
            ui.label(_contraparte(r, eu)).classes('text-body1')
            with ui.element('div').classes('grid grid-cols-2 sm:grid-cols-3 gap-2 w-full'):
                campo('Objeto', resumo_objeto(r))
                campo('Valor total', valor_total(r))
                campo('Atualizado', r.atualizado_em.astimezone().strftime('%d/%m/%Y %H:%M'))
            if r.estado == Estado.RASCUNHO and r.autor_id == usuario.id:
                ui.label('Continuar preenchendo →').classes('text-caption text-accent')


@pagina('/conta', Papel.MEMBRO, 'Minha conta')
def minha_conta(usuario: Usuario):
    with sessao() as s:
        eu = membros.do_usuario(s, usuario)
    titulo_pagina('Minha conta', 'Para alterar algum dado, fale com o backoffice.')
    with ui.card().classes('w-full'), ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
        campo('Nome ou razão social', eu.nome)
        campo('CPF ou CNPJ', formatar_documento(eu.documento))
        campo('Cidade', f'{eu.cidade}/{eu.uf}')
        campo('Propriedade', eu.propriedade)
        campo('Matrícula do imóvel', eu.matricula_imovel)
        if eu.representante_nome:
            campo(
                'Quem assina pela empresa',
                f'{eu.representante_nome}, {formatar_documento(eu.representante_cpf or "")}',
            )
        campo('Acesso', f'{usuario.nome} · {usuario.email}')
        campo('Membro desde', eu.membro_desde.strftime('%d/%m/%Y'))
        campo('Perfil', 'Corretor' if eu.corretor else 'Membro')
