"""Zera o banco e monta os cenários de demonstração, um por situação do registro.

    uv run python -m scripts.demo --apagar-tudo

Rodar logo antes de apresentar: o envelope que aguarda assinatura usa a janela configurada
(CLUBE_JANELA_ASSINATURA_MINUTOS; para uma reunião, 60 é mais confortável que 15).
Tudo passa pelos serviços, então a linha do tempo e a auditoria saem como num uso real.
"""

import argparse
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, text

from app.config import config
from app.db import engine, sessao
from app.domain.models import Base, PapelNoRegistro, Registro, Usuario
from app.services import b3, envelopes, registros
from app.services.registros import DadosObjeto, DadosPartes
from scripts import seed

V, C, CO = PapelNoRegistro.VENDEDOR, PapelNoRegistro.COMPRADOR, PapelNoRegistro.CORRETOR
ANO = datetime.now().year + 1

# Tabelas que ficam: a lista provisória de domínios da B3 vem da migração
PRESERVAR = {'dominio_b3', 'alembic_version'}


def zerar():
    tabelas = [t.name for t in Base.metadata.sorted_tables if t.name not in PRESERVAR]
    with engine.begin() as conexao:
        # TRUNCATE não dispara a trigger append-only do log, que é por linha (UPDATE/DELETE)
        conexao.execute(text(f'TRUNCATE {", ".join(tabelas)} RESTART IDENTITY CASCADE'))


class Cenario:
    def __init__(self, s):
        self.s = s
        self.u = {u.email.split('@')[0]: u for u in s.scalars(select(Usuario))}
        self.operador = self.u['claudia']

    def membro(self, apelido: str) -> int:
        return self.u[apelido].membro.id

    def rascunho(self, autor, papel, vendedor, comprador, corretor=None, **objeto) -> Registro:
        r = registros.criar_rascunho(
            self.s,
            self.u[autor],
            DadosPartes(
                papel, self.membro(vendedor), self.membro(comprador), self.membro(corretor) if corretor else None
            ),
        )
        if objeto:
            registros.salvar_objeto(self.s, self.u[autor], r.id, DadosObjeto(**objeto))
        return r

    def objeto(self, sacas, preco, regiao, armazem, mes, ano=ANO, adiantado=False) -> dict:
        return dict(
            produto='arabica',
            sacas=sacas,
            preco_saca=Decimal(preco),
            regiao=regiao,
            armazem=armazem,
            entrega_mes=mes,
            entrega_ano=ano,
            pagamento_adiantado=adiantado,
        )

    def envelope(self, r: Registro, autor: str, *assinam: str):
        erros = envelopes.gerar_envelope(self.s, self.u[autor], r.id)
        assert not erros, erros
        for quem in assinam:
            envelopes.assinar(self.s, self.u[quem], r.id)

    def emitido_ha(self, r: Registro, dias: int):
        """Recua a emissão, para a fila de pendências mostrar prazos diferentes."""
        envelopes.atual(r).aberto_em -= timedelta(days=dias)

    def b3(self, modo: str):
        b3.definir_modo_simulador(self.s, self.operador, modo)
        b3.processar_assinados(self.s)


def montar():
    with sessao() as s:
        c = Cenario(s)
        sul = ('Sul de Minas', 'Armazéns Gerais Varginha')
        tres_pontas = ('Sul de Minas', 'Armazéns Gerais Três Pontas')

        # 1. Registrado, com corretor
        r = c.rascunho('jose', V, 'jose', 'claudia.ferraz', 'rogerio', **c.objeto(600, '1610', *sul, 9))
        c.envelope(r, 'jose', 'jose', 'claudia.ferraz', 'rogerio')
        c.b3('sucesso')

        # 2. Registrado depois de uma recusa 422, resolvido pelo backoffice
        r = c.rascunho('helena', V, 'helena', 'paulo', **c.objeto(1300, '1500', *tres_pontas, 7))
        c.envelope(r, 'helena', 'helena', 'paulo')
        c.b3('recusa')
        b3.assumir(s, c.operador, r.id)
        b3.definir_modo_simulador(s, c.operador, 'sucesso')
        b3.reenviar(s, c.operador, r.id)

        # 3. Pendência urgente: 422, emitida há 5 semanas, ninguém assumiu
        r = c.rascunho('jose', V, 'jose', 'rodrigo', **c.objeto(1200, '1480', *sul, 5))
        c.envelope(r, 'jose', 'jose', 'rodrigo')
        c.emitido_ha(r, 39)
        c.b3('recusa')

        # 4. Pendência com prazo folgado: B3 fora do ar, 3 tentativas, já assumida
        r = c.rascunho('helena', V, 'helena', 'rodrigo', 'rogerio', **c.objeto(800, '1520', *sul, 3))
        c.envelope(r, 'helena', 'helena', 'rodrigo', 'rogerio')
        c.emitido_ha(r, 6)
        c.b3('indisponivel')
        b3.assumir(s, c.operador, r.id)

        # 5. Janela expirada: só a cooperativa assinou
        r = c.rascunho('helena', V, 'helena', 'claudia.ferraz', **c.objeto(450, '1550', *tres_pontas, 8))
        c.envelope(r, 'helena', 'helena')
        envelopes.atual(r).expira_em = datetime.now(UTC) - timedelta(minutes=1)
        envelopes.expirar_vencidos(s)

        # 6. Rascunho pela metade: partes escolhidas, objeto em branco
        c.rascunho('jose', V, 'jose', 'paulo')

        # 7. Rascunho pronto que vai barrar na pré-validação: Marta não tem matrícula no cadastro
        c.rascunho(
            'marta', V, 'marta', 'rodrigo', **c.objeto(750, '1490', 'Cerrado Mineiro', 'Armazém Geral Patrocínio', 3)
        )

        # 8. Aguardando assinaturas, por último, para a janela começar a contar agora.
        #    José já assinou; Rodrigo (Tostado) e Rogério (corretor) assinam ao vivo
        r = c.rascunho('rogerio', CO, 'jose', 'rodrigo', 'rogerio', **c.objeto(2000, '1395', *sul, 12, ANO - 1))
        c.envelope(r, 'rogerio', 'jose')

        b3.definir_modo_simulador(s, c.operador, 'sucesso')


def resumo():
    with sessao() as s:
        for r in s.scalars(select(Registro).order_by(Registro.id)):
            print(f'  {r.numero}  {r.estado.value:<24} {r.vendedor.nome} → {r.comprador.nome}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--apagar-tudo', action='store_true', help='confirma que todos os dados do banco serão apagados'
    )
    args = parser.parse_args()
    if not args.apagar_tudo:
        parser.error(f'isto apaga todos os dados de {engine.url.render_as_string(hide_password=True)}. '
                     'Repita com --apagar-tudo para confirmar.')  # fmt: skip
    zerar()
    seed.main()
    montar()
    print(f'Cenários montados (janela de assinatura: {config().janela_assinatura_minutos} min):')
    resumo()


if __name__ == '__main__':
    main()
