# Clube do Café (nome provisório) / CRTC

Plataforma de formalização, assinatura e registro de contratos de café.
Consultoria: VSTech Consulting · Victor Alves

**Estágio atual:** Fase 0, validação de escopo. Seis frentes de estudo rodando em paralelo, ver [frentes-de-trabalho.md](docs/frentes-de-trabalho.md).

---

## Documentação

| Documento | O que responde |
|---|---|
| [entendimento-do-projeto.md](docs/entendimento-do-projeto.md) | O que é o sistema, o que está dentro e fora, o que ainda trava o escopo |
| [maquina-de-estados.md](docs/maquina-de-estados.md) | Ciclo de vida do registro, as duas camadas, e como o backoffice resolve falhas |
| [arquitetura-seguranca.md](docs/arquitetura-seguranca.md) | Modelo de ameaça, classificação de dados, controles e LGPD |
| [plano-do-projeto.md](docs/plano-do-projeto.md) | Fases, horas, telas do mockup, escolha de parceiro, nota comercial |
| [frentes-de-trabalho.md](docs/frentes-de-trabalho.md) | As seis frentes de estudo em andamento, com briefing para cada sessão |

Ler nessa ordem na primeira vez.

---

## Decisões já fechadas

- Escopo inicial é **só café**.
- Homologação B3 **resolvida**, via conta do escritório de advocacia sócio.
- Assinatura é **ICP-Brasil**.
- O membro vê estados simplificados. O backoffice vê a máquina completa.
- Falha de registro tem **human in the loop** obrigatório.
- Nada de blockchain. Banco relacional comum.

## Abertas

- Que certificado ICP os membros já usam (nuvem ou token físico).
- Se quem assina precisa ser membro do clube.
- Quantos modelos de documento entram no preço fechado.
- Campos reais do cadastro.

---

`planejamento/kickoff-md` é de outro projeto (Labeee/FEESC, UFSC) e precisa sair daqui.
