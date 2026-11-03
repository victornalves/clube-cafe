"""Registro na B3: envio, consulta antes de reenviar, falha e resolução humana (maquina-de-estados.md, camada 2).

`RegistradoraB3` é o ponto de troca. Na Fase 3 entra a implementação real (mTLS, OAuth); nada acima muda.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.config import config
from app.domain import b3, prazos
from app.domain.b3 import RespostaB3
from app.domain.estados import Estado, Quem
from app.domain.models import CprNaB3Simulada, EnvioB3, Papel, Registro, SimuladorB3, Usuario
from app.services import envelopes, registros
from app.services.erros import ErroDeNegocio, exigir_papel
from app.services.registros import transicionar


class RegistradoraB3(Protocol):
    def registrar(self, payload: dict) -> RespostaB3: ...
    def consultar(self, chave: str) -> RespostaB3: ...


MODOS_SIMULADOR = {
    'sucesso': 'Sucesso: registra e devolve o número de controle',
    'instavel': 'Instável: 503 na primeira tentativa de cada registro, depois sucesso',
    'indisponivel': 'Fora do ar: 503 em toda tentativa',
    'registrou_sem_responder': 'Tempo esgotado (504), mas a B3 registrou: a consulta acha',
    'recusa': 'Recusa definitiva: 422, unidade de medida incompatível',
}


class B3Simulada:
    def __init__(self, s: Session):
        self.s = s

    def modo(self) -> str:
        simulador = self.s.get(SimuladorB3, 1)
        return simulador.modo if simulador else 'sucesso'

    def _gravar(self, chave: str) -> CprNaB3Simulada:
        agora = datetime.now(UTC)
        cpr = CprNaB3Simulada(chave=chave, numero_controle='', registrado_em=agora)
        self.s.add(cpr)
        self.s.flush()
        # Data + sequencial: único por construção, no formato numérico do Número de Controle
        cpr.numero_controle = f'{agora.astimezone():%Y%m%d}{cpr.id:08d}'
        return cpr

    def registrar(self, payload: dict) -> RespostaB3:
        chave = payload['codigo_contrato']
        modo = self.modo()
        if modo == 'instavel':
            anteriores = self.s.scalar(
                select(func.count())
                .select_from(EnvioB3)
                .join(Registro, Registro.id == EnvioB3.registro_id)
                .where(Registro.numero == chave, EnvioB3.operacao == 'envio')
            )
            modo = 'indisponivel' if anteriores == 0 else 'sucesso'
        if modo == 'indisponivel':
            return RespostaB3(503, {'mensagem': 'Serviço indisponível'})
        if modo == 'recusa':
            return RespostaB3(
                422, {'mensagem': 'Unidade de medida incompatível com o produto', 'campo': 'unidade_medida'}
            )
        if self.s.scalar(select(CprNaB3Simulada).where(CprNaB3Simulada.chave == chave)):
            return RespostaB3(409, {'mensagem': 'CPR já registrada com esta chave'})
        cpr = self._gravar(chave)
        if modo == 'registrou_sem_responder':
            return RespostaB3(504, {'mensagem': 'Tempo esgotado'})
        return RespostaB3(201, {'numero_controle': cpr.numero_controle})

    def consultar(self, chave: str) -> RespostaB3:
        cpr = self.s.scalar(select(CprNaB3Simulada).where(CprNaB3Simulada.chave == chave))
        if cpr is None:
            return RespostaB3(404, {'mensagem': 'CPR não encontrada'})
        return RespostaB3(200, {'numero_controle': cpr.numero_controle})


def registradora(s: Session) -> RegistradoraB3:
    return B3Simulada(s)


def emissao(registro: Registro) -> date | None:
    """Data impressa na CPR: abertura do envelope assinado (pendência: envio ou última assinatura?)."""
    envelope = envelopes.atual(registro)
    return envelope.aberto_em.astimezone().date() if envelope else None


def _log(s, registro, operacao, resposta: RespostaB3, *, automatico, autor, payload=None, resultado) -> EnvioB3:
    envio = EnvioB3(
        registro_id=registro.id,
        momento=datetime.now(UTC),
        operacao=operacao,
        automatico=automatico,
        usuario_id=autor.id if autor else None,
        status_http=resposta.status,
        resultado=resultado,
        mensagem=resposta.mensagem or resposta.corpo.get('numero_controle', ''),
        payload=payload,
        resposta=resposta.corpo,
    )
    s.add(envio)
    return envio


def _confirmar(s, registro: Registro, numero_controle: str):
    registro.numero_controle_b3 = numero_controle
    registro.registrado_em = datetime.now(UTC)
    transicionar(
        s, registro, 'confirmar_b3', Quem.SISTEMA, autor=None,
        descricao=f'Registro confirmado pela B3, sob o número {numero_controle}',
    )  # fmt: skip


def _processar(s: Session, registro: Registro, *, autor: Usuario | None, tentativas: int, consultar_antes: bool):
    """Envia; em erro transitório, consulta antes de reenviar, até esgotar as tentativas."""
    api = registradora(s)
    automatico = autor is None
    dados = b3.payload(registro, emissao(registro))
    for _ in range(tentativas):
        if consultar_antes:
            consulta = api.consultar(b3.chave(registro))
            achou = consulta.sucesso
            _log(s, registro, 'consulta', consulta, automatico=automatico, autor=autor,
                 resultado='encontrado' if achou else 'nao_encontrado')  # fmt: skip
            if achou:
                _confirmar(s, registro, consulta.corpo['numero_controle'])
                return
        resposta = api.registrar(dados)
        if resposta.sucesso:
            _log(s, registro, 'envio', resposta, automatico=automatico, autor=autor, payload=dados, resultado='sucesso')
            _confirmar(s, registro, resposta.corpo['numero_controle'])
            return
        transitorio = resposta.transitorio
        _log(s, registro, 'envio', resposta, automatico=automatico, autor=autor, payload=dados,
             resultado='transitorio' if transitorio else 'definitivo')  # fmt: skip
        if not transitorio:
            break
        consultar_antes = True

    transicionar(
        s, registro, 'falhar_b3', Quem.SISTEMA, autor=None,
        descricao=f'O registro na B3 falhou: {resposta.status} · {resposta.mensagem}',
        dados={'status': resposta.status, 'mensagem': resposta.mensagem},
    )  # fmt: skip


def processar_assinados(s: Session) -> int:
    """Job do sistema: tudo que ficou ASSINADO segue para a B3, com reenvio automático (T-05)."""
    assinados = s.scalars(select(Registro).where(Registro.estado == Estado.ASSINADO)).all()
    for registro in assinados:
        transicionar(s, registro, 'enviar_b3', Quem.SISTEMA, autor=None, descricao='Enviado para registro na B3')
        _processar(s, registro, autor=None, tentativas=config().tentativas_automaticas_b3, consultar_antes=False)
    return len(assinados)


# Ações do backoffice (telas 15 e 16)


def _do_backoffice(s: Session, operador: Usuario, registro_id: int, estado: Estado) -> Registro:
    exigir_papel(operador, Papel.OPERADOR)
    registro = registros.obter(s, operador, registro_id)
    if registro.estado != estado:
        raise ErroDeNegocio('Esta ação não está disponível na situação atual do registro.')
    return registro


def assumir(s: Session, operador: Usuario, registro_id: int) -> Registro:
    registro = _do_backoffice(s, operador, registro_id, Estado.FALHA_B3)
    registro.responsavel_id = operador.id
    transicionar(
        s, registro, 'assumir_correcao', Quem.OPERADOR, autor=operador, descricao=f'{operador.nome} assumiu a correção'
    )
    return registro


def reenviar(s: Session, operador: Usuario, registro_id: int) -> Registro:
    """Caminho 1: reenviar sem mudar nada, sempre consultando antes (T-06)."""
    registro = _do_backoffice(s, operador, registro_id, Estado.EM_CORRECAO)
    transicionar(
        s, registro, 'reenviar', Quem.OPERADOR, autor=operador, descricao=f'{operador.nome} pediu o reenvio à B3'
    )
    _processar(s, registro, autor=operador, tentativas=1, consultar_antes=True)
    return registro


def cancelar(s: Session, operador: Usuario, registro_id: int, motivo: str) -> Registro:
    """Caminho 4. O motivo é obrigatório e vai para o log."""
    if not (motivo or '').strip():
        raise ErroDeNegocio('Informe o motivo do cancelamento.')
    registro = _do_backoffice(s, operador, registro_id, Estado.EM_CORRECAO)
    transicionar(
        s, registro, 'cancelar_correcao', Quem.OPERADOR, autor=operador,
        descricao=f'Registro cancelado pelo backoffice. Motivo: {motivo.strip()}', dados={'motivo': motivo.strip()},
    )  # fmt: skip
    return registro


@dataclass
class Prazo:
    emissao: date
    limite: date
    dias_uteis_restantes: int


def prazo_legal(registro: Registro, hoje: date | None = None) -> Prazo | None:
    inicio = emissao(registro)
    if inicio is None:
        return None
    limite = prazos.limite_legal(inicio, config().prazo_legal_dias_uteis)
    return Prazo(inicio, limite, prazos.dias_uteis_entre(hoje or date.today(), limite))


@dataclass
class Pendencia:
    registro: Registro
    prazo: Prazo
    ultimo_envio: EnvioB3 | None
    tentativas: int


def envios(s: Session, operador: Usuario, registro_id: int) -> list[EnvioB3]:
    exigir_papel(operador, Papel.OPERADOR)
    registros.obter(s, operador, registro_id)
    return list(s.scalars(select(EnvioB3).where(EnvioB3.registro_id == registro_id).order_by(EnvioB3.id)))


def pendencias(s: Session, operador: Usuario) -> list[Pendencia]:
    """Fila da tela 15: falhas na B3, quem vence primeiro aparece primeiro."""
    exigir_papel(operador, Papel.OPERADOR)
    parados = s.scalars(
        select(Registro)
        .options(joinedload(Registro.vendedor), joinedload(Registro.responsavel))
        .where(Registro.estado.in_([Estado.FALHA_B3, Estado.EM_CORRECAO]))
    ).unique()
    fila = []
    for registro in parados:
        todos = s.scalars(select(EnvioB3).where(EnvioB3.registro_id == registro.id, EnvioB3.operacao == 'envio')).all()
        fila.append(Pendencia(registro, prazo_legal(registro), todos[-1] if todos else None, len(todos)))
    return sorted(fila, key=lambda p: p.prazo.limite)


def modo_simulador(s: Session) -> str:
    return B3Simulada(s).modo()


def definir_modo_simulador(s: Session, operador: Usuario, modo: str):
    exigir_papel(operador, Papel.OPERADOR)
    if modo not in MODOS_SIMULADOR:
        raise ErroDeNegocio('Modo desconhecido.')
    simulador = s.get(SimuladorB3, 1) or SimuladorB3(id=1)
    simulador.modo = modo
    s.add(simulador)
