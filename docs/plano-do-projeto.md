# Clube do Café — Plano do Projeto

**Revisão 3** · 12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 4)

---

## Onde estamos

**Fase 0, validação de escopo.** As seis frentes de estudo terminaram e a consolidação foi feita (`consolidacao-rev4.md`). O que falta para sair da Fase 0:

| # | Tarefa | Quem | Depende de |
|---|---|---|---|
| 1 | ~~Commitar o estudo da Lacuna~~ Feito | — | — |
| 2 | Enviar os dois e-mails ao escritório sócio (`pendencias.md` §2) | Você | — |
| 3 | Enviar as perguntas à Clicksign e à Lacuna (§3 e §4) | Você | — |
| 4 | ~~Ajustar telas do mockup~~ Feito, com as duas formas de assinar (9a e 9b). Revisar | Você | — |
| 5 | Reunião de validação com o cliente (`pauta-reuniao-validacao.md`) | Você | 4 |
| 6 | Escolher o fornecedor de assinatura | Você + cliente | 3, 5 |
| 7 | Revisão 5: aplicar respostas, fechar faixas | Sessão Claude | 2, 3, 5 |
| 8 | Proposta de escopo fechado da Fase 1 | Você | 7 |

As tarefas 2 e 3 não dependem de ninguém e podem sair hoje.

### Ajustes do mockup antes da reunião, feitos em 12/09

| Tela | Ajuste |
|---|---|
| `02b` | Prazo de análise coerente com a regra escolhida (dois ou três dias úteis) |
| `06` | Acrescentar situação, produção, imóvel, acondicionamento, garantia, indexador, vencimento, finalidade. Marcar bebida e peneira como "vai no contrato" |
| `09` | Mostrar o caso em que o membro sai para o aplicativo do certificado e volta. Sem citar fornecedor |
| `15` | Ordenar e exibir por prazo legal restante |
| `16a` | Mostrar a consulta à B3 antes do reenvio, e o resultado dela |

---

## Estratégia

Construir o sistema inteiro com assinatura e B3 simuladas, entregar funcionando de ponta a ponta, e trocar cada simulação pela integração real depois. A simulação da assinatura precisa ter os **dois modos de entrega**, embutido e redirecionado, para que a escolha do fornecedor não mexa na Fase 1.

---

## Fases

### Fase 0 — Validação de escopo
**Hora, R$ 300/h.** Planejado: 24–32h. Horas reais até aqui: registrar.

### Fase 1 — Sistema completo, com simulações
**Escopo fechado.**

| Bloco | Rev. 2 | Rev. 3 |
|---|---|---|
| Setup, autenticação, papéis, MFA | 20 | 20 |
| Solicitação de cadastro + fila de aprovação | 20 | 20 |
| Formulário de registro com os campos da B3 | 24 | **36–44** |
| Geração de documento, 1 modelo | 20 | 20 |
| Assinatura simulada com dois modos + máquina de estados | 24 | **27–29** |
| Envio B3 simulado, reconciliação simulada, tela de resolução, 4 caminhos | 24 | **26–28** |
| Transições novas T-01 a T-04 | — | **6–10** |
| Relógio de prazo legal, dias úteis, alertas | — | **6–8** |
| Painel de backoffice | 24 | 24 |
| Área do membro | 16 | 16 |
| Páginas públicas | 8 | 8 |
| Segurança: isolamento + testes de autorização | 12 | 12 |
| Segurança: criptografia + gestão de chaves | 16 | 16 |
| Segurança: logs + exportação controlada | 12 | 12 |
| Testes, deploy, ajustes | 24 | 24 |
| **Total** | **244** | **273–291** |

De onde vêm as 29–47h a mais:

| Motivo | Horas | Fonte |
|---|---|---|
| Formulário com ~45 campos, condicionais e listas fechadas, no lugar de "poucos campos" | +12–20 | B3 §2 |
| Simulação de assinatura com saída e retorno do provedor | +3–5 | Clicksign §3 |
| Simulação de consulta antes de reenviar e de erro automático | +2–4 | B3 §5 |
| Transições que faltavam na máquina de estados | +6–10 | Regras §7 |
| Prazo legal de 30 dias úteis | +6–8 | Panorama §8.3 |

### Fase 2 — Assinatura real
**Escopo fechado, depois da escolha do fornecedor.**

| Fornecedor e cenário | Horas | Ponto médio |
|---|---|---|
| Clicksign, só e-CPF | 51–75 | 62 |
| Lacuna, só certificado em nuvem | 57–78 | 67 |
| Lacuna, só token físico | 68–94 | 80 |
| Lacuna, nuvem e token | 86–118 | 100 |

Fontes: `estudo-assinatura-api-clicksign.md` §10 e `estudo-assinatura-api-lacuna.md` §10.

### Fase 3 — B3 real
**Escopo fechado, com o ciclo de certificação fora do prazo contratual.**

**65–98h**, ponto médio 80h. A maior incerteza é se as listas de produto, safra e unidade vêm por endpoint ou por arquivo (pendência 2.4, ~8h). Fonte: `estudo-api-b3.md` §8.

O acesso está aprovado. O ciclo de certificação técnica depende do tempo de resposta do SAT da B3.

---

## O número total

| Cenário | F0 | F1 | F2 | F3 | **Total** | Equivalente a R$ 300/h |
|---|---|---|---|---|---|---|
| Otimista: Clicksign, respostas favoráveis | 24 | 273 | 51 | 65 | **413h** | R$ 123.900 |
| Médio: Lacuna nuvem, pontos médios | 28 | 282 | 67 | 80 | **457h** | R$ 137.100 |
| Pessimista: Lacuna com os dois certificados | 32 | 291 | 118 | 98 | **539h** | R$ 161.700 |

| Momento | Horas |
|---|---|
| Dossiê original | 200 |
| Rev. 2 do plano | ~332–356 |
| Rev. 3 do plano | **~413–539** |

A coluna em reais é referência. Preço de escopo fechado não é hora vezes taxa (ver nota comercial).

### Por que subiu de novo

As Fases 2 e 3 dobraram. As duas estimativas anteriores foram feitas sem ler a documentação dos fornecedores, e três premissas caíram quando ela foi lida:

1. **Certificado em nuvem não é assinatura embutida.** Existe saída para o provedor, com estados e suporte próprios.
2. **Webhook não é confiável por padrão.** Nenhum fornecedor documenta reentrega, e a B3 não tem webhook para CPR. Toda integração ganhou um job de reconciliação.
3. **A B3 não é uma API key.** É mTLS, pinning, listas de domínio, consulta antes de reenviar e um ciclo de certificação com o SAT.

### Alavancas para reduzir

| Corte | Economia | Custo do corte |
|---|---|---|
| Um só tipo de certificado no MVP, se Lacuna | 18–40h | Membros com o outro tipo esperam a fase seguinte |
| Adiar criptografia de aplicação, mantendo isolamento e logs | 16h | Dump de banco fica exposto. Aceitável só antes de dado real |
| Reassinatura como "cancelar e criar registro vinculado", sem fluxo próprio | 8–12h | Operador faz em dois passos o que seria um |
| 2 papéis de backoffice em vez de 3 | 6h | Quem aprova cadastro enxerga termos comerciais |
| Landing mínima | 6h | Nenhum |
| CPRs fora do SCR (se o escritório confirmar) | 4h | Nenhum, se não se aplica |
| Adiar a extensão do carimbo de arquivamento (Lacuna) para depois do lançamento | 3–4h | Nenhum no primeiro ano. O carimbo vence em anos |
| **Juntas** | **61–88h** | |

Não recomendo cortar isolamento por registro, logs de auditoria, consulta antes de reenviar nem o relógio de prazo legal. Os dois primeiros protegem o cliente de concorrente, os dois últimos protegem de CPR duplicada e de CPR vencida.

---

## Escolha do fornecedor de assinatura

> **Atualização 12/09:** se o cliente aceitar assinatura por e-mail sem certificado (pendência 1.25), a comparação abaixo perde a maior parte do sentido. As vantagens da Lacuna são todas de certificado, e a Clicksign vira a candidata natural, com Fase 2 de ~49–72h. Ver `estudo-assinatura-sem-certificado.md` §5. A tabela abaixo continua valendo para o cenário com ICP-Brasil.

Dois finalistas.

| Critério | Clicksign | Lacuna |
|---|---|---|
| Certificado em nuvem | 3 provedores confirmados. Redireciona ao app | 5 provedores. Redireciona na sessão do Core; fica na tela com PKI Express |
| Token físico | Web PKI dentro do widget. ICP no widget não confirmado | Web PKI na nossa página, Windows, Linux e macOS. Sem Safari |
| e-CNPJ, emitente PJ | **Não** | Sim |
| Fluxo pronto (convite, ordem, lembrete) | Sim | Não. Só no Signer, a R$ 1.750/mês |
| O PDF sai da nossa infraestrutura | Sim, e fica guardado | Depende da rota. Pendência 4.5 |
| Carimbo do tempo | À parte, preço não publicado | R$ 0,15 por carimbo, publicado |
| Prova de longo prazo | Perfil PAdES não documentado | Endpoint de extensão de carimbo de arquivamento |
| Sandbox | Grátis, sem contrato, imediato | Web PKI grátis em localhost, 150 transações grátis por 3 meses, certificados de teste |
| Opex com 100 CPRs/mês | R$ 119, sem carimbo | R$ 200, com carimbo |
| Fase 2 | 51–75h | 57–118h |

### Recomendação, condicionada

**Clicksign vence** se as três condições valerem ao mesmo tempo: emitente sempre pessoa física, membros com certificado em nuvem, e o cliente aceita o contrato guardado no fornecedor. Integra mais rápido, mais barato, e com fluxo pronto.

**Lacuna vence** se qualquer uma falhar: cooperativa emitindo, membros com token físico, ou o contrato não pode sair da nossa infraestrutura. Nesse último caso, só se a pendência 4.5 confirmar a rota por hash.

A resposta sai das pendências 1.1, 1.3, 1.8 e 4.5. Não contratar nada antes delas.

---

## Telas do mockup

17 telas principais e 8 auxiliares em `mockup/`, com roteiro em `mockup/README.md`. As auxiliares são a confirmação de solicitação, as duas formas de assinar, o detalhe de registro concluído e uma confirmação para cada caminho de resolução.

Identidade visual em `estudo-ui-identidade.md`. Recomendação: direção **Cartório**, com números em monoespaçada. Só entra depois do fluxo aprovado.

---

## Como escrever para este cliente

- Estado em português comum.
- Uma ação principal por tela.
- Zero jargão de software na interface do membro.
- Linha do tempo em linguagem de fato.
- Erro sempre com o próximo passo.
- **Na assinatura, cada passo fora da nossa tela anunciado antes**: "você vai confirmar no aplicativo do seu certificado e voltar para cá".

A tela de resolução do backoffice é a exceção: mostra payload e resposta da B3 inteiros.

---

## Nota comercial

A faixa total varia 30% entre otimista e pessimista, e quase toda a variação está nas Fases 2 e 3, que dependem de fornecedor e da documentação fechada da B3.

**Recomendação:** propor preço fechado só para a **Fase 1**, que depende de decisões do cliente e não de terceiros. Fases 2 e 3 entram na mesma proposta como estimativa com faixa, e viram preço fechado em aditivo quando as respostas chegarem. Isso evita que você absorva uma diferença de até 100h que ninguém consegue prever hoje.

Continua valendo: escopo fechado transfere risco de estimativa para você. Ou o preço carrega prêmio sobre a taxa horária, ou o contrato tem cláusula de escopo com gatilho de aditivo.

Duas linhas de custo recorrente ainda sem número, que o cliente precisa conhecer antes de aceitar o modelo de negócio: **tarifa da B3 por registro** (pendência 2.15) e **certificado dos membros**, se o clube decidir bancar (pendência 1.7).
