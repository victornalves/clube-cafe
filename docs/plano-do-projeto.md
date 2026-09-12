# Clube do Café — Plano do Projeto

**Revisão 2** · 12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 3)

---

## Estratégia

Construir o sistema inteiro com assinatura e B3 mockadas, entregar funcionando de ponta a ponta, e trocar cada mock pela integração real depois.

Com a homologação da B3 resolvida, isso deixou de ser proteção contra risco de prazo e virou só sequenciamento de trabalho: a máquina de estados fica pronta e testada antes de depender de resposta de terceiro.

---

## Fases

### Fase 0 — Validação de escopo
**Modelo: hora, R$ 300/h.** É onde estamos.

| Entregável | Para quê |
|---|---|
| Mockup HTML clicável | Validar os fluxos sem escrever backend |
| Lista final de campos (cadastro + registro) | Fechar o que precisa de validação |
| Máquina de estados aprovada pelo cliente | Confirmar as duas camadas e os quatro caminhos de resolução |
| Definição dos modelos de documento | Transformar "múltiplos modelos" em um número |
| **Leitura da documentação da API B3 + mapeamento do payload** | Estimar a Fase 3 com número real em vez de chute |
| **Comparativo escrito de parceiros ICP-Brasil** | Escolher por critério, não por demo |

Estimativa: **24 a 32h**.

**Saída:** proposta de escopo fechado ancorada em algo que o cliente já viu e aprovou.

---

### Fase 1 — Sistema completo, com mocks
**Modelo: escopo fechado**

Funciona do cadastro ao "registrado". Assinatura e B3 simuladas internamente, com as mesmas telas e os mesmos estados da versão real.

| Bloco | Horas |
|---|---|
| Setup, autenticação, papéis, MFA de backoffice | 20 |
| Solicitação de cadastro + fila de aprovação | 20 |
| Formulário de registro (multi-etapa) | 24 |
| Geração de documento, 1 modelo | 20 |
| Assinatura mockada + máquina de estados em duas camadas | 24 |
| Envio B3 mockado + tela de resolução + os 4 caminhos | 24 |
| Painel de backoffice | 24 |
| Área do membro | 16 |
| Páginas públicas | 8 |
| Segurança: isolamento por registro + testes de autorização | 12 |
| Segurança: criptografia de aplicação + gestão de chaves | 16 |
| Segurança: logs de eventos e acessos + exportação controlada | 12 |
| Testes, deploy, ajustes | 24 |
| **Total** | **~244h** |

---

### Fase 2 — Assinatura ICP-Brasil real
**Modelo: escopo fechado, após escolha do parceiro**

Troca o mock pelo provedor escolhido. Inclui webhook, reconciliação de estado e assinatura embutida quando o tipo de certificado permitir.

Estimativa: **32 a 40h**. A faixa depende de certificado em nuvem (mais simples) ou token físico (exige componente local).

---

### Fase 3 — B3 real
**Modelo: escopo fechado**

Troca o mock pela API real, sob a conta do escritório sócio. Sem gate externo: falta apenas solicitar a API key de homologação.

Estimativa: **32 a 40h**, a fechar depois da leitura da documentação na Fase 0.

---

## O número total, sem maquiagem

| Fase | Horas |
|---|---|
| 0 — Validação | 24–32 |
| 1 — Sistema com mocks | ~244 |
| 2 — Assinatura real | 32–40 |
| 3 — B3 real | 32–40 |
| **Total** | **~332 a 356h** |

O dossiê original falava em 200h e R$ 45.000. A diferença não é inflação de estimativa. É escopo que apareceu depois: painel de backoffice, fluxo de aprovação de cadastro, área do membro, páginas públicas, resolução de falhas com human in the loop e o bloco inteiro de segurança.

**Levar essa conta ao cliente antes da proposta**, junto com as alavancas abaixo. Descobrir o número no meio do projeto é pior para todo mundo.

### Alavancas para reduzir, se necessário

| Corte | Economia | Custo do corte |
|---|---|---|
| Adiar criptografia de aplicação (mantendo isolamento e logs) | ~16h | Dump de banco fica exposto. Aceitável só antes de dado real |
| 2 papéis de backoffice em vez de 3 | ~6h | Quem aprova cadastro enxerga termos comerciais |
| Landing mínima em vez de página de conteúdo | ~6h | Nenhum. É clube fechado |
| Travar em 1 modelo de documento | já previsto | Modelos extras viram cotação por unidade |

Não recomendo cortar o isolamento por registro nem os logs de auditoria. São o produto, não o enfeite.

---

## Escolha do parceiro ICP-Brasil

Comparar por escrito, mesma tabela para todos. Candidatos a avaliar: ZapSign, Clicksign, D4Sign, BRy, Lacuna, Certisign.

| Critério | Por que importa |
|---|---|
| Assinatura qualificada ICP-Brasil | Requisito confirmado |
| Certificado em nuvem via API (Vidaas, Bird ID, Safeweb) | Define se dá para assinar sem sair da nossa tela |
| Assinatura embutida: iframe, SDK ou redirect obrigatório | Requisito de UX do cliente |
| Webhook de retorno | Sem isso, viramos polling |
| Sandbox de verdade | Necessário para a Fase 1 |
| Quem guarda o documento | Queremos guardar nós |
| Preço por documento e mínimo mensal | O opex do dossiê (R$ 295/mês) presume volume baixo. Confirmar |
| Manifesto e trilha de auditoria da assinatura | É o que prova a assinatura depois |

**Antes de tudo isso, perguntar ao cliente que certificado os membros já têm.** Se for token físico, a promessa de assinar sem sair da plataforma muda.

---

## Telas do mockup (Fase 0)

### Públicas
1. Landing discreta
2. Solicitar convite
3. Login

### Membro
4. Meus registros (listagem com status simplificado)
5. Novo registro — etapa 1: partes
6. Novo registro — etapa 2: objeto, data, valor
7. Novo registro — etapa 3: revisão
8. Pré-visualização do documento (HTML simulando o PDF)
9. Assinatura (status por parte)
10. Detalhe do registro (linha do tempo)
11. Minha conta

### Backoffice
12. Fila de aprovação de cadastros
13. Detalhe da solicitação (aprovar / recusar)
14. Todos os registros
15. **Fila de pendências** (registros em falha)
16. **Tela de resolução de falha** (com os 4 caminhos)
17. Auditoria (consulta aos logs)

Dezessete telas, HTML puro, sem framework, links reais entre elas. O cliente clica e percorre a jornada inteira, incluindo o caminho de erro.

As telas 15, 16 e 17 são novas nesta revisão e são as mais importantes de validar: é onde o backoffice trabalha todo dia.

---

## Depois do mockup: opções de UI

Só depois que os fluxos estiverem aprovados. Duas ou três direções visuais aplicadas às mesmas telas.

Separar as duas conversas é o que impede o cliente de reabrir o fluxo por causa de uma cor.

---

## Como escrever para este cliente

Não são pessoas de tecnologia.

- Estado em português comum: "aguardando assinatura do comprador", nunca `pending_signature`.
- Uma ação principal por tela.
- Zero jargão de software na interface: sem "payload", "webhook", "API", "sync".
- Linha do tempo em linguagem de fato: "João assinou em 10/09 às 14h".
- Erro sempre com o próximo passo junto.

A tela de resolução do backoffice é a exceção parcial: quem a usa é time interno e precisa ver o payload e a resposta da B3.

---

## Sequência recomendada

1. Pedir a API key de homologação da B3 ao escritório **hoje**
2. Ler a documentação da API e mapear o payload da CPR de café
3. Perguntar ao cliente que certificado ICP os membros usam
4. Montar o mockup HTML
5. Reunião de validação em cima do mockup
6. Fechar campos, modelos e máquina de estados
7. Comparar e escolher o parceiro de assinatura
8. Emitir a proposta de escopo fechado

Os passos 1, 2 e 3 podem correr em paralelo com o 4. Nenhum deles depende do mockup.

---

## Nota comercial

As horas são preliminares até o mockup existir. Estimar preço fechado antes dele significa chutar o tamanho dos formulários e das validações, que é onde o trabalho mora.

Caminho seguro: cobrar a Fase 0 por hora, usar o mockup aprovado como anexo do contrato, e fechar o preço da Fase 1 em cima dele.

Uma decisão a tomar: **preço fechado não é hora × R$ 300.** Escopo fechado transfere o risco de estimativa para você. Ou o valor fechado carrega um prêmio sobre a taxa horária, ou o contrato precisa de cláusula de escopo com gatilho de aditivo. Escolher uma das duas antes de enviar a proposta.
