"""Telas 05, 05c, 06 e 07: o registro em três etapas. Cada etapa grava no banco ao avançar."""

from datetime import date
from decimal import Decimal

from nicegui import ui

from app.db import sessao
from app.domain.catalogos import ARMAZENS_POR_REGIAO, KG_POR_SACA, MESES, PRODUTOS
from app.domain.estados import Estado
from app.domain.formatos import formatar_inteiro, formatar_reais
from app.domain.models import Membro, Papel, PapelNoRegistro, Registro, Usuario
from app.services import envelopes, membros, registros
from app.services.erros import NaoEncontrado
from app.services.registros import DadosObjeto, DadosPartes
from app.ui.componentes import detalhes_registro, notificar_erros, parte, rotulo_membro
from app.ui.membro.detalhe import detalhe
from app.ui.tema import pagina, titulo_pagina

ETAPAS = ['Partes', 'Objeto, preço e entrega', 'Revisão']
ROTULOS_CURTOS = ['Partes', 'Objeto', 'Revisão']  # no stepper, para caber no celular


@pagina('/registros/novo', Papel.MEMBRO, 'Novo registro')
def novo(usuario: Usuario):
    editor(usuario, None, 1)


@pagina('/registros/{registro_id}', Papel.MEMBRO, 'Registro')
def abrir(usuario: Usuario, registro_id: int, etapa: int | None = None):
    try:
        with sessao() as s:
            registro = registros.obter(s, usuario, registro_id)
    except NaoEncontrado:
        titulo_pagina('Registro não encontrado', 'Ele não existe ou você não é parte dele.')
        ui.button('Voltar para meus registros', on_click=lambda: ui.navigate.to('/')).props('flat no-caps')
        return
    if registro.estado == Estado.RASCUNHO and registro.autor_id == usuario.id:
        if etapa is None:
            # Reabrir o rascunho leva para onde a pessoa parou
            etapa = 2 if registros.pendencias_objeto(registro) else 3
        editor(usuario, registro, min(max(etapa, 1), 3))
    else:
        detalhe(usuario, registro)


def _ir(registro_id: int, etapa: int):
    ui.navigate.to(f'/registros/{registro_id}?etapa={etapa}')


def editor(usuario: Usuario, registro: Registro | None, etapa: int):
    with sessao() as s:
        eu = membros.do_usuario(s, usuario)
        outros = [m for m in membros.selecionaveis(s) if m.id != eu.id]

    with ui.row().classes('w-full items-center gap-2'):
        ui.link('Meus registros', '/').classes('text-primary')
        ui.label('›').classes('text-grey-6')
        ui.label(registro.numero if registro else 'Novo registro').classes('text-grey-8')
    titulo_pagina(f'Novo registro — {ETAPAS[etapa - 1].lower()}')

    stepper = ui.stepper(value=ROTULOS_CURTOS[etapa - 1]).props(
        'flat alternative-labels active-color=primary done-color=primary'
    )
    stepper.classes('w-full bg-transparent')
    with stepper:
        for i, nome in enumerate(ROTULOS_CURTOS, start=1):
            with ui.step(nome).props(f':done="{str(i < etapa).lower()}"').classes('q-pa-none'):
                if i != etapa:
                    continue
                if etapa == 1:
                    etapa_partes(usuario, registro, eu, outros)
                elif registro is None:
                    ui.navigate.to('/registros/novo')
                elif etapa == 2:
                    etapa_objeto(usuario, registro)
                else:
                    etapa_revisao(usuario, registro)


def etapa_partes(usuario: Usuario, registro: Registro | None, eu: Membro, outros: list[Membro]):
    opcoes = {m.id: rotulo_membro(m) for m in outros}
    corretores = {m.id: rotulo_membro(m) for m in outros if m.corretor}
    if registro:
        estado = {
            'papel': registro.papel_autor,
            'vendedor_id': registro.vendedor_id,
            'comprador_id': registro.comprador_id,
            'corretor_id': registro.corretor_id,
            'tem_corretor': registro.corretor_id is not None,
        }
    else:
        # Corretor logado já vem com "Sou o corretor" marcado (reunião 4)
        papel = PapelNoRegistro.CORRETOR if eu.corretor else PapelNoRegistro.VENDEDOR
        estado = {'papel': papel, 'vendedor_id': None, 'comprador_id': None, 'corretor_id': None, 'tem_corretor': False}

    papeis = {PapelNoRegistro.VENDEDOR: 'Sou o vendedor', PapelNoRegistro.COMPRADOR: 'Sou o comprador'}
    if eu.corretor:
        papeis[PapelNoRegistro.CORRETOR] = 'Sou o corretor'

    with ui.card().classes('w-full'):
        ui.label('Seu papel neste contrato').classes('text-subtitle1 text-weight-medium text-primary')
        ui.label('As outras partes precisam ser membros da Câmara.').classes('text-body2 text-grey-8')
        ui.radio(papeis, value=estado['papel'], on_change=lambda e: (estado.update(papel=e.value), campos.refresh()))

    def seletor(rotulo: str, chave: str, opcoes_: dict):
        valor = estado[chave] if estado[chave] in opcoes_ else None
        ui.select(
            opcoes_,
            label=rotulo,
            value=valor,
            with_input=True,
            clearable=True,
            on_change=lambda e: estado.update({chave: e.value}),
        ).props('outlined').classes('w-full')

    @ui.refreshable
    def campos():
        papel = estado['papel']
        with ui.card().classes('w-full'):
            if papel == PapelNoRegistro.VENDEDOR:
                parte('Você, vendedor (emitente da CPR)', eu)
                seletor('Comprador (credor) — buscar por nome, CPF ou CNPJ', 'comprador_id', opcoes)
            elif papel == PapelNoRegistro.COMPRADOR:
                parte('Você, comprador (credor)', eu)
                seletor('Vendedor (emitente da CPR) — buscar por nome, CPF ou CNPJ', 'vendedor_id', opcoes)
            else:
                parte('Você, corretor (intermediário)', eu)
                ui.label('Você preenche e media; vendedor e comprador assinam, cada um com o próprio certificado.')
                seletor('Vendedor (emitente da CPR)', 'vendedor_id', opcoes)
                seletor('Comprador (credor)', 'comprador_id', opcoes)
        if papel != PapelNoRegistro.CORRETOR:
            with ui.card().classes('w-full'):
                ui.label('Intermediário — corretor (opcional)').classes(
                    'text-subtitle1 text-weight-medium text-primary'
                )
                ui.checkbox(
                    'Este contrato tem um corretor como intermediário',
                    value=estado['tem_corretor'],
                    on_change=lambda e: (estado.update(tem_corretor=e.value), campos.refresh()),
                )
                if estado['tem_corretor']:
                    seletor('Corretor', 'corretor_id', corretores)

    campos()

    def dados() -> DadosPartes:
        papel = estado['papel']
        return DadosPartes(
            papel_autor=papel,
            vendedor_id=eu.id if papel == PapelNoRegistro.VENDEDOR else estado['vendedor_id'],
            comprador_id=eu.id if papel == PapelNoRegistro.COMPRADOR else estado['comprador_id'],
            corretor_id=eu.id
            if papel == PapelNoRegistro.CORRETOR
            else (estado['corretor_id'] if estado['tem_corretor'] else None),
        )

    def continuar():
        resultado = {}

        def gravar():
            with sessao() as s:
                if registro is None:
                    resultado['id'] = registros.criar_rascunho(s, usuario, dados()).id
                else:
                    resultado['id'] = registros.salvar_partes(s, usuario, registro.id, dados()).id

        if notificar_erros(gravar):
            _ir(resultado['id'], 2)

    with ui.row().classes('w-full justify-between'):
        ui.button('Voltar para meus registros', on_click=lambda: ui.navigate.to('/')).props('flat no-caps')
        ui.button('Continuar', on_click=continuar).props('unelevated no-caps icon-right=arrow_forward')


def etapa_objeto(usuario: Usuario, registro: Registro):
    hoje = date.today()
    anos = list(range(hoje.year, hoje.year + 4))

    with ui.card().classes('w-full'):
        ui.label('O café').classes('text-subtitle1 text-weight-medium text-primary')
        produto = ui.radio(PRODUTOS, value=registro.produto).props('inline')

    with ui.card().classes('w-full'):
        ui.label('Quantidade e preço').classes('text-subtitle1 text-weight-medium text-primary')
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
            sacas = ui.number('Quantidade em sacas de 60 kg', value=registro.sacas, min=1, precision=0)
            preco_atual = float(registro.preco_saca) if registro.preco_saca is not None else None
            preco = ui.number('Preço por saca (R$)', value=preco_atual, min=0.01, precision=2)
            sacas.props('outlined')
            preco.props('outlined')
        total = ui.label().classes('text-body1')

        def atualizar_total():
            if sacas.value and preco.value:
                valor = Decimal(str(preco.value)) * int(sacas.value)
                peso = formatar_inteiro(int(sacas.value) * KG_POR_SACA)
                total.text = f'Peso total: {peso} kg · Valor total do contrato: R$ {formatar_reais(valor)}'
            else:
                total.text = 'Informe quantidade e preço para ver o valor total.'

        sacas.on_value_change(atualizar_total)
        preco.on_value_change(atualizar_total)
        atualizar_total()

    with ui.card().classes('w-full'):
        ui.label('Entrega').classes('text-subtitle1 text-weight-medium text-primary')
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
            regiao = ui.select(list(ARMAZENS_POR_REGIAO), label='Região', value=registro.regiao).props('outlined')
            armazem = ui.select(
                ARMAZENS_POR_REGIAO.get(registro.regiao, []), label='Armazém de entrega', value=registro.armazem
            ).props('outlined')
            mes = ui.select({i: m.capitalize() for i, m in enumerate(MESES, 1)}, label='Mês de entrega')
            ano = ui.select(anos, label='Ano de entrega')
            mes.props('outlined').set_value(registro.entrega_mes)
            ano.props('outlined').set_value(registro.entrega_ano)
        ui.label('Só armazéns gerais credenciados: guardam o café e não negociam.').classes('text-caption text-grey-7')
        ui.label('A entrega pode acontecer em qualquer dia do mês de referência.').classes('text-caption text-grey-7')

        def trocar_regiao(e):
            armazem.set_options(ARMAZENS_POR_REGIAO.get(e.value, []), value=None)

        regiao.on_value_change(trocar_regiao)

    with ui.card().classes('w-full'):
        ui.label('Pagamento').classes('text-subtitle1 text-weight-medium text-primary')
        adiantado = ui.checkbox('O pagamento já foi adiantado ao vendedor', value=registro.pagamento_adiantado)
        ui.label('Marque se o comprador já pagou, total ou parte, antes deste registro.').classes(
            'text-caption text-grey-7'
        )

    def gravar() -> Registro:
        with sessao() as s:
            return registros.salvar_objeto(
                s,
                usuario,
                registro.id,
                DadosObjeto(
                    produto=produto.value,
                    sacas=int(sacas.value) if sacas.value else None,
                    preco_saca=Decimal(str(preco.value)).quantize(Decimal('0.01')) if preco.value else None,
                    regiao=regiao.value,
                    armazem=armazem.value,
                    entrega_mes=mes.value,
                    entrega_ano=ano.value,
                    pagamento_adiantado=adiantado.value,
                ),
            )

    def continuar():
        atualizado = gravar()
        if pendencias := registros.pendencias_objeto(atualizado):
            ui.notify(' '.join(pendencias), type='warning', multi_line=True, position='top')
            return
        _ir(registro.id, 3)

    def salvar_e_sair():
        gravar()
        ui.navigate.to('/')

    with ui.row().classes('w-full items-center'):
        ui.button('Voltar para partes', icon='arrow_back', on_click=lambda: (gravar(), _ir(registro.id, 1))).props(
            'flat no-caps'
        )
        ui.space()
        ui.button('Salvar rascunho e sair', on_click=salvar_e_sair).props('flat no-caps')
        ui.button('Continuar para revisão', on_click=continuar).props('unelevated no-caps icon-right=arrow_forward')


def etapa_revisao(usuario: Usuario, registro: Registro):
    if pendencias := registros.pendencias_objeto(registro):
        _ir(registro.id, 2)
        ui.notify(' '.join(pendencias), type='warning', multi_line=True, position='top')
        return

    ui.label(
        'Confira os dados. Depois que o envelope for assinado, qualquer correção exige envelope novo '
        'e nova assinatura de todas as partes.'
    ).classes('text-body2 text-grey-8')
    detalhes_registro(registro, corrigir=lambda etapa: _ir(registro.id, etapa))

    with ui.card().classes('w-full'):
        ui.label('Modelo de contrato').classes('text-subtitle1 text-weight-medium text-primary')
        ui.label(
            'Contrato de compra e venda de café a termo (simulado, sem valor jurídico) e CPR de liquidação física (documento-padrão da Câmara, CPR V.1).'
        )

    def descartar():
        with ui.dialog() as dialogo, ui.card():
            ui.label(f'Descartar o rascunho {registro.numero}?').classes('text-h6')
            ui.label('Ele sai da sua lista de registros. Essa ação não pode ser desfeita.')
            with ui.row().classes('w-full justify-end'):
                ui.button('Manter', on_click=dialogo.close).props('flat no-caps')

                def confirmar():
                    with sessao() as s:
                        registros.descartar(s, usuario, registro.id)
                    ui.navigate.to('/')

                ui.button('Descartar', on_click=confirmar).props('unelevated no-caps color=negative')
        dialogo.open()

    with ui.row().classes('w-full items-center'):
        ui.button('Descartar rascunho', icon='delete_outline', on_click=descartar).props('flat no-caps color=negative')
        ui.space()
        ui.button('Salvar e sair', on_click=lambda: ui.navigate.to('/')).props('flat no-caps')
        ui.button(
            'Gerar envelope para assinatura', icon='draw', on_click=lambda: gerar_envelope(usuario, registro)
        ).props('unelevated no-caps')


def gerar_envelope(usuario: Usuario, registro: Registro):
    resultado = {}

    def executar():
        with sessao() as s:
            resultado['erros'] = envelopes.gerar_envelope(s, usuario, registro.id)

    if not notificar_erros(executar):
        return
    if not resultado['erros']:
        ui.navigate.to(f'/registros/{registro.id}')
        return

    # Pré-validação barrou (T-08): nada foi enviado às partes, o registro continua em rascunho
    with ui.dialog() as dialogo, ui.card().classes('max-w-lg'):
        ui.label('O envelope não foi gerado').classes('text-h6')
        ui.label(
            'Antes de enviar para assinatura, conferimos os dados com as regras da B3. Estes pontos precisam '
            'ser resolvidos. Nada foi enviado às outras partes.'
        ).classes('text-body2')
        with ui.column().classes('gap-1 q-my-sm'):
            for erro in resultado['erros']:
                with ui.row().classes('no-wrap items-start gap-2'):
                    ui.icon('error_outline', color='negative').classes('q-mt-xs')
                    ui.label(erro)
        with ui.row().classes('w-full justify-end'):
            ui.button('Entendi', on_click=dialogo.close).props('unelevated no-caps')
    dialogo.open()
