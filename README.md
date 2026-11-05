# Clube do Café (nome provisório) / CRTC

Plataforma de formalização, assinatura e registro de contratos de café, para **membros** de um clube fechado.
Consultoria: VSTech Consulting · Victor Alves

**Estágio atual:** Fase 0. A reunião de validação com o cliente aconteceu em 24/09/2026 e mudou o modelo de entrada, de assinatura e trouxe escopo novo (armazéns, árbitros, amostras, vídeo). Documentos atualizados para a **revisão 5** em 01/10/2026 — ver [consolidacao-rev5.md](docs/consolidacao-rev5.md) e a ata em [planejamento/atas-reunioes-wado.md](planejamento/atas-reunioes-wado.md). Próximo passo: ampliar o mockup para cobrir o escopo novo e enviar as pendências que a reunião abriu. Ver [plano-do-projeto.md](docs/plano-do-projeto.md), seção "Onde estamos".

---

## MVP

Plano e escopo em [plano-mvp.md](docs/plano-mvp.md). Python 3.12, NiceGUI, PostgreSQL, SQLAlchemy + Alembic, gerenciado com `uv`. **Só dado fictício.**

```bash
brew install pango                   # biblioteca de sistema do WeasyPrint, que gera os PDFs
docker compose up -d                 # Postgres na porta 5450 (cria também o banco de teste)
cp .env.example .env                 # opcional: os padrões já servem para desenvolvimento
uv run alembic upgrade head
uv run python -m scripts.seed        # usuários de demonstração, senha cafe123
uv run python -m scripts.demo --apagar-tudo   # zera o banco e monta os cenários de demonstração
uv run python -m app.main            # http://localhost:8350
uv run pytest
```

| Usuário de demonstração | Papel |
|---|---|
| `jose@membro.demo` | Membro, produtor PF |
| `rodrigo@membro.demo` | Membro, comprador PJ (Tostado Brasil) |
| `marta@membro.demo` | Membro, produtora PF |
| `rogerio@membro.demo` | Membro, corretor |
| `helena@membro.demo` | Membro, Cooperativa Agrária do Sul de Minas (PJ, vendedora) |
| `claudia.ferraz@membro.demo` | Membro, Exportadora Monte Verde (PJ, compradora) |
| `paulo@membro.demo` | Membro, Café Aurora Exportação (PJ, compradora) |
| `claudia@backoffice.demo` | Backoffice, operadora |

### Roteiro de demonstração

`scripts.demo` monta um registro em cada situação. Rodar logo antes de apresentar, porque a janela de assinatura começa a contar na hora; para uma reunião, `CLUBE_JANELA_ASSINATURA_MINUTOS=60` no `.env`.

| Registro | Situação | Para mostrar |
|---|---|---|
| CRTC-2026-0001 | Registrado, com corretor | Fluxo feliz completo, PDFs, número de controle |
| CRTC-2026-0002 | Registrado depois de recusa 422 | Backoffice: comunicação com a B3, consulta antes do reenvio |
| CRTC-2026-0003 | Falha 422, emitido há 5 semanas | Pendências: prazo legal vermelho, assumir e resolver ao vivo |
| CRTC-2026-0004 | B3 fora do ar, já assumido | Pendências: 3 tentativas automáticas, responsável |
| CRTC-2026-0005 | Janela expirada | Helena reabre ou cancela |
| CRTC-2026-0006 | Rascunho pela metade | José continua de onde parou |
| CRTC-2026-0007 | Rascunho pronto | Marta gera o envelope e a pré-validação barra: falta matrícula |
| PROP-2026-0001 | Proposta pronta para o comitê | Relatório para a reunião, registrar a decisão, e o aprovado cria a senha e assina os termos pela caixa de e-mails |
| PROP-2026-0002 | Proposta aguardando assinatura | O proponente de fora da Câmara assina pelo link, na caixa de e-mails |
| PROP-2026-0003 | Proposta em diligência | A candidata responde pelo link e a proposta volta à fila |
| CRTC-2026-0008 | Aguardando assinaturas | Rogério (corretor) criou, José assinou; Rodrigo e Rogério assinam ao vivo, e o registro segue para a B3 |

O código separa `app/domain` e `app/services`, que ficam para a Fase 1, de `app/ui`, que é descartável.

---

## Documentação

### Principais

| Documento | O que responde |
|---|---|
| [entendimento-do-projeto.md](docs/entendimento-do-projeto.md) | O que é o sistema, escopo, riscos. Rev. 5 |
| [maquina-de-estados.md](docs/maquina-de-estados.md) | Estados, transições, prazo legal, alertas, caminhos de resolução, máquina da proposta de adesão. Rev. 3 |
| [regras-de-negocio.md](docs/regras-de-negocio.md) | Regras com identificador, matriz de papéis, lacunas, novo bloco de armazéns/árbitros/amostras |
| [arquitetura-seguranca.md](docs/arquitetura-seguranca.md) | Ameaças, credenciais, fornecedor como superfície de dado, LGPD. Rev. 2, ainda não revisada para o escopo novo |
| [plano-do-projeto.md](docs/plano-do-projeto.md) | Onde estamos, fases, horas, escolha de fornecedor, nota comercial, Fase 4 (escopo novo). Rev. 4 |
| [pendencias.md](docs/pendencias.md) | **Perguntas abertas, agrupadas por quem responde.** Rev. 5 |
| [pauta-reuniao-validacao.md](docs/pauta-reuniao-validacao.md) | Pauta da reunião de 24/09 — já realizada, fica como registro |

Ler nessa ordem na primeira vez.

### Estudos e registro

| Documento | Conteúdo |
|---|---|
| [planejamento/atas-reunioes-wado.md](planejamento/atas-reunioes-wado.md) | Ata limpa das reuniões 1 e 2 com o cliente, organizada por tema |
| [consolidacao-rev4.md](docs/consolidacao-rev4.md) | O que os estudos das seis frentes mudaram, contradição por contradição, com fonte |
| [consolidacao-rev5.md](docs/consolidacao-rev5.md) | O que a reunião de 24/09 mudou, e por quê |
| [estudo-api-b3.md](docs/estudo-api-b3.md) | Autenticação mTLS, payload de CPR, erros, reconciliação, Fase 3 |
| [estudo-assinatura-panorama.md](docs/estudo-assinatura-panorama.md) | Tipos de certificado, lei, mercado. Parcialmente superado pelos dois abaixo |
| [estudo-assinatura-api-clicksign.md](docs/estudo-assinatura-api-clicksign.md) | Clicksign: fluxo, webhook, guarda, preço, Fase 2 |
| [estudo-assinatura-api-lacuna.md](docs/estudo-assinatura-api-lacuna.md) | Lacuna: rotas, Web PKI, prova de longo prazo, preço, Fase 2 |
| [estudo-assinatura-sem-certificado.md](docs/estudo-assinatura-sem-certificado.md) | Validação: assinatura por e-mail na Clicksign, lei, garantia real, impacto |
| [estudo-ui-identidade.md](docs/estudo-ui-identidade.md) | Três direções visuais |
| [frentes-de-trabalho.md](docs/frentes-de-trabalho.md) | Briefing original das seis frentes |
| [diagramas/](docs/diagramas/) | Um único arquivo draw.io, com 10 páginas (abas): A entrada e limites, B registro, C liquidação e armazém, D papéis. Rev. 2, atualizado com a reunião 3 |
| [mockup/](mockup/) | Telas navegáveis, com roteiro. Ampliado em 01/10 para cobrir o escopo novo |

---

## Decisões já fechadas

- Escopo inicial é **só café**, e é **CPR física** — não a financeira que o escritório avaliou por engano a princípio.
- Termo oficial é **"membro"**, nunca "sócio".
- Entrada é por **proposta de adesão**: proponente + 2 recomendantes assinam; comitê de admissão avalia, provavelmente fora do sistema; backoffice materializa a decisão.
- **Sem bloqueio automático** de quem foi recusado: pode propor de novo quando quiser.
- Acesso à B3 **aprovado**, via conta do escritório de advocacia sócio, com pacote de acesso mTLS.
- ~~Assinatura ICP-Brasil~~ **Em reavaliação:** assinatura por e-mail, sem certificado, para CPR sem garantia real. Validada juridicamente com condições em [estudo-assinatura-sem-certificado.md](docs/estudo-assinatura-sem-certificado.md).
- Assinatura é de um **envelope único** (contrato + CPR + outros), numa janela curta e configurável (15 minutos de partida).
- O membro vê cinco estados. O backoffice vê a máquina completa.
- Falha de registro tem **human in the loop**, com uma **pré-validação antes da assinatura** para reduzir o caso mais comum de falha.
- Retorno da B3 por **consulta**, nunca reenvio cego.
- Fila de pendências ordenada por **prazo legal restante**.
- Nada de blockchain. Banco relacional comum.
- Aditamento de CPR registrada fica **fora do MVP**.
- Escopo novo (armazéns, árbitros, amostras, vídeo) entra no **mockup** para validação completa, mas é **precificado em módulos separados**, não no núcleo.

## As seis perguntas que mais mudam o projeto

1. Que certificado os membros têm hoje.
2. Se o emitente pode ser pessoa jurídica.
3. ~~Se a contraparte precisa ser membro.~~ **Respondida em 24/09/2026:** todas as partes que assinam são membros.
4. Se a data de emissão é o envio ou a última assinatura (escritório).
5. Se o contrato pode ficar guardado no fornecedor de assinatura.
6. Se o comitê de admissão precisa de conta própria no sistema, ou só relatório + decisão materializada pelo backoffice.

Lista completa em [pendencias.md](docs/pendencias.md).

---

`planejamento/kickoff-md` é de outro projeto (Labeee/FEESC, UFSC) e precisa sair daqui.
