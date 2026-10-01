# Clube do Café — Plano do Projeto

**Revisão 4** · 01/10/2026 · complementa `entendimento-do-projeto.md` (rev. 5)

---

## Onde estamos

**Fase 0, validação de escopo.** As seis frentes de estudo terminaram, a consolidação da rev. 4 foi feita, e a reunião de validação com o cliente aconteceu em 24/09/2026, trazendo mudança de modelo (`planejamento/atas-reunioes-wado.md`, `consolidacao-rev5.md`). O que falta para sair da Fase 0:

| # | Tarefa | Quem | Depende de |
|---|---|---|---|
| 1 | ~~Commitar o estudo da Lacuna~~ Feito | — | — |
| 2 | Enviar os dois e-mails ao escritório sócio (`pendencias.md` §2) | Você | — |
| 3 | Enviar as perguntas à Clicksign e à Lacuna (§3 e §4) | Você | — |
| 4 | ~~Ajustar telas do mockup para a reunião de 12/09~~ Feito | — | — |
| 5 | ~~Reunião de validação com o cliente~~ Feita em 24/09/2026 | — | — |
| 6 | Escolher o fornecedor de assinatura | Você + cliente | 3 |
| 7 | ~~Revisão 5: aplicar as mudanças da reunião de 24/09~~ Feito em 01/10/2026 (esta revisão) | Sessão Claude | — |
| 8 | **Ampliar o mockup para cobrir o escopo novo inteiro** (proposta de adesão, envelope, armazéns, árbitros, amostras, vídeo), para o cliente validar a ideia completa | Sessão Claude | 7 |
| 9 | Enviar as novas pendências ao cliente e ao escritório (`pendencias.md`, itens de 24/09) | Você | 7 |
| 10 | Estimar e precificar cada módulo em separado, para o cliente compor o MVP dele | Você + sessão Claude | 8, 9 |
| 11 | Proposta de escopo fechado do núcleo | Você | 10 |

A tarefa 8 está em andamento nesta sessão (01/10/2026).

### Mudança de estratégia em 01/10/2026

Até a rev. 3 do plano, a lógica era: mockup enxuto do fluxo essencial → validar → orçar → construir. A reunião de 24/09 mudou tanto a forma de entrada quanto a de assinatura, e trouxe domínio inteiramente novo (armazéns, árbitros, amostras, vídeo). Em vez de cortar esse escopo novo do mockup para não atrasar o preço, a decisão foi: **mostrar a ideia completa primeiro.** O mockup cresce para cobrir tudo, inclusive o que ainda não está maduro nas pendências. Depois, cada bloco é estimado e precificado em separado, e o cliente compõe o MVP dele conforme o orçamento disponível — maximizando faturamento sem travar a Fase 0 numa única proposta monolítica.

### Ajustes do mockup antes da reunião de 24/09, feitos em 12/09

| Tela | Ajuste |
|---|---|
| `02b` | Prazo de análise coerente com a regra escolhida (dois ou três dias úteis) |
| `06` | Acrescentar situação, produção, imóvel, acondicionamento, garantia, indexador, vencimento, finalidade. Marcar bebida e peneira como "vai no contrato" |
| `09` | Mostrar o caso em que o membro sai para o aplicativo do certificado e volta. Sem citar fornecedor |
| `15` | Ordenar e exibir por prazo legal restante |
| `16a` | Mostrar a consulta à B3 antes do reenvio, e o resultado dela |

### Ajustes do mockup para a ampliação de 01/10

| Tela | Ajuste |
|---|---|
| `02` | Vira "Propor adesão": de 1 a 3 recomendantes dinâmicos (não mais 2 fixos), cada um com telefone e texto de recomendação; anexos viram área de arrastar/selecionar, múltiplos arquivos |
| `02c` (nova) | Recomendante assina a indicação |
| `02b` | Mensagem reflete a fila do comitê, não mais um prazo fixo em dias |
| `03b` (nova) | Aceite dos termos do clube no primeiro acesso |
| `05` | Qualquer parte pode preencher envolvendo a outra. Vira etapa 1 de 4 |
| `05b` (nova) | Etapa 2 de 4: decidir se abre a **Mesa de Negociação**, antes mesmo de preencher objeto e valor |
| `06` / `06b` (nova) | Etapa 3 de 4: objeto e valor, com campos reduzidos a produto, classificação, safra, quantidade, preço, liquidação (só física por ora), região/armazém e data de entrega. `06b` é a mesma etapa com a Mesa ativa, em layout de tela compartilhada |
| `07` / `07b` (nova) | Etapa 4 de 4: revisão. `07b` mantém a Mesa ativa e vai direto para a assinatura, sem passar pelo resumo do envelope |
| `08` | Vira resumo rápido do acordado — não mostra mais o documento inteiro |
| `08b`, `08c` (novas) | Documentos completos (contrato, CPR), um clique de distância do resumo |
| `09` / `09-mesa` / `09-mesa-concluído` (novas as duas últimas) | Assinatura do envelope. Com a Mesa ativa, a câmera fica ligada até a assinatura completa, terminando com a confirmação de registro na B3 |
| `12b`, `12c` (novas) | Relatório do comitê de admissão e registro da decisão pelo backoffice |
| `13` | Reflete proponente + recomendantes (número variável), diligência, parecer do comitê |
| `18`–`20` (novas) | Armazéns credenciados, árbitros, amostras — localidade padrão: Varginha/MG e região (Sul de Minas, Cerrado Mineiro, Mogiana) |

A tela `09-video` (sala de vídeo isolada) da primeira rodada de 01/10 foi **substituída**: em vez de uma página de chamada separada, a Mesa de Negociação agora acompanha o fluxo de criação do registro do início ao fim, como painel fixo ao lado do conteúdo.

---

## Estratégia

Construir o sistema inteiro com assinatura e B3 simuladas, entregar funcionando de ponta a ponta, e trocar cada simulação pela integração real depois. A simulação da assinatura precisa ter os **dois modos de entrega**, embutido e redirecionado, para que a escolha do fornecedor não mexa na Fase 1.

**Desde 01/10:** a simulação cobre também o envelope único (vários documentos, uma assinatura por signatário) e a janela curta configurável. A sala de vídeo é sempre simulada no MVP, mesmo quando contratada depois — é serviço de terceiro (whitelabel), não construído por nós.

---

## Fases

### Fase 0 — Validação de escopo
**Hora, R$ 300/h.** Planejado: 24–32h. Horas reais até aqui: registrar.

### Fase 1 — Sistema completo, com simulações (núcleo)
**Escopo fechado.** A rev. 4 do plano ainda não fecha faixa nova: a reunião de 24/09 mudou blocos inteiros (proposta de adesão, assinatura) e a reestimativa fina depende do mockup ampliado (tarefa 8, em andamento). As direções de mudança, por bloco, em relação à rev. 3:

| Bloco | Rev. 3 | Direção na rev. 4 | Por quê |
|---|---|---|---|
| Setup, autenticação, papéis, MFA | 20 | 20, +6 se existir `comite_admissao` | Pendência 1.28 |
| Proposta de adesão (era "solicitação + fila") | 20 | **↑, estimativa ainda aberta** | Recomendantes, assinatura deles, fila do comitê, relatório impresso/tela, diligência — mais telas e mais estado que uma fila simples |
| Onboarding e termos do clube | — | **Novo bloco, estimativa ainda aberta** | RN-114, RN-134 a RN-136: assinatura do contrato-mãe, versionamento, reassinatura obrigatória |
| Formulário de registro com os campos da B3 | 36–44 | 36–44, + campo de modalidade de liquidação | Sem mudança grande aqui; a modalidade é um campo a mais |
| Geração de documento, 1 modelo | 20 | 20 | Sem mudança |
| Envelope de assinatura (era "assinatura simulada") | 27–29 | **↑, estimativa ainda aberta** | Agrupar múltiplos documentos num evento só, janela curta configurável, visualização completa antes de assinar — mais complexo que um documento com dois modos de entrega |
| Pré-validação contra domínios/formatos da B3 | — | **Novo bloco, estimativa ainda aberta** | T-08 na máquina de estados. Depende de ter o layout fechado da B3 (frente 3) |
| Envio B3 simulado, reconciliação simulada, tela de resolução, 4 caminhos | 26–28 | 26–28 | Lógica não muda; só ganha o gatilho da pré-validação antes dela |
| Transições novas T-01 a T-09 | 6–10 | **8–14** | T-08 e T-09 somam-se às quatro já estimadas |
| Relógio de prazo legal, dias úteis, alertas | 6–8 | 6–8 | Sem mudança |
| Painel de backoffice | 24 | 24, + relatório do comitê | Pendência 1.28 decide se é impressão simples ou tela própria |
| Área do membro | 16 | 16 | Sem mudança |
| Páginas públicas | 8 | 8 | Sem mudança |
| Segurança: isolamento + testes de autorização | 12 | 12 | Sem mudança |
| Segurança: criptografia + gestão de chaves | 16 | 16 | Sem mudança |
| Segurança: logs + exportação controlada | 12 | 12 | Sem mudança |
| Testes, deploy, ajustes | 24 | 24 | Sem mudança |
| **Total rev. 3 (referência)** | **273–291** | — | — |

**Não há total novo ainda.** Os três blocos marcados "estimativa ainda aberta" dependem do mockup ampliado (tarefa 8) para virar número — construir a tela é, historicamente, o que revela o tamanho real de um bloco deste projeto (ver "O escopo cresceu de novo" em `entendimento-do-projeto.md`).

De onde vêm as 29–47h a mais da rev. 2 para a rev. 3:

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

## Fase 4 — Escopo novo, módulos opcionais (sem estimativa fechada)

Nasceu na reunião de 24/09/2026. Cada módulo é **independente dos outros e do núcleo**: o cliente pode contratar um, todos, ou nenhum, conforme o orçamento. Faixas abaixo são **placeholders de ordem de grandeza**, por analogia a blocos parecidos já estimados no núcleo — não cotar com elas ainda. Viram número depois que o mockup ampliado (tarefa 8) existir e as pendências 1.36 a 1.39 e 2.21 forem respondidas.

| Módulo | Ordem de grandeza | Por quê | Depende de |
|---|---|---|---|
| Modalidade de liquidação (campo + regra) | 4–8h | Um campo novo no formulário, mas com lógica condicional (some o bloco de armazém fora da modalidade física) | Pendência 1.36/2.21 |
| Armazéns credenciados + fluxo de credenciamento | 20–32h | Cadastro, fluxo de aprovação, listagem por região — tamanho parecido com a fila de propostas | Pendência 1.37 |
| Árbitros classificadores + checagem de imparcialidade | 16–28h | Cadastro simples, mas a checagem de vínculo com as partes (RN-129/130) é a parte não trivial | Pendência 1.38 |
| Fluxo de amostras | 16–24h | Depende de como fica o caso de amostra reprovada (RN-132) | Pendência 1.39 |
| Mesa de Negociação (integração whitelabel) | 16–26h | Integração de terceiro, não construção de videochamada própria. Subiu da faixa original (12–20h) depois da UX de 01/10: a Mesa precisa acompanhar 3 telas do fluxo de criação (objeto, revisão, assinatura) em vez de só abrir perto da assinatura | Escolha do provedor (Whereby ou similar), fora do escopo desta sessão |
| **Soma, se tudo entrar** | **72–118h** | | |

Nenhuma linha acima inclui o custo recorrente do provedor de vídeo nem eventual tarifa de credenciamento de armazém — ainda não levantados.

---

## O número total (núcleo)

**Esta tabela cobre só o núcleo** (Fases 0 a 3). Os três blocos "estimativa ainda aberta" da Fase 1 rev. 4 ainda não entraram aqui — os valores abaixo são os da rev. 3, mantidos como última base firme até o mockup ampliado fechar os números novos. A Fase 4 (escopo novo) soma-se à parte, por fora.

| Cenário | F0 | F1 | F2 | F3 | **Total núcleo** | Equivalente a R$ 300/h |
|---|---|---|---|---|---|---|
| Otimista: Clicksign, respostas favoráveis | 24 | 273 | 51 | 65 | **413h** | R$ 123.900 |
| Médio: Lacuna nuvem, pontos médios | 28 | 282 | 67 | 80 | **457h** | R$ 137.100 |
| Pessimista: Lacuna com os dois certificados | 32 | 291 | 118 | 98 | **539h** | R$ 161.700 |

Com a Fase 4 completa (módulos novos), somar 72–118h, ou R$ 21.600–35.400 a mais.

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

Ampliado em 01/10/2026 para cobrir o escopo novo inteiro (proposta de adesão, envelope de assinatura com vídeo, armazéns, árbitros, amostras), além das 17 telas principais e 8 auxiliares de 12/09. Lista completa e roteiro em `mockup/README.md`.

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

A faixa total do núcleo varia 30% entre otimista e pessimista, e quase toda a variação está nas Fases 2 e 3, que dependem de fornecedor e da documentação fechada da B3.

**Recomendação:** propor preço fechado só para a **Fase 1**, que depende de decisões do cliente e não de terceiros. Fases 2 e 3 entram na mesma proposta como estimativa com faixa, e viram preço fechado em aditivo quando as respostas chegarem. Isso evita que você absorva uma diferença de até 100h que ninguém consegue prever hoje.

**Desde 01/10:** a Fase 4 (escopo novo) nunca entra como preço fechado nesta rodada — cada módulo vira uma proposta própria, depois que o cliente vir o mockup ampliado e decidir o que cabe no orçamento dele. Isso também significa mais faturamento potencial por hora investida em manter o mockup completo e navegável.

Continua valendo: escopo fechado transfere risco de estimativa para você. Ou o preço carrega prêmio sobre a taxa horária, ou o contrato tem cláusula de escopo com gatilho de aditivo.

Duas linhas de custo recorrente ainda sem número, que o cliente precisa conhecer antes de aceitar o modelo de negócio: **tarifa da B3 por registro** (pendência 2.15) e **certificado dos membros**, se o clube decidir bancar (pendência 1.7).
