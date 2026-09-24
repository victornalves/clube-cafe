# Clube do Café (nome provisório) / CRTC

Plataforma de formalização, assinatura e registro de contratos de café.
Consultoria: VSTech Consulting · Victor Alves

**Estágio atual:** Fase 0. As seis frentes de estudo terminaram e foram consolidadas na **revisão 4**. Mockup e diagramas atualizados. Próximo passo: disparar as pendências externas e fazer a reunião de validação ([pauta](docs/pauta-reuniao-validacao.md)). Ver [plano-do-projeto.md](docs/plano-do-projeto.md), seção "Onde estamos".

---

## Documentação

### Principais

| Documento | O que responde |
|---|---|
| [entendimento-do-projeto.md](docs/entendimento-do-projeto.md) | O que é o sistema, escopo, riscos. Rev. 4 |
| [maquina-de-estados.md](docs/maquina-de-estados.md) | Estados, transições, prazo legal, alertas, caminhos de resolução. Rev. 2 |
| [regras-de-negocio.md](docs/regras-de-negocio.md) | 100 regras com identificador, matriz de papéis, lacunas |
| [arquitetura-seguranca.md](docs/arquitetura-seguranca.md) | Ameaças, credenciais, fornecedor como superfície de dado, LGPD. Rev. 2 |
| [plano-do-projeto.md](docs/plano-do-projeto.md) | Onde estamos, fases, horas, escolha de fornecedor, nota comercial. Rev. 3 |
| [pendencias.md](docs/pendencias.md) | **70 perguntas abertas, agrupadas por quem responde** |
| [pauta-reuniao-validacao.md](docs/pauta-reuniao-validacao.md) | Estrutura e objetivos da próxima reunião com o cliente |

Ler nessa ordem na primeira vez.

### Estudos e registro

| Documento | Conteúdo |
|---|---|
| [consolidacao-rev4.md](docs/consolidacao-rev4.md) | O que os estudos mudaram, contradição por contradição, com fonte |
| [estudo-api-b3.md](docs/estudo-api-b3.md) | Autenticação mTLS, payload de CPR, erros, reconciliação, Fase 3 |
| [estudo-assinatura-panorama.md](docs/estudo-assinatura-panorama.md) | Tipos de certificado, lei, mercado. Parcialmente superado pelos dois abaixo |
| [estudo-assinatura-api-clicksign.md](docs/estudo-assinatura-api-clicksign.md) | Clicksign: fluxo, webhook, guarda, preço, Fase 2 |
| [estudo-assinatura-api-lacuna.md](docs/estudo-assinatura-api-lacuna.md) | Lacuna: rotas, Web PKI, prova de longo prazo, preço, Fase 2 |
| [estudo-assinatura-sem-certificado.md](docs/estudo-assinatura-sem-certificado.md) | Validação: assinatura por e-mail na Clicksign, lei, garantia real, impacto |
| [estudo-ui-identidade.md](docs/estudo-ui-identidade.md) | Três direções visuais |
| [frentes-de-trabalho.md](docs/frentes-de-trabalho.md) | Briefing original das seis frentes |
| [diagramas/](docs/diagramas/) | Cinco diagramas draw.io. 02, 03 e 04 mostram a máquina de estados rev. 2 |
| [mockup/](mockup/) | 17 telas principais e 8 auxiliares, navegáveis, com roteiro |

---

## Decisões já fechadas

- Escopo inicial é **só café**.
- Acesso à B3 **aprovado**, via conta do escritório de advocacia sócio, com pacote de acesso mTLS.
- ~~Assinatura ICP-Brasil~~ **Em reavaliação:** assinatura por e-mail, sem certificado, para CPR sem garantia real. Validada juridicamente com condições em [estudo-assinatura-sem-certificado.md](docs/estudo-assinatura-sem-certificado.md).
- O membro vê cinco estados. O backoffice vê a máquina completa.
- Falha de registro tem **human in the loop**.
- Retorno da B3 por **consulta**, nunca reenvio cego.
- Fila de pendências ordenada por **prazo legal restante**.
- Nada de blockchain. Banco relacional comum.
- Aditamento de CPR registrada fica **fora do MVP**.

## As cinco perguntas que mais mudam o projeto

1. Que certificado os membros têm hoje.
2. Se o emitente pode ser pessoa jurídica.
3. Se a contraparte precisa ser membro.
4. Se a data de emissão é o envio ou a última assinatura (escritório).
5. Se o contrato pode ficar guardado no fornecedor de assinatura.

Lista completa em [pendencias.md](docs/pendencias.md).

---

`planejamento/kickoff-md` é de outro projeto (Labeee/FEESC, UFSC) e precisa sair daqui.
