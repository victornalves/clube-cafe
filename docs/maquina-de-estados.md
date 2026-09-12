# Máquina de Estados do Registro

12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 3)

---

## O princípio

Duas camadas. O membro vê uma versão simplificada. O backoffice vê tudo.

O membro não precisa saber que a B3 recusou um payload. Ele precisa saber que está em processamento e que alguém está cuidando.

---

## Camada 1 — o que o membro vê

```
RASCUNHO  →  AGUARDANDO ASSINATURAS  →  EM PROCESSAMENTO  →  REGISTRADO
                        │                       │
                        └───────► CANCELADO ◄───┘
```

Cinco estados. Nenhum deles exige explicação técnica.

---

## Camada 2 — o que o backoffice vê

```
RASCUNHO
   │
   ▼
AGUARDANDO_ASSINATURAS ──────────► RECUSADO_POR_PARTE
   │                                        │
   ▼                                        ▼
ASSINADO                               CANCELADO
   │
   ▼
ENVIANDO_B3 ──────────► FALHA_B3
   │                        │
   │                        ▼
   │                   EM_CORRECAO  ◄──── backoffice assume
   │                        │
   │         ┌──────────────┼──────────────┬─────────────┐
   │         ▼              ▼              ▼             ▼
   │      retry      corrigir payload  reassinatura   cancelar
   │         │              │              │             │
   │         └──────────────┴──────┐       ▼             ▼
   │                               │  AGUARDANDO_    CANCELADO
   └───────────────────────────────┤  REASSINATURA
                                   │       │
                                   ▼       │
                              ENVIANDO_B3 ◄┘
   ▼
REGISTRADO
```

---

## Mapeamento entre as camadas

| Interno | Membro vê |
|---|---|
| `RASCUNHO` | Rascunho |
| `AGUARDANDO_ASSINATURAS` | Aguardando assinaturas |
| `ASSINADO` | Em processamento |
| `ENVIANDO_B3` | Em processamento |
| `FALHA_B3` | Em processamento |
| `EM_CORRECAO` | Em processamento |
| `AGUARDANDO_REASSINATURA` | Aguardando assinaturas |
| `REGISTRADO` | Registrado |
| `CANCELADO` / `RECUSADO_POR_PARTE` | Cancelado |

`AGUARDANDO_REASSINATURA` é a única exceção: volta a aparecer para o membro, porque exige ação dele.

---

## Os quatro caminhos de resolução

Quando a B3 recusa, o backoffice escolhe um caminho. A regra que separa os casos:

> **O dado errado aparece no documento assinado?**
> Se não, é correção técnica. Se sim, exige nova assinatura.

### 1. Retry
Falha transitória: timeout, instabilidade, erro 5xx. Reenvia o mesmo payload sem tocar em nada.
**Registra:** quem mandou reenviar, quando, qual tentativa.

### 2. Corrigir payload
Erro nosso de mapeamento ou formatação. O dado do contrato está certo, o envio estava errado. Corrige e reenvia.
**O documento assinado continua válido.**
**Registra:** o que mudou no payload, antes e depois, quem autorizou.

### 3. Reassinatura
O dado errado está dentro do documento assinado. Precisa de documento novo e assinatura nova. Duas variantes, decididas caso a caso com o jurídico:

| Variante | Quando | O que acontece com o anterior |
|---|---|---|
| Substituição | Erro material, contrato ainda não produziu efeito | Cancelado e arquivado, com motivo |
| Aditivo | Contrato válido, ajuste pontual | Preservado, novo documento referencia o anterior |

**Registra:** documento antes, documento depois, variante escolhida, quem decidiu, justificativa.

### 4. Cancelamento
Não tem solução. Arquiva com motivo obrigatório.
**Registra:** motivo, quem decidiu, quando.

---

## O alerta

Quando um registro entra em `FALHA_B3`:

- Alerta disparado para o time de backoffice.
- Canal, responsável e prazo de resposta: **a definir com o cliente.**
- Registro entra numa fila de pendências no painel, visível até ser resolvido.

Sem dono e sem prazo, o alerta vira ruído e a fila cresce. Definir isso é decisão do cliente, não nossa.

---

## A tela de resolução

"Toda informação necessária para agir" significa, numa tela só:

- Dados do registro como o membro preencheu
- Documento assinado, visualizável ali mesmo
- Payload exato que enviamos à B3
- Resposta da B3: código, mensagem, horário
- Histórico de todas as tentativas anteriores
- Os quatro botões de ação, cada um pedindo justificativa

Se o operador precisar abrir outra tela ou consultar um log para decidir, a tela está errada.

---

## O que é rastreado, sempre

Toda transição de estado grava: registro, estado anterior, estado novo, quem causou, quando, motivo e, quando houver, o diff do que mudou.

Transição sem autor identificado não existe. Ação automática grava o sistema como autor, com o gatilho que a originou.
