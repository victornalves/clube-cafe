# Máquina de Estados do Registro

**Revisão 2** · 12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 4)

A rev. 1 continua valendo. A rev. 2 acrescenta o prazo legal, a consulta antes de reenviar à B3, e sete transições que a Frente 4 encontrou faltando.

**Tudo marcado _Proposta_ espera aceite do cliente ou do escritório.** Os diagramas `diagramas/02`, `03` e `04` já mostram a rev. 2, com as propostas em tracejado laranja.

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

Cinco estados. A seta de volta, de "em processamento" para "aguardando assinaturas", só acontece na reassinatura, e é a única vez que o membro vê o estado andar para trás. _(L-06, correção de desenho)_

---

## Camada 2 — o que o backoffice vê

```
RASCUNHO ─────────────────────────────────────────────► CANCELADO  (descarte, L-01)
   │
   ▼
AGUARDANDO_ASSINATURAS ──► CANCELADO  (autor, ninguém assinou ainda, L-02)
   │            │
   │            └──► RECUSADO_POR_PARTE ──► RASCUNHO  (autor corrige, L-08)
   │                           └──────────► CANCELADO
   ▼
ASSINADO
   │
   ▼
ENVIANDO_B3 ◄───────────────────────────────────────────┐
   │   ├─ transitório ─► consulta ─► achou ─► REGISTRADO │
   │   │                     └─► não achou ─► reenvia ───┘  (até N vezes, I-03)
   │   │
   │   └─ definitivo, ou N tentativas esgotadas
   │              ▼
   │          FALHA_B3 ──► alerta
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

---

## Transições novas da rev. 2

| # | Transição | Quem dispara | Status | Origem |
|---|---|---|---|---|
| T-01 | `RASCUNHO` → `CANCELADO` com motivo "descartado" | Autor | _Proposta_ | Regras L-01 |
| T-02 | `AGUARDANDO_ASSINATURAS` → `CANCELADO`, só enquanto ninguém assinou. Depois da primeira assinatura, vira pedido ao backoffice | Autor | _Proposta_ | Regras L-02, RN-71 |
| T-03 | `RECUSADO_POR_PARTE` → `RASCUNHO`, preservando o motivo da recusa. Documento novo, assinaturas novas | Autor | _Proposta_ | Regras L-08 |
| T-04 | `AGUARDANDO_REASSINATURA` → `EM_CORRECAO` quando uma parte recusa a reassinatura | Sistema | _Proposta_ | Regras L-03 |
| T-05 | Dentro de `ENVIANDO_B3`: erro transitório dispara consulta e, se não achou, reenvio automático até N vezes | Sistema | _Proposta, precisa do seu aceite_ | B3 §5, consolidação I-03 |
| T-06 | Caminho 1 (reenviar) passa a consultar a B3 antes de reenviar | Operador | **Aplicada**. É correção de risco, não de produto | B3 §5 |
| T-07 | Seta de volta na camada 1 | — | **Aplicada**. Já existia na tabela de mapeamento | Regras L-06 |

**Fora do MVP:** aditivo a partir de `REGISTRADO` (L-04). Depende de aditamento de CPR na B3, operação separada e sem estimativa. `REGISTRADO` segue terminal.

---

## Mapeamento entre as camadas

| Interno | Membro vê |
|---|---|
| `RASCUNHO` | Rascunho |
| `AGUARDANDO_ASSINATURAS` | Aguardando assinaturas |
| `RECUSADO_POR_PARTE` | Cancelado, ou Rascunho se o autor corrigir |
| `ASSINADO` | Em processamento |
| `ENVIANDO_B3` | Em processamento |
| `FALHA_B3` | Em processamento |
| `EM_CORRECAO` | Em processamento |
| `AGUARDANDO_REASSINATURA` | Aguardando assinaturas |
| `REGISTRADO` | Registrado |
| `CANCELADO` | Cancelado |

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

Se a emissão for no envio para assinatura, a coleta de assinaturas, a correção e a reassinatura saem todas do mesmo saldo de 30 dias úteis.

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
| Assinatura parada | Registro em `AGUARDANDO_ASSINATURAS` sem evento novo há X dias | Autor e backoffice | _Proposta_. A Clicksign não avisa quando o certificado falha (consolidação I-06) |
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
