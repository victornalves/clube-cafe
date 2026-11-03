# Clube do Café — Plano do MVP

**Revisão 1** · 03/11/2026 · complementa `plano-do-projeto.md` (rev. 4)

---

## Contexto

Em 03/11/2026 o cliente pediu para não acelerar: o trabalho continua **por hora, R$ 300/h**, sem proposta de escopo fechado por enquanto. Este plano cobre o passo seguinte dentro desse modelo, que é um **MVP simplificado e semi-descartável** para o cliente usar o fluxo de verdade, e não só navegar pelo mockup.

"Semi-descartável" tem um sentido preciso aqui. A interface pode ser jogada fora. O domínio fica: modelo de dados, máquina de estados, regras e checagem de acesso são escritos para servir à Fase 1 sem reescrita.

| Fica para a Fase 1 | Pode ser descartado |
|---|---|
| Modelo de dados e migrações | Telas NiceGUI |
| Máquina de estados, como tabela de transições | Layout e estilo |
| Regras de negócio e checagem de acesso, na camada de serviços | Simulações de assinatura e da B3 |
| Log de eventos | |
| Modelos de documento (contrato, CPR) | |

**Só dado fictício.** O MVP fica sem criptografia de aplicação e sem MFA (ver "Fora do MVP"), então nenhum dado real de membro entra nele.

---

## Stack

| Peça | Escolha | Por quê |
|---|---|---|
| Linguagem | Python 3.12 | |
| Interface | **NiceGUI**, com os componentes do Quasar | Já dominado. Tabela, stepper, formulário, diálogo e upload prontos. Todas as telas, inclusive o backoffice, são da aplicação, para ter controle total. Sem Django admin, sem sqladmin |
| Servidor HTTP | O FastAPI que vem dentro do NiceGUI | Webhooks de assinatura e da B3 entram depois como rotas comuns, no mesmo processo |
| Banco | PostgreSQL | O mesmo banco da Fase 1, para o modelo de dados não mudar de banco depois |
| ORM e migrações | SQLAlchemy 2 + Alembic | |
| Configuração | pydantic-settings, por variável de ambiente | Nenhum prazo fica constante no código (RN-99, RN-119) |
| Documento | Jinja2 + WeasyPrint, de HTML para PDF | Modelo editável em HTML, sem ferramenta proprietária |
| Senha | argon2 | |
| Tarefas em segundo plano | `app.timer` / `asyncio` do próprio NiceGUI | Expirar janela e simular o envio à B3. Sem Celery, sem Redis |
| Ferramentas | uv, ruff, pytest | |
| Hospedagem | Uma VPS pequena com Docker Compose e Caddy (HTTPS) | O NiceGUI guarda o estado da tela no servidor por websocket, então roda em uma instância só. Para a escala do clube, sobra |

### Cuidados com o NiceGUI neste projeto

1. **Conexão fraca no campo.** Se o websocket cai, o que estava só em memória se perde. Por isso cada etapa do registro grava o rascunho no banco ao avançar, e não só no final.
2. **Isolamento testável sem API REST.** Toda leitura e escrita passa pela camada `services/`, que recebe o usuário logado e filtra na origem. A UI nunca consulta o banco direto. Os testes de autorização (membro A pede o registro de B e não recebe nada) rodam contra essa camada.
3. **Certificado no navegador, mais adiante.** O Web PKI da Lacuna, se for o escolhido, é JavaScript no cliente. No NiceGUI isso entra por `ui.add_body_html` + `ui.run_javascript`. Não bloqueia o MVP, porque a assinatura aqui é simulada.

---

## Escopo

### Dentro

Recortado do mockup (`mockup/index.html`). Onde a tela entra simplificada, a coluna da direita diz como.

**Área do membro**

| Tela | Entra como |
|---|---|
| `03` Login | E-mail e senha. A conta é criada pelo backoffice, sem convite |
| `04` Meus registros | Lista com o estado simplificado (camada 1) |
| `05` / `05c` Partes | Uma tela só, com "seu papel": vendedor, comprador ou corretor. Contraparte buscada entre os membros cadastrados |
| `06` Objeto, preço e entrega | Produto, sacas, preço, região, armazém (lista fixa, sem cadastro), mês e ano de entrega, pagamento adiantado |
| `07` Revisão | Sem seguro de performance e sem o aceite prévio da contraparte (ver "Decisões tomadas") |
| `08`, `08b`, `08c` Envelope | Resumo, contrato em PDF e CPR em PDF. A CPR parte de `planejamento/CPR V.1.pdf`. O contrato é **simulado**: três parágrafos (apresentação das partes, objeto, conclusão), marcado como simulado no título e no rodapé |
| `09` / `09c` Assinatura | Botão "assinar (simulado)" para cada signatário: vendedor, comprador e, se houver, corretor como interveniente só no contrato. Janela configurável |
| `10` / `10b` Detalhe | Dados, estado e linha do tempo, montada a partir do log de eventos. Sem o bloco de ações de liquidação |
| `11` Minha conta | Só leitura |

**Backoffice**

| Tela | Entra como |
|---|---|
| Membros | **Tela nova, fora do mockup.** Lista e formulário para cadastrar membro (PF ou PJ, quem assina pela empresa). Substitui a proposta de adesão enquanto ela está fora |
| `14` Todos os registros | Lista com filtro por situação interna e por membro |
| `15` Fila de pendências | Ordenada pelo prazo legal de 30 dias úteis |
| `16` Resolução de falha | Dois dos quatro caminhos: **reenviar** (com consulta antes, `16a`) e **cancelar** (`16d`) |
| `17` Auditoria | Log de eventos, filtrável por registro e por pessoa |
| Simulador da B3 | **Tela nova, só para demonstração.** Escolhe o que a B3 simulada vai responder no próximo envio: sucesso, 503 ou 422 |

**Estados do registro**

Subconjunto da camada 2 de `maquina-de-estados.md` (rev. 3), implementado como tabela de transições, não como `if` espalhado:

```
RASCUNHO ──► PRE_VALIDANDO ──► AGUARDANDO_ASSINATURAS ──► ASSINADO ──► ENVIANDO_B3 ──► REGISTRADO
   ▲              │                    │                                   │
   └── falhou ────┘                    ├─► JANELA_EXPIRADA ─► reabrir      └─► FALHA_B3 ─► EM_CORRECAO
                                       │          └──────────► CANCELADO              ├─► reenviar ─► ENVIANDO_B3
   RASCUNHO ─► CANCELADO               └─► CANCELADO (ninguém assinou)                └─► cancelar ─► CANCELADO
```

Fica de fora `RECUSADO_POR_PARTE` (no MVP, quem não quer assinar só não assina) e `AGUARDANDO_REASSINATURA`. A pré-validação confere obrigatoriedade, formato e tamanho dos campos do `estudo-api-b3.md` §2, localmente, sem chamar a B3. Os domínios fechados (produto, safra, unidade, acondicionamento) vêm de arquivos da B3 que ainda não temos. Até lá, ficam numa lista provisória, em tabela, para trocar sem mexer no código.

### Fora do MVP

| Bloco | Telas | Por quê |
|---|---|---|
| Landing | `01` | Ninguém entra sem conta nesta fase |
| Proposta de adesão e comitê | `02`, `02b`, `02c`, `12`, `12b`, `12c`, `13` | Bloco grande e com pendências abertas (1.27, 1.28, 1.43). O backoffice cadastra o membro direto |
| Termos do clube | `03b` | Pendência 1.43. Entra como flag "aceitou os termos" no cadastro, marcada pelo backoffice |
| Mesa de Negociação | `05b`, `06b`, `07b`, `09-assinatura-mesa*` | Serviço de terceiro, ainda sem provedor escolhido |
| Assinatura real com certificado | `09a`, `09b` | Fase 2. A simulação implementa a mesma interface que o fornecedor real vai implementar |
| Correção de payload e reassinatura | `16b`, `16c` | Os dois caminhos mais raros. Reenviar e cancelar cobrem a demonstração |
| Armazéns, árbitros, amostras | `18`, `18b`, `19`, `20`, `25`, `25b` | Fase 4. O armazém vira uma lista fixa no formulário |
| Limite de negociação | `21`, `21b`, `22`, `22b` | Pendências abertas |
| Liquidação e pós-registro | `23`, `24`, `26` a `31` | Pendências 1.69 a 1.71, ainda sem resposta |
| Segurança completa | — | Criptografia de aplicação, MFA no backoffice, log de acessos e exportação controlada. Por isso, só dado fictício |

---

## Arquitetura

```
clube-cafe/
├── app/
│   ├── main.py              # ui.run, tema, registro das páginas
│   ├── config.py            # prazos, janela, tentativas: tudo por variável de ambiente
│   ├── db.py
│   ├── domain/              # FICA
│   │   ├── models.py        # Membro, Registro, Parte, Envelope, Assinatura, Evento, EnvioB3
│   │   ├── estados.py       # tabela de transições + mapeamento interno → o que o membro vê
│   │   ├── prevalidacao.py
│   │   └── prazos.py        # dias úteis, prazo legal de 30 dias úteis
│   ├── services/            # FICA: todo caso de uso recebe o usuário e checa acesso
│   │   ├── membros.py
│   │   ├── registros.py
│   │   ├── documentos.py    # Jinja + WeasyPrint
│   │   ├── assinatura.py    # interface ProvedorAssinatura + simulação
│   │   ├── b3.py            # interface RegistradoraB3 + simulação
│   │   └── eventos.py       # log de eventos, append-only
│   ├── ui/                  # DESCARTÁVEL
│   │   ├── tema.py          # cores, cabeçalho, layout base
│   │   ├── componentes.py   # cartão de registro, selo de estado, linha do tempo
│   │   ├── membro/
│   │   └── backoffice/
│   └── templates/           # contrato.html, cpr.html
├── migrations/              # Alembic
├── tests/
│   ├── test_isolamento.py
│   ├── test_estados.py
│   └── test_prevalidacao.py
├── docker-compose.yml       # app + postgres + caddy
└── pyproject.toml
```

As duas interfaces, `ProvedorAssinatura` e `RegistradoraB3`, são o ponto de troca. Na Fase 2 entra uma implementação Clicksign ou Lacuna; na Fase 3, a B3 real. Nada acima de `services/` muda.

**Simplificação consciente:** a simulação de assinatura cobre só o modo embutido. O modo redirecionado, que a estratégia do `plano-do-projeto.md` pede para a Fase 1, fica para quando o fornecedor for escolhido.

---

## Visual

Sem design elaborado. Componentes padrão do Quasar com as cores da logo aplicadas como tema, e nada além disso. A direção "Cartório" do `estudo-ui-identidade.md` continua valendo para depois.

| Papel | Cor | Origem na logo |
|---|---|---|
| `primary` | `#3F5B2E` | Verde da folha e do nome |
| `secondary` | `#6B4423` | Marrom do grão |
| `accent` | `#A8743A` | Caramelo da folha |
| `dark` | `#2E2A24` | Texto |
| Fundo | `#FAF8F3` | Off-white |

Valores estimados a partir da imagem da logo e aprovados por Victor em 03/11/2026. Fonte serifada (Cormorant Garamond, por exemplo) só no nome do clube no cabeçalho; o resto fica com a fonte padrão do Quasar.

---

## Entregas e horas

Três marcos, cada um com demonstração para o cliente. Como o trabalho é por hora, o cliente pode parar em qualquer marco e ainda fica com algo que funciona.

### Marco 1 — Esqueleto e registro em rascunho

| Item | Horas |
|---|---|
| Projeto, banco, migrações, tema, layout base, deploy local | 6–8 |
| Login, sessão, papéis membro e backoffice | 3–4 |
| Modelo de dados, tabela de transições, log de eventos, testes | 6–8 |
| Backoffice: cadastro de membros | 3–4 |
| Registro em três etapas (partes, objeto, revisão), rascunho gravado a cada etapa | 10–13 |
| Meus registros e minha conta | 2–3 |
| **Subtotal** | **30–40** |

**Demonstração:** o membro entra, cria um registro com um colega, salva, sai e volta para continuar de onde parou.

### Marco 2 — Envelope e assinatura simulada

| Item | Horas |
|---|---|
| Pré-validação de formato e de lista provisória de domínios | 3–4 |
| Modelos de contrato e CPR em HTML, geração de PDF | 7–9 |
| Envelope, assinatura simulada por signatário, janela configurável e expiração | 5–7 |
| Detalhe do registro com linha do tempo | 3–4 |
| **Subtotal** | **18–24** |

**Demonstração:** registro sai do rascunho, gera contrato e CPR, cada parte assina na própria conta, e a janela expira se alguém demorar.

### Marco 3 — B3 simulada e backoffice

| Item | Horas |
|---|---|
| B3 simulada: envio, reenvio automático até N vezes, consulta antes de reenviar, simulador | 4–6 |
| Todos os registros, fila de pendências por prazo legal, resolução com reenviar e cancelar | 9–11 |
| Auditoria | 2–3 |
| Testes de isolamento entre membros | 3–4 |
| Deploy na VPS, HTTPS, dados de demonstração | 4–5 |
| **Subtotal** | **22–29** |

**Demonstração:** o operador força uma falha 422 no simulador, o registro aparece na fila com o prazo correndo, e é resolvido por reenvio.

### Total

| | Horas | R$ 300/h |
|---|---|---|
| Marcos 1 a 3 | 70–93 | R$ 21.000–27.900 |
| Ajustes depois das demonstrações | 6–10 | R$ 1.800–3.000 |
| **Total** | **76–103** | **R$ 22.800–30.900** |

Esse total não se soma à Fase 1 do `plano-do-projeto.md`, que continua sendo a referência do sistema completo. O que fica do MVP (domínio, serviços, modelos de documento, testes) reduz a Fase 1 quando ela for contratada. A redução só vai ser estimada depois do Marco 3.

Custo recorrente: VPS de US$ 6–12/mês e um domínio. Assinatura e B3 simuladas não custam nada.

---

## Decisões tomadas

| Decisão | Motivo |
|---|---|
| NiceGUI para todas as telas, inclusive o backoffice | Controle total da interface, decidido por Victor em 03/11/2026. Nada de Django admin ou sqladmin |
| PostgreSQL desde o início, e não SQLite | O modelo de dados é parte do que fica |
| Sem aceite prévio da contraparte, o estado "em negociação" das telas `04` e `07` | No MVP, assinar é aceitar. Volta quando a Mesa entrar |
| Membro cadastrado pelo backoffice, sem proposta de adesão | Corta o maior bloco com pendência aberta |
| Só dado fictício | Sem criptografia de aplicação nem MFA nesta fase |
| Contrato de compra e venda simulado, com três parágrafos | Ainda não há modelo do escritório. Decidido por Victor em 03/11/2026 |
| Cores da tabela "Visual" | Aprovadas por Victor em 03/11/2026 |
| Assinatura simulada só no modo embutido | Aprovado por Victor em 03/11/2026 |

## Para começar

1. ~~Conferir as cores~~ Aprovadas.
2. ~~Modelo de contrato~~ Simulado, em `app/templates/contrato.html`.
3. Ler `planejamento/CPR V.1.pdf` e transformar o texto em `app/templates/cpr.html` (Marco 2).
4. Marco 1, em andamento desde 03/11/2026. Como rodar: `README.md` na raiz.

### Andamento do Marco 1

| Item | Situação |
|---|---|
| Projeto, banco, migrações, tema, layout base | Feito, 03/11 |
| Login, sessão, papéis membro e backoffice | Feito, 03/11 |
| Modelo de dados, tabela de transições, log de eventos, testes | Feito, 03/11 |
| Backoffice: cadastro de membros | Feito, 03/11 |
| Registro em três etapas, rascunho gravado a cada etapa | Feito, 03/11 |
| Meus registros e minha conta | Feito, 03/11 |
| Deploy local | Pendente. Hoje roda com `uv run`; a imagem Docker do app entra com o deploy do Marco 3 |

Decisões de implementação deste marco:

- **Rascunho é só do autor.** As outras partes passam a ver o registro quando o envelope chega até elas (`enviado_as_partes_em`). Um rascunho descartado nunca aparece para elas.
- **Os CPFs e o CNPJ do mockup não têm dígito verificador válido.** Os dados de demonstração usam os mesmos números com os dois últimos dígitos corrigidos.
- **O servidor escuta só em `127.0.0.1` por padrão** (`CLUBE_HOST`). O padrão do NiceGUI é escutar em todas as interfaces, inclusive IP público.
