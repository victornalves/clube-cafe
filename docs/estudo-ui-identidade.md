# Estudo de Identidade Visual e Direções de UI

12/09/2026 · frente 5 · complementa `plano-do-projeto.md` (rev. 2)

Três direções visuais, aplicadas às mesmas três telas cada uma, para comparação lado a lado.

**Canvas:** https://claude.ai/code/artifact/b12e699d-5f5e-47bb-a4c7-a58710df9349

---

## Regra de sequência, antes de qualquer coisa

**Isto não entra no mockup da frente 6, e não entra na reunião de validação de fluxo.**

O mockup é deliberadamente sem estilo. Se o cliente vir cor e tipografia antes de aprovar o fluxo, a reunião vira conversa sobre a cor do botão, e o fluxo sai da pauta. As duas conversas acontecem em ordem: primeiro o fluxo, depois o visual.

Este documento existe para estar pronto quando a segunda conversa chegar, não para antecipá-la.

---

## O que as três direções têm em comum

Fixo em todas, porque são requisitos e não escolha estética:

| Requisito | De onde vem | Como aparece |
|---|---|---|
| Corpo de texto de 16 px para cima | Público pode ter idade mais alta | Nenhuma direção usa menos de 16 px em texto corrido; duas usam 17 |
| Alvo de toque de 44 px no mínimo | Acompanhamento de status pelo celular | Botões entre 46 e 58 px de altura |
| Contraste alto de verdade | Acessibilidade, não selo | Texto sobre fundo sempre acima de 7:1 |
| `<label>` amarrado a cada campo | Leitor de tela e clique na etiqueta | Em todos os formulários |
| Estado em português comum | `plano-do-projeto.md`, "Como escrever para este cliente" | "Aguardando assinatura do comprador", nunca `pending_signature` |
| Cor só onde carrega informação | Sobriedade pedida pelo cliente | Nenhuma das três usa cor decorativa |

As mesmas três telas em cada direção: **listagem de registros**, **novo registro (etapa de partes)** e **detalhe com linha do tempo**. Mesmos dados falsos em todas, para a comparação ser justa: contrato CRTC-2026-0184, 1.200 sacas, R$ 1.776.000,00.

---

## As três direções

| | A · Cartório | B · Terra | C · Pregão |
|---|---|---|---|
| **Referência** | Livro de registro, documento oficial | Cooperativa, material do agro | Mesa de operações, sistema de bolsa |
| **Tipografia** | Libre Baskerville + Source Serif 4 | Bitter + Public Sans | IBM Plex Sans + IBM Plex Mono |
| **Fundo** | Papel creme, `#faf8f3` | Creme quente, `#fdfaf6` | Cinza frio, `#f4f5f7` |
| **Acento** | Verde-tinta, `#1f4d3a` | Terracota, `#8c4a2f` | Navy, `#1a3a6b` |
| **Navegação** | Menu horizontal no topo | Menu horizontal no topo | Menu lateral escuro |
| **Listagem** | Tabela com fio, sem cartão | Cartões empilhados | Tabela densa, números em monoespaçada |
| **Corpo** | 16–17 px | 17–19 px | 15–16 px |
| **Cantos** | Retos | 6–8 px | Retos |

### A · Cartório

Papel creme, serifa, fio fino, tabela sem cartão.

**A favor:** a seriedade vem da forma, não de um selo. Densidade alta sem parecer painel de banco. Serifa em corpo grande lê bem para quem tem 60 anos.

**Contra:** pouca cor deixa a situação do contrato menos imediata na varredura rápida. Serifa exige tela boa.

### B · Terra

Paleta de terra, tipo grande, cartões no lugar da tabela, ícones de traço.

**A favor:** a mais legível das três. Corpo de 17 a 19 px e alvo de toque de 54 px. Fala a língua do agro sem fantasia.

**Contra:** cinco registros já ocupam a tela inteira. Quando o membro tiver 40 contratos, a listagem em cartão cansa. Terracota puxa para "marca de café", que o cliente não pediu.

### C · Pregão

Cinza frio, navy, monoespaçada nos números, menu lateral escuro, tabela densa.

**A favor:** rastreabilidade é o assunto do produto, e número alinhado em monoespaçada se confere melhor. É a única que escala para as telas de backoffice sem redesenho.

**Contra:** a mais fria. Para um produtor abrindo no celular, parece sistema de banco. O menu lateral escuro custa área em tela pequena.

---

## Recomendação

**A · Cartório**, com um empréstimo da C.

O produto é um registro de contratos. Das três, A é a única que diz isso pela forma em vez de dizer com um aviso na tela. A sobriedade pedida pelo cliente sai de graça, e a densidade serve tanto o membro quanto o backoffice.

O empréstimo: **números em monoespaçada, como na C**. Valor, quantidade e protocolo alinhados à direita em monoespaçada se conferem melhor do que em serifa proporcional, e um contrato de R$ 1.776.000,00 é conferido, não lido.

Se o cliente recusar serifa, a segunda escolha é **C**, não B. C erra por frieza, que se corrige com espaçamento e um acento mais quente. B erra por densidade, que não se corrige sem refazer a listagem.

---

## Contradições com os docs existentes

Nenhuma.

---

## Decisões pendentes do cliente

1. **O clube tem nome definitivo?** "Clube do Café" está marcado como provisório no README. Marca e identidade dependem disso, e refazer depois custa.
2. **O backoffice usa a mesma identidade do membro?** São públicos diferentes: o membro usa poucas vezes por mês, o operador passa o dia na tela. Divergir é defensável e custa horas.
3. **Tamanho mínimo de corpo, testado com um produtor de verdade.** As três direções assumem 16 px ou mais por dedução, não por teste. Uma sessão de 30 minutos com um membro resolve.
4. **Existe material de marca do clube** (logotipo, cor, papelaria) ou a identidade nasce aqui?

---

## O que não está aqui

Ícone próprio, ilustração, animação e logotipo. Nada disso entra antes da direção escolhida, e nada disso está no escopo da Fase 0.
