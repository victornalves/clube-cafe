# Máquina de Estados do Registro

**Revisão 3** · 01/10/2026 · complementa `entendimento-do-projeto.md` (rev. 5)

A rev. 1 e a rev. 2 continuam valendo. A rev. 3 aplica o que a reunião de 24/09/2026 com o cliente mudou (`planejamento/atas-reunioes-wado.md`): assinatura em **envelope único** com janela curta, uma **pré-validação** antes de abrir essa janela, e a **proposta de adesão** virou uma máquina de estados própria, separada da de registro. Ver `regras-de-negocio.md` §1 e §3.3.1.

**Mudança de princípio desta revisão:** a rev. 2 tratava falha na B3 como algo a corrigir depois, com `EM_CORRECAO` e quatro caminhos. O cliente chamou isso de **"erro grave"**: o contrato já foi assinado pelas partes, e ele não pode ficar sem efeito por um problema técnico nosso. A rev. 3 não elimina `EM_CORRECAO` — falha pode sempre acontecer do lado da B3 — mas acrescenta uma barreira **antes** da assinatura, para que o caso mais comum de falha (payload com dado fora do domínio, formato errado) nunca chegue a ser assinado.

**Tudo marcado _Proposta_ espera aceite do cliente ou do escritório.** Os diagramas das páginas B3 e B4 de `diagramas/Clube do Café - Diagramas - rev 2.drawio` já foram redesenhados (rev. 3 e reunião 3 de 01/10/2026); o registro está em `consolidacao-rev5.md`.

---

## O princípio

Duas camadas. O membro vê uma versão simplificada. O backoffice vê tudo.

E dois relógios: o **prazo legal**, que é do membro e da lei, e os **prazos operacionais**, que são do backoffice.

---

## Camada 1 — o que o membro vê

```
RASCUNHO ──► AGUARDANDO ASSINATURAS ──► EM PROCESSAMENTO ──► REGISTRADO
   │                  │     ▲                   │
   │                  │     └───────────────────┘  reassinatura
   │                  │
   └──────────────────┴──────────► CANCELADO
```

Cinco estados, inalterados pela rev. 3. O que muda por dentro de "aguardando assinaturas" é que agora é um **envelope único** (contrato, CPR e demais documentos), com janela curta e configurável — 15 minutos de partida (RN-119) — em vez de dias com lembretes. A seta de volta, de "em processamento" para "aguardando assinaturas", só acontece na reassinatura, e é a única vez que o membro vê o estado andar para trás. _(L-06, correção de desenho)_

---

## Camada 2 — o que o backoffice vê

```
RASCUNHO ─────────────────────────────────────────────► CANCELADO  (descarte, L-01)
   │
   ▼
PRE_VALIDANDO  (novo, rev. 3: valida payload contra os domínios e formatos da B3)
   │
   ├─ falhou ─► RASCUNHO  (volta com os erros listados, T-08. Não abre envelope, não assina nada)
   │
   ▼  passou
AGUARDANDO_ASSINATURAS  (envelope único: contrato + CPR + demais documentos, janela curta)
   │            │                              │
   │            │                              └─► JANELA_EXPIRADA  (ninguém concluiu a tempo, T-09)
   │            │                                        ├─► reabrir janela ─► AGUARDANDO_ASSINATURAS
   │            │                                        └─► CANCELADO  (decisão humana, nunca automática)
   │            └──► CANCELADO  (autor, ninguém assinou ainda, L-02 — fechada na rev. 5 das regras)
   │
   ├──► RECUSADO_POR_PARTE ──► RASCUNHO  (autor corrige, L-08)
   │                 └──────────► CANCELADO
   ▼
ASSINADO  (envelope inteiro assinado por todos os signatários convocados, de uma vez)
   │
   ▼
ENVIANDO_B3 ◄───────────────────────────────────────────┐
   │   ├─ transitório ─► consulta ─► achou ─► REGISTRADO │
   │   │                     └─► não achou ─► reenvia ───┘  (até N vezes, I-03)
   │   │
   │   └─ definitivo, ou N tentativas esgotadas
   │              ▼
   │          FALHA_B3 ──► alerta (crítico, ver nota abaixo)
   │              ▼
   │         EM_CORRECAO ◄─── operador assume
   │              │
   │   ┌──────────┼─────────────┬──────────────┐
   │   ▼          ▼             ▼              ▼
   │ reenviar  corrigir     reassinatura    cancelar
   │ (consulta  payload         │              │
   │  antes)      │             ▼              ▼
   │   │          │    AGUARDANDO_REASSINATURA  CANCELADO
   │   └──────────┴──────► ENVIANDO_B3   │
   │                                     └─ parte recusa ─► EM_CORRECAO  (L-03)
   ▼
REGISTRADO  (terminal)
```

**`EM_CORRECAO` continua existindo, mas o cliente quer vê-lo como exceção rara, não rotina.** "O fluxo EM_CORREÇÃO é muito danoso para o clube" (reunião 2, 24/09). A pré-validação (`PRE_VALIDANDO`) é a resposta de produto a isso: pega antes da assinatura o que daria **422** de formato/domínio na B3 — a classe de erro mais provável e mais evitável — e nunca deixa chegar a um documento assinado que já se sabe que vai falhar no registro. Erros genuinamente do lado da B3 (fora do ar, mudança de regra sem aviso) continuam possíveis e continuam exigindo os quatro caminhos.

---

## Transições novas da rev. 2 e da rev. 3

| # | Transição | Quem dispara | Status | Origem |
|---|---|---|---|---|
| T-01 | `RASCUNHO` → `CANCELADO` com motivo "descartado" | Autor | **Aplicada**, rev. 5 das regras (RN-71) | Regras L-01 |
| T-02 | `AGUARDANDO_ASSINATURAS` → `CANCELADO`, só enquanto ninguém assinou. Depois da primeira assinatura, vira pedido ao backoffice | Autor | **Aplicada**, rev. 5 das regras (RN-71, RN-72) | Regras L-02, RN-71 |
| T-03 | `RECUSADO_POR_PARTE` → `RASCUNHO`, preservando o motivo da recusa. Documento novo, assinaturas novas | Autor | _Proposta_ | Regras L-08 |
| T-04 | `AGUARDANDO_REASSINATURA` → `EM_CORRECAO` quando uma parte recusa a reassinatura | Sistema | _Proposta_ | Regras L-03 |
| T-05 | Dentro de `ENVIANDO_B3`: erro transitório dispara consulta e, se não achou, reenvio automático até N vezes | Sistema | _Proposta, precisa do seu aceite_ | B3 §5, consolidação I-03 |
| T-06 | Caminho 1 (reenviar) passa a consultar a B3 antes de reenviar | Operador | **Aplicada**. É correção de risco, não de produto | B3 §5 |
| T-07 | Seta de volta na camada 1 | — | **Aplicada**. Já existia na tabela de mapeamento | Regras L-06 |
| T-08 | `RASCUNHO` → `PRE_VALIDANDO` → `RASCUNHO` (se falhar) ou `AGUARDANDO_ASSINATURAS` (se passar). A pré-validação confere o payload contra os domínios e formatos conhecidos da B3, **sem chamar a B3** | Sistema | _Proposta, precisa do seu aceite_ | Reunião 2, 24/09/2026; pendência 1.35 |
| T-09 | `AGUARDANDO_ASSINATURAS` → `JANELA_EXPIRADA` quando a janela do envelope (RN-119) se esgota sem todas as assinaturas. Dali, reabrir uma nova janela ou cancelar são decisões humanas — nenhuma é automática (RN-120) | Sistema (detecta) / Autor ou backoffice (decide o destino) | _Proposta_ | RN-118 a RN-120 |

**Fora do MVP:** aditivo a partir de `REGISTRADO` (L-04). Depende de aditamento de CPR na B3, operação separada e sem estimativa. `REGISTRADO` segue terminal.

---

## Mapeamento entre as camadas

| Interno | Membro vê |
|---|---|
| `RASCUNHO` | Rascunho |
| `PRE_VALIDANDO` | Rascunho (passo automático, geralmente imperceptível) |
| `AGUARDANDO_ASSINATURAS` | Aguardando assinaturas |
| `JANELA_EXPIRADA` | Aguardando assinaturas, com aviso de que precisa reabrir |
| `RECUSADO_POR_PARTE` | Cancelado, ou Rascunho se o autor corrigir |
| `ASSINADO` | Em processamento |
| `ENVIANDO_B3` | Em processamento |
| `FALHA_B3` | Em processamento |
| `EM_CORRECAO` | Em processamento |
| `AGUARDANDO_REASSINATURA` | Aguardando assinaturas |
| `REGISTRADO` | Registrado |
| `CANCELADO` | Cancelado |

---

## A proposta de adesão — uma máquina separada

**Nova na rev. 3.** Não é mais um simples "em análise / aprovado / recusado". É uma máquina própria, que roda antes de existir qualquer conta de membro, e que termina sendo materializada pelo backoffice a partir de uma decisão tomada fora do sistema. Regras em `regras-de-negocio.md` §1.

```
PREENCHENDO
   │  (proponente nomeia 2 recomendantes)
   ▼
AGUARDANDO_ASSINATURA_RECOMENDANTES
   │  (proponente e os 2 recomendantes assinam, mesmo processo do registro)
   ▼
EM_FILA_COMITE ◄──────────────────────┐
   │                                   │
   ├─ comitê pede mais dados ─► EM_DILIGENCIA ─ respondido ─┘
   │
   ├─ comitê decide (offline, reunião semanal) ─► backoffice materializa
   │
   ├──► APROVADA ──► RN-32 (cria conta de membro) ──► RN-114 (assina termos do clube)
   │
   └──► RECUSADA  (sem bloqueio automático de CPF/CNPJ — RN-110. Proponente pode propor de novo quando quiser)

AGUARDANDO_ASSINATURA_RECOMENDANTES → EXPIRADA, se a janela de assinatura dos recomendantes vencer sem conclusão (prazo a definir, análogo a RN-89)
```

**O que ainda está em aberto nesta máquina:**
- Se `EM_FILA_COMITE` e `EM_DILIGENCIA` são estados do sistema de verdade, ou só uma anotação sobre um processo majoritariamente manual (pendência 1.28).
- Como um recomendante que não é membro assina `AGUARDANDO_ASSINATURA_RECOMENDANTES` (pendência 1.27) — é a mesma pergunta que a seção de registro resolveu com "todo signatário é membro", mas aqui parece haver exceção.
- Se existe via expressa para proposta urgente, fora do ciclo semanal do comitê (pendência 1.30).

---

## O prazo legal

A CPR precisa ser registrada em **30 dias úteis** a partir da emissão (Lei 8.929/1994, art. 12, redação da Lei 14.421/2022). Número do artigo a conferir pelo escritório, pendência 2.7.

| Item | Regra | Status |
|---|---|---|
| Quando começa | Data de emissão. **Se é o envio para assinatura ou a última assinatura, decide o escritório** | Pendente 2.8 |
| Estados que consomem prazo | Todos entre a emissão e `REGISTRADO` | Aplicada |
| Dias úteis | Calendário nacional de feriados, configurável | Aplicada |
| Fila de pendências | **Ordena por prazo legal restante**, não por tempo parado | Aplicada |
| Alertas | D-10 e D-5 dias úteis para o backoffice. D-2 para o responsável nominal | _Proposta_ |
| Prazo vencido | Nada automático. Alerta máximo e decisão humana com o jurídico | _Proposta_ |

Se a emissão for no envio para assinatura, a coleta de assinaturas, a correção e a reassinatura saem todas do mesmo saldo de 30 dias úteis. **Com a janela do envelope em minutos (RN-119), a coleta de assinaturas deixa de ser a parte que mais consome esse saldo** — o risco se concentra no tempo entre `ASSINADO` e `REGISTRADO`, que é exatamente onde a pré-validação (T-08) e os quatro caminhos atuam.

---

## Os quatro caminhos de resolução

A regra que separa os caminhos continua a mesma:

> **O dado errado aparece no documento assinado?**
> Se não, é correção técnica. Se sim, exige nova assinatura.

### 1. Reenviar
Falha transitória que esgotou as tentativas automáticas, ou que o operador sabe ter sido resolvida do lado da B3.

**Sempre consulta antes.** A B3 não documenta idempotência. Consulta por Número de Controle Interno; se o registro existe, reconcilia e vai para `REGISTRADO`; se não existe, reenvia.

**Registra:** quem mandou, quando, resultado da consulta, número da tentativa.

### 2. Corrigir payload
Erro de mapeamento ou formatação nosso. O documento assinado continua válido.
**Registra:** diff do payload, quem autorizou.

### 3. Reassinatura
O dado errado está no documento. Substituição ou aditivo, decidido com o jurídico (pendência 2.13).
**Registra:** documento antes e depois, variante, quem decidiu, justificativa.

### 4. Cancelar
Sem solução. Motivo obrigatório.

### Como os erros da B3 chegam a cada caminho

Resumo de `estudo-api-b3.md` §3.

| Resposta da B3 | Tratamento |
|---|---|
| 401 | Renova token e tenta uma vez. Falhou de novo: **alerta para infraestrutura**, não para o backoffice |
| 429, 503 | Automático, com backoff |
| 408, 500, 504, timeout, rede | Automático: consulta antes de reenviar |
| 400, 404, 405, 415, 421 | `FALHA_B3`. Bug nosso. Caminho 2 |
| **422** | `FALHA_B3`. **Sempre humano no MVP.** Caminho 2 ou 3 conforme a regra acima |
| 422 de duplicidade | `FALHA_B3`. Consultar antes de cancelar: pode ser um registro nosso que já entrou |

---

## Os alertas

| Alerta | Quando | Para quem | Status |
|---|---|---|---|
| Falha no registro | Entra em `FALHA_B3` | Backoffice | Aplicada. Canal e dono: pendência 1.19 |
| Prazo legal | D-10, D-5, D-2 dias úteis | Backoffice e responsável nominal | _Proposta_ |
| Janela do envelope expirando | Faltam 2 minutos para o fim da janela de assinatura (RN-119) e ainda falta signatário | Quem está na tela do envelope, em tempo real | _Proposta_, rev. 3 |
| Janela do envelope expirou | Registro foi para `JANELA_EXPIRADA` sem concluir (T-09) | Autor e backoffice | _Proposta_. A Clicksign não avisa quando o certificado falha (consolidação I-06) |
| Credencial | 401 repetido, certificado da B3 perto de vencer | Infraestrutura | Aplicada |
| Pendência sem dono | `FALHA_B3` sem ninguém assumir em X horas | Responsável pelo backoffice | _Proposta_. Prazos: pendência 1.19 |

---

## A tela de resolução

Numa tela só:

- Dados do registro como o membro preencheu
- Documento assinado, visualizável ali mesmo
- Payload exato enviado à B3
- Resposta da B3 com `errors[].code`, `title` e `detail` **inteiros**. `detail` tem até 2.000 caracteres e não pode ser truncado
- Resultado de cada consulta de reconciliação
- Histórico de tentativas, automáticas e manuais
- **Prazo legal restante**
- Os quatro botões, cada um pedindo justificativa

---

## O que é rastreado, sempre

Toda transição grava: registro, estado anterior, estado novo, autor, horário, motivo e, quando houver, diff.

Ação automática grava o sistema como autor, com o gatilho. Isso vale para cada tentativa automática da T-05 e para cada consulta de reconciliação.

Assinatura feita dentro de sessão longa de certificado em nuvem (até 7 dias no Bird ID e no NeoID) grava qual sessão autorizou e quando ela foi criada.

**Novo na rev. 3:** toda assinatura de envelope grava a lista de documentos cobertos por aquele evento único (RN-116). Toda decisão do comitê de admissão materializada pelo backoffice grava a referência à reunião/ata de origem, o parecer (se houver) e quem no backoffice lançou a decisão (RN-106, RN-109), mesmo quando o comitê em si não é um ator do sistema.
