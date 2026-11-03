from nicegui import ui

from app.db import sessao
from app.domain.formatos import formatar_documento
from app.domain.models import Membro, Papel, TipoPessoa, Usuario
from app.services import membros
from app.services.membros import DadosMembro
from app.ui.componentes import notificar_erros
from app.ui.tema import pagina, titulo_pagina

COLUNAS = [
    {'name': 'nome', 'label': 'Nome ou razão social', 'field': 'nome', 'align': 'left', 'sortable': True},
    {'name': 'documento', 'label': 'CPF/CNPJ', 'field': 'documento', 'align': 'left'},
    {'name': 'local', 'label': 'Cidade', 'field': 'local', 'align': 'left', 'sortable': True},
    {'name': 'email', 'label': 'E-mail de acesso', 'field': 'email', 'align': 'left'},
    {'name': 'perfil', 'label': 'Perfil', 'field': 'perfil', 'align': 'left'},
    {'name': 'situacao', 'label': 'Situação', 'field': 'situacao', 'align': 'left', 'sortable': True},
]


def _linha(m: Membro) -> dict:
    if not m.usuario.ativo:
        situacao = 'Desativado'
    elif m.termos_aceitos_em is None:
        situacao = 'Aguardando aceite dos termos'
    else:
        situacao = 'Ativo'
    return {
        'id': m.id,
        'nome': m.nome,
        'documento': formatar_documento(m.documento),
        'local': f'{m.cidade}/{m.uf}',
        'email': m.usuario.email,
        'perfil': 'Corretor'
        if m.corretor
        else ('Pessoa jurídica' if m.tipo_pessoa == TipoPessoa.PJ else 'Pessoa física'),
        'situacao': situacao,
    }


@pagina('/backoffice/membros', Papel.OPERADOR, 'Membros')
def tela_membros(operador: Usuario):
    def carregar() -> list[dict]:
        with sessao() as s:
            return [_linha(m) for m in membros.listar(s, operador)]

    def recarregar():
        tabela.rows = carregar()

    with ui.row().classes('w-full items-end justify-between'):
        titulo_pagina(
            'Membros',
            'Cadastro direto pelo backoffice, enquanto a proposta de adesão não faz parte do MVP.',
        )
        ui.button('Cadastrar membro', icon='person_add', on_click=lambda: formulario(operador, None, recarregar)).props(
            'unelevated no-caps'
        )

    busca = ui.input(placeholder='Buscar por nome, documento, cidade ou e-mail').props('outlined dense clearable')
    busca.classes('w-full sm:w-96')
    tabela = ui.table(columns=COLUNAS, rows=carregar(), row_key='id', pagination=20).classes('w-full')
    tabela.props('flat bordered')
    tabela.bind_filter_from(busca, 'value')
    tabela.on('rowClick', lambda e: formulario(operador, e.args[1]['id'], recarregar))
    ui.label('Clique em um membro para editar.').classes('text-caption text-grey-7')


def formulario(operador: Usuario, membro_id: int | None, ao_salvar):
    novo = membro_id is None
    if novo:
        m = None
        atual = {'tipo_pessoa': TipoPessoa.PF, 'corretor': False, 'termos_aceitos': False, 'ativo': True}
    else:
        with sessao() as s:
            m = membros.obter(s, operador, membro_id)
            atual = {
                'tipo_pessoa': m.tipo_pessoa,
                'documento': formatar_documento(m.documento),
                'nome': m.nome,
                'nome_usuario': m.usuario.nome,
                'email': m.usuario.email,
                'cidade': m.cidade,
                'uf': m.uf,
                'propriedade': m.propriedade,
                'matricula_imovel': m.matricula_imovel,
                'representante_nome': m.representante_nome,
                'representante_cpf': formatar_documento(m.representante_cpf or ''),
                'representante_cargo': m.representante_cargo,
                'corretor': m.corretor,
                'termos_aceitos': m.termos_aceitos_em is not None,
                'ativo': m.usuario.ativo,
            }

    with ui.dialog() as dialogo, ui.card().classes('w-full max-w-2xl'):
        ui.label('Cadastrar membro' if novo else f'Editar · {m.nome}').classes('text-h6')

        tipo = ui.toggle({TipoPessoa.PF: 'Pessoa física', TipoPessoa.PJ: 'Pessoa jurídica'}, value=atual['tipo_pessoa'])
        tipo.props('no-caps unelevated toggle-color=primary')

        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-x-4 w-full'):
            documento = ui.input('CPF ou CNPJ', value=atual.get('documento'))
            nome = ui.input('Nome ou razão social', value=atual.get('nome'))
            cidade = ui.input('Cidade', value=atual.get('cidade'))
            uf = ui.input('UF', value=atual.get('uf')).props('maxlength=2')
            propriedade = ui.input('Propriedade (produtor)', value=atual.get('propriedade'))
            matricula = ui.input('Matrícula do imóvel', value=atual.get('matricula_imovel'))

        with ui.column().classes('w-full gap-0') as bloco_pj:
            ui.label('Quem assina pela empresa').classes('text-subtitle2 q-mt-sm')
            with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-3 gap-x-4 w-full'):
                rep_nome = ui.input('Nome', value=atual.get('representante_nome'))
                rep_cpf = ui.input('CPF', value=atual.get('representante_cpf'))
                rep_cargo = ui.input('Cargo', value=atual.get('representante_cargo'))
        bloco_pj.bind_visibility_from(tipo, 'value', backward=lambda v: v == TipoPessoa.PJ)

        ui.label('Acesso à plataforma').classes('text-subtitle2 q-mt-sm')
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-x-4 w-full'):
            nome_usuario = ui.input('Nome de quem acessa', value=atual.get('nome_usuario'))
            email = ui.input('E-mail', value=atual.get('email'))
            senha = ui.input('Senha inicial', password=True) if novo else None

        corretor = ui.checkbox('É corretor (pode intermediar registros)', value=atual['corretor'])
        termos = ui.checkbox('Aceitou os termos do clube', value=atual['termos_aceitos'])
        ui.label(
            'Até o fluxo de termos existir, o backoffice marca o aceite. Sem ele, o membro não pode ser escolhido como parte.'
        ).classes('text-caption text-grey-7')

        def dados() -> DadosMembro:
            return DadosMembro(
                email=email.value or '',
                nome_usuario=nome_usuario.value or '',
                tipo_pessoa=tipo.value,
                documento=documento.value or '',
                nome=nome.value or '',
                cidade=cidade.value or '',
                uf=uf.value or '',
                propriedade=propriedade.value,
                matricula_imovel=matricula.value,
                representante_nome=rep_nome.value,
                representante_cpf=rep_cpf.value,
                representante_cargo=rep_cargo.value,
                corretor=corretor.value,
                termos_aceitos=termos.value,
            )

        def salvar():
            def gravar():
                with sessao() as s:
                    if novo:
                        membros.criar(s, operador, dados(), senha.value or '')
                    else:
                        membros.editar(s, operador, membro_id, dados())

            if notificar_erros(gravar):
                ui.notify('Membro salvo.', type='positive')
                dialogo.close()
                ao_salvar()

        def alternar_ativo():
            with sessao() as s:
                membros.alterar_ativo(s, operador, membro_id, not atual['ativo'])
            ui.notify('Acesso desativado.' if atual['ativo'] else 'Acesso reativado.')
            dialogo.close()
            ao_salvar()

        with ui.row().classes('w-full justify-between q-mt-md'):
            if not novo:
                ui.button('Desativar acesso' if atual['ativo'] else 'Reativar acesso', on_click=alternar_ativo).props(
                    'flat no-caps color=negative' if atual['ativo'] else 'flat no-caps'
                )
            ui.space()
            ui.button('Cancelar', on_click=dialogo.close).props('flat no-caps')
            ui.button('Salvar', on_click=salvar).props('unelevated no-caps')

    dialogo.open()
