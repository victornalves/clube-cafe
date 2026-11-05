"""Telas públicas da adesão: 02 (propor), 02b (enviada), 02c (assinar por link), diligência, criar senha e caixa simulada."""

from fastapi import Response
from nicegui import app, events, ui

from app.db import sessao
from app.domain import adesao as dominio
from app.domain.adesao import SituacaoProposta
from app.domain.models import Atuacao, PropostaAdesao
from app.services import adesao, auth, emails
from app.services.adesao import Arquivo, DadosProponente, DadosProposta, DocumentoDeMembroAtivo
from app.services.erros import AcessoNegado, ErroDeNegocio, NaoEncontrado
from app.ui.componentes import notificar_erros
from app.ui.tema import INICIO, aviso_simulado, layout_publico, titulo_pagina

UFS = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR',
       'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']  # fmt: skip
ATUACOES = {
    Atuacao.PRODUTOR: 'Produtor',
    Atuacao.COOPERATIVA: 'Cooperativa',
    Atuacao.EXPORTADORA: 'Exportadora',
    Atuacao.TORREFADORA: 'Torrefadora',
    Atuacao.CORRETOR: 'Corretor',
}
ACEITOS = '.pdf,.jpg,.jpeg,.png'
DEZ_MB = 10 * 1024 * 1024


def _hora(momento) -> str:
    return momento.astimezone().strftime('%d/%m/%Y, às %H:%M')


def _upload(rotulo: str, ao_receber, multiplo: bool = False):
    async def receber(e: events.UploadEventArguments):
        ao_receber(Arquivo(e.file.name, e.file.content_type, await e.file.read()))

    ui.upload(
        label=rotulo, auto_upload=True, multiple=multiplo, max_file_size=DEZ_MB, on_upload=receber,
        on_rejected=lambda: ui.notify('Arquivo acima de 10 MB.', type='warning'),
    ).props(f'accept={ACEITOS} flat bordered color=grey-2 text-color=primary').classes('w-full')  # fmt: skip


def _secao(titulo: str, subtitulo: str | None = None):
    cartao = ui.card().classes('w-full')
    with cartao:
        ui.label(titulo).classes('text-subtitle1 text-weight-medium text-primary')
        if subtitulo:
            ui.label(subtitulo).classes('text-body2 text-grey-8')
    return cartao


@ui.page('/adesao', title='Propor adesão · Câmara do Comércio de Café')
def propor():
    with layout_publico():
        conteudo = ui.column().classes('w-full gap-4')
    with conteudo:
        formulario(conteudo)


def formulario(conteudo):
    estado = {'corretor': False, 'cartas': [None, None], 'documentos': []}

    titulo_pagina(
        'Propor adesão à Câmara',
        'Sua proposta é avaliada pelo comitê de admissão, depois de você e dos seus 2 proponentes assinarem.',
    )

    with _secao('Quem está preenchendo'):
        quem = ui.radio({'eu': 'Eu mesmo. A proposta é minha.', 'corretor': 'Sou corretor, preenchendo por um produtor'},
                        value='eu')  # fmt: skip
        with ui.column().classes('w-full gap-0') as bloco_corretor:
            with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-x-4 w-full'):
                corretor_nome = ui.input('Seu nome').props('outlined')
                corretor_email = ui.input('Seu e-mail').props('outlined type=email')
            ui.label('Você preenche, mas quem assina é o produtor: ele recebe a proposta no e-mail informado abaixo.')
        bloco_corretor.bind_visibility_from(quem, 'value', backward=lambda v: v == 'corretor')

    with _secao('Candidato', 'Quem está pedindo para entrar na Câmara.'):
        with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-x-4 w-full'):
            nome = ui.input('Nome completo ou razão social').props('outlined')
            documento = ui.input('CPF ou CNPJ').props('outlined')
            atuacao = ui.select(ATUACOES, label='Atuação no mercado de café', value=Atuacao.PRODUTOR).props('outlined')
            sacas = ui.number('Volume aproximado por safra (sacas de 60 kg)', min=0, precision=0).props('outlined')
            email = ui.input('E-mail', placeholder='É para ele que vai o pedido de assinatura').props(
                'outlined type=email'
            )
            telefone = ui.input('Telefone com DDD').props('outlined')
            propriedade = ui.input('Nome da fazenda ou da empresa').props('outlined')
            with ui.row().classes('w-full no-wrap gap-2'):
                cidade = ui.input('Município').props('outlined').classes('col')
                uf = ui.select(UFS, label='UF', value='MG').props('outlined').classes('w-24')
        with ui.column().classes('w-full gap-0') as bloco_pj:
            ui.label('Quem assina pela empresa').classes('text-subtitle2 q-mt-sm')
            with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-x-4 w-full'):
                rep_nome = ui.input('Nome').props('outlined')
                rep_cpf = ui.input('CPF').props('outlined')
        bloco_pj.bind_visibility_from(
            documento, 'value', backward=lambda v: len(''.join(filter(str.isdigit, v or ''))) == 14
        )

    campos_proponentes = []
    with _secao('Proponentes — exatamente 2, os dois obrigatórios',
                'Duas pessoas que conhecem você e o seu trabalho. Podem ser membros da Câmara ou pessoas de fora, '
                'reconhecidas no mercado de café. Anexe a carta de recomendação de cada uma.'):  # fmt: skip
        for i in range(2):
            ui.label(f'Proponente {i + 1}').classes('text-subtitle2 q-mt-sm')
            with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-3 gap-x-4 w-full'):
                campos = (
                    ui.input('Nome completo').props('outlined'),
                    ui.input('E-mail').props('outlined type=email'),
                    ui.input('Telefone com DDD').props('outlined'),
                )
            campos_proponentes.append(campos)
            rotulo = ui.label('Nenhuma carta anexada').classes('text-caption text-grey-7')

            def guardar(arquivo: Arquivo, i=i, rotulo=rotulo):
                estado['cartas'][i] = arquivo
                rotulo.text = f'Carta anexada: {arquivo.nome}'

            _upload(f'Carta de recomendação do proponente {i + 1} (PDF ou imagem, até 10 MB)', guardar)

    with _secao('Outros documentos — opcional', 'Referências, contrato social, declaração de propriedade.'):
        lista_docs = ui.label().classes('text-caption text-grey-7')

        def guardar_documento(arquivo: Arquivo):
            estado['documentos'].append(arquivo)
            lista_docs.text = 'Anexados: ' + ', '.join(a.nome for a in estado['documentos'])

        _upload('Documentos (pode mais de um)', guardar_documento, multiplo=True)

    def enviar():
        corretor = quem.value == 'corretor'
        dados = DadosProposta(
            nome=nome.value or '',
            documento=documento.value or '',
            atuacao=atuacao.value,
            email=email.value or '',
            telefone=telefone.value or '',
            cidade=cidade.value or '',
            uf=uf.value or '',
            propriedade=propriedade.value,
            sacas_safra=int(sacas.value) if sacas.value else None,
            representante_nome=rep_nome.value,
            representante_cpf=rep_cpf.value,
            corretor_nome=corretor_nome.value if corretor else None,
            corretor_email=(corretor_email.value or '') if corretor else None,
            proponentes=[
                DadosProponente(c[0].value or '', c[1].value or '', c[2].value or '', estado['cartas'][i])
                for i, c in enumerate(campos_proponentes)
            ],
            documentos=estado['documentos'],
        )
        resultado = {}

        def gravar():
            with sessao() as s:
                resultado['proposta'] = _resumo(adesao.enviar_proposta(s, dados))

        try:
            ok = notificar_erros(gravar)
        except DocumentoDeMembroAtivo:
            # RN-07: sem dizer se a conta existe
            ui.notify('Para continuar, entre com a sua conta.', type='info', position='top')
            ui.navigate.to('/login')
            return
        if ok:
            conteudo.clear()
            with conteudo:
                enviada(resultado['proposta'])
            ui.run_javascript('window.scrollTo(0, 0)')

    with ui.row().classes('w-full justify-end'):
        ui.button('Enviar proposta', icon='send', on_click=enviar).props('unelevated no-caps size=lg')


def _resumo(proposta: PropostaAdesao) -> dict:
    return {
        'numero': proposta.numero,
        'nome': proposta.nome,
        'corretor': proposta.corretor_nome,
        'signatarios': [(dominio.PAPEIS[s.papel], s.nome) for s in proposta.signatarios],
    }


def enviada(p: dict):
    """Tela 02b."""
    with ui.row().classes('items-center gap-2'):
        ui.icon('mark_email_read', size='lg', color='primary')
        titulo_pagina('Proposta enviada para assinatura', f'Número de acompanhamento: {p["numero"]}')
    with _secao('Assinaturas da proposta'):
        for papel, nome in p['signatarios']:
            with ui.row().classes('items-center gap-2'):
                ui.icon('radio_button_unchecked', color='grey-6')
                ui.label(f'{nome} · {papel} · aguardando').classes('text-body2')
    with _secao('O que acontece agora'):
        if p['corretor']:
            ui.label(f'{p["nome"]} recebe a proposta preenchida por {p["corretor"]} e assina pelo próprio link. '
                     'O corretor não assina por ele.')  # fmt: skip
        ui.label('Cada pessoa recebe um link por e-mail para assinar. Se um proponente recusar ou deixar o prazo '
                 'passar, a proposta não segue e o candidato pode refazê-la.')  # fmt: skip
        ui.label('Com as 3 assinaturas, a proposta entra na fila do comitê de admissão, que se reúne uma vez por '
                 'semana e pode aprovar, recusar ou pedir mais dados.')  # fmt: skip
    if auth.login_demo_ligado():
        aviso_simulado('Demonstração: nenhum e-mail sai de verdade. Os três links de assinatura estão na caixa de '
                       'e-mails simulada.')  # fmt: skip
        ui.button('Abrir a caixa de e-mails simulada', icon='inbox', on_click=lambda: ui.navigate.to('/emails')).props(
            'unelevated no-caps'
        )


@ui.page('/adesao/assinar/{token}', title='Assinar proposta · Câmara do Comércio de Café')
def assinar(token: str):
    """Tela 02c: candidato ou proponente, membro da Câmara ou não, pelo link do e-mail."""
    with layout_publico():
        try:
            with sessao() as s:
                sig = adesao.abrir_para_assinar(s, token)
                proposta = sig.proposta
                outros = [x for x in proposta.signatarios if x.id != sig.id and x.papel != 'candidato']
                carta = next((a for a in proposta.anexos if a.signatario_id == sig.id), None)
                documentos = [a for a in proposta.anexos if a.tipo == 'documento']
        except NaoEncontrado:
            titulo_pagina('Link inválido', 'Confira se o endereço está completo.')
            return

        papel = dominio.PAPEIS[sig.papel]
        titulo_pagina(
            f'Assine a proposta de adesão · {proposta.numero}', f'{sig.nome}, você está como {papel.lower()}.'
        )
        with _secao('O que você está assinando'):
            ui.label(f'Candidato: {proposta.nome} · {proposta.propriedade or "—"}, {proposta.cidade}/{proposta.uf}')
            for x in outros:
                ui.label(f'{dominio.PAPEIS[x.papel]}: {x.nome}').classes('text-body2')
            if proposta.corretor_nome:
                ui.label(f'Preenchida por {proposta.corretor_nome}, corretor.').classes('text-body2 text-grey-8')
            if carta:
                ui.link(f'Sua carta de recomendação: {carta.nome_arquivo}', f'/adesao/anexo/{token}/{carta.id}',
                        new_tab=True)  # fmt: skip
            for doc in documentos:
                ui.link(f'Documento: {doc.nome_arquivo}', f'/adesao/anexo/{token}/{doc.id}', new_tab=True)
            ui.label(f'Este link vale até {_hora(proposta.assinaturas_vencem_em)}.').classes('text-caption text-grey-7')

        if sig.assinado_em or sig.recusado_em:
            feito = 'assinou' if sig.assinado_em else 'recusou'
            with _secao('Você já respondeu'):
                ui.label(f'Você {feito} esta proposta em {_hora(sig.assinado_em or sig.recusado_em)}.')
            return
        if proposta.situacao != SituacaoProposta.AGUARDANDO_ASSINATURAS:
            with _secao('Esta proposta não recebe mais assinaturas'):
                ui.label(f'Situação: {dominio.ROTULO[SituacaoProposta(proposta.situacao)]}.')
            return

        with _secao('Confirmar e assinar'):
            texto = ('Confirmo os dados da minha proposta e assino por minha conta.' if sig.papel == 'candidato'
                     else 'Li a minha carta de recomendação, confirmo que conheço o candidato e assino por minha conta.')  # fmt: skip
            confirmo = ui.checkbox(texto)
            aviso_simulado('Assinatura simulada. Na versão final, este passo abre o aplicativo do seu certificado '
                           'digital (token, nuvem ou arquivo A1).')  # fmt: skip

            def agir(fn, mensagem):
                def executar():
                    with sessao() as s:
                        fn(s, token)

                if notificar_erros(executar):
                    ui.notify(mensagem, type='positive')
                    ui.navigate.reload()

            with ui.row().classes('w-full justify-between'):
                ui.button(
                    'Recusar assinar', on_click=lambda: agir(adesao.recusar_assinatura, 'Recusa registrada.')
                ).props('flat no-caps color=negative')
                botao = ui.button('Assinar (simulado)', icon='draw',
                                  on_click=lambda: agir(adesao.assinar, 'Assinatura registrada.'))  # fmt: skip
                botao.props('unelevated no-caps').bind_enabled_from(confirmo, 'value')


@ui.page('/adesao/diligencia/{token}', title='Responder ao comitê · Câmara do Comércio de Café')
def diligencia(token: str):
    with layout_publico():
        try:
            with sessao() as s:
                proposta = adesao.abrir_diligencia(s, token)
        except NaoEncontrado:
            titulo_pagina('Link inválido')
            return
        titulo_pagina(f'O comitê pediu mais informações · {proposta.numero}', proposta.nome)
        with _secao('O que o comitê pediu'):
            ui.label(proposta.diligencia_pedido)
        if proposta.situacao != SituacaoProposta.EM_DILIGENCIA:
            with _secao('Pedido já respondido'):
                ui.label(proposta.diligencia_resposta or 'Resposta enviada com anexos.')
            return
        arquivos: list[Arquivo] = []
        with _secao('Sua resposta'):
            resposta = ui.textarea('Resposta').props('outlined autogrow').classes('w-full')
            anexados = ui.label().classes('text-caption text-grey-7')

            def guardar(arquivo: Arquivo):
                arquivos.append(arquivo)
                anexados.text = 'Anexados: ' + ', '.join(a.nome for a in arquivos)

            _upload('Documentos (opcional)', guardar, multiplo=True)

            def enviar():
                def gravar():
                    with sessao() as s:
                        adesao.responder_diligencia(s, token, resposta.value, arquivos)

                if notificar_erros(gravar):
                    ui.notify('Resposta enviada ao comitê.', type='positive')
                    ui.navigate.reload()

            with ui.row().classes('w-full justify-end'):
                ui.button('Enviar resposta', icon='send', on_click=enviar).props('unelevated no-caps')


@ui.page('/acesso/{token}', title='Criar senha · Câmara do Comércio de Café')
def criar_senha(token: str):
    with layout_publico():
        try:
            with sessao() as s:
                usuario = adesao.abrir_convite(s, token)
        except NaoEncontrado:
            titulo_pagina('Link inválido ou já usado', 'Se você já criou a senha, entre pelo login.')
            return
        except ErroDeNegocio as erro:
            titulo_pagina('Link expirado', str(erro))
            return
        titulo_pagina('Bem-vindo à Câmara do Comércio de Café', f'{usuario.nome} · {usuario.email}')
        with _secao('Crie a sua senha', 'No primeiro acesso, você assina os termos da Câmara; depois, já pode '
                    'registrar contratos.'):  # fmt: skip
            senha = ui.input('Senha (pelo menos 8 caracteres)', password=True).props('outlined').classes('w-full')
            confirmacao = ui.input('Repita a senha', password=True).props('outlined').classes('w-full')

            def criar():
                resultado = {}

                def gravar():
                    with sessao() as s:
                        resultado['usuario'] = adesao.criar_senha(s, token, senha.value, confirmacao.value)

                if notificar_erros(gravar):
                    app.storage.user['usuario_id'] = resultado['usuario'].id
                    ui.navigate.to(INICIO[resultado['usuario'].papel])

            ui.button('Criar senha e entrar', on_click=criar).props('unelevated no-caps').classes('w-full')


@app.get('/adesao/anexo/{token}/{anexo_id}')
def baixar_anexo_signatario(token: str, anexo_id: int):
    try:
        with sessao() as s:
            anexo = adesao.anexo_para_signatario(s, token, anexo_id)
    except NaoEncontrado:
        return Response('Arquivo não encontrado.', status_code=404)
    return _arquivo(anexo)


def _arquivo(anexo) -> Response:
    return Response(
        anexo.conteudo,
        media_type=anexo.content_type,
        headers={'Content-Disposition': f'inline; filename="{anexo.nome_arquivo}"'},
    )


@ui.page('/emails', title='E-mails simulados · Câmara do Comércio de Café')
def caixa_de_emails():
    with layout_publico():
        try:
            with sessao() as s:
                lista = emails.caixa(s)
        except AcessoNegado:
            titulo_pagina('Página não encontrada')
            return
        with ui.row().classes('w-full items-end justify-between'):
            titulo_pagina('E-mails enviados (simulado)',
                          'Tudo o que o sistema mandaria por e-mail, mais recente primeiro. Clique no link para '
                          'seguir o fluxo como o destinatário.')  # fmt: skip
            ui.button('Atualizar', icon='refresh', on_click=ui.navigate.reload).props('flat no-caps')
        if not lista:
            ui.label('Nenhum e-mail ainda.').classes('text-grey-8')
        for email in lista:
            with ui.card().classes('w-full'):
                with ui.row().classes('w-full items-start justify-between no-wrap'):
                    with ui.column().classes('gap-0'):
                        ui.label(email.assunto).classes('text-subtitle1 text-weight-medium')
                        ui.label(f'Para {email.para_nome} <{email.para_email}>').classes('text-body2 text-grey-8')
                    ui.label(_hora(email.criado_em)).classes('text-caption text-grey-7 text-right')
                ui.label(email.corpo).classes('text-body2')
                if email.link:
                    ui.button(email.rotulo_link or 'Abrir', icon='open_in_new',
                              on_click=lambda link=email.link: ui.navigate.to(link)).props('unelevated no-caps')  # fmt: skip
