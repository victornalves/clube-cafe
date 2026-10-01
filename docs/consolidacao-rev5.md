# Consolidação — Revisão 5

01/10/2026 · lê a reunião de validação de 24/09/2026 com o cliente (Victor + Wado Aranha) e os esclarecimentos trocados por mensagem em 01/10/2026, e registra o que eles mudaram nos documentos principais.

Fonte primária: `planejamento/atas-reunioes-wado.md`. Este arquivo é o registro do porquê; os documentos principais já estão atualizados.

---

## Resumo da reunião

Diferente das consolidações anteriores (rev. 4, seis frentes de estudo técnico), esta reunião não trouxe dado técnico novo sobre fornecedor ou B3. Trouxe **mudança de modelo de produto**, em cinco frentes:

1. Correção jurídica: CPR é física, não financeira — não muda escopo, só remove um mal-entendido do escritório.
2. Entrada no clube virou um processo social (recomendação de pares, comitê), não administrativo simples.
3. Assinatura virou um evento único e rápido (envelope, minutos), não um processo de dias com lembretes.
4. Falha de registro na B3 passou de "corrige depois" para "previne antes" — mudança de princípio de risco, não só de fluxo.
5. Surgiu um domínio de negócio inteiramente novo: armazéns, árbitros, amostras, vídeo de negociação.

---

## O que mudou, documento por documento

| Documento | Mudança principal |
|---|---|
| `entendimento-do-projeto.md` | Rev. 5. Escopo dividido em núcleo + escopo novo. Nova decisão de produto (prevenção antes de correção). Seis perguntas-chave em vez de cinco |
| `regras-de-negocio.md` | Seção 1 inteira reescrita (era "Entrada no clube", virou "Proposta de adesão"). RN-08, RN-18 a 23, RN-25 a 29, RN-90 a 92 retiradas. ~25 regras novas (RN-101 a RN-133), cobrindo recomendantes, comitê, termos do clube, envelope, armazéns, árbitros, amostras |
| `maquina-de-estados.md` | Rev. 3. Novo estado `PRE_VALIDANDO` e transição T-08 (prevenção). Novo estado `JANELA_EXPIRADA` e transição T-09 (envelope). Nova máquina separada para a proposta de adesão. Lacuna L-02 fechada |
| `pendencias.md` | Rev. 5. ~15 perguntas novas (1.27 a 1.39, 2.21 a 2.24). Pergunta 1.4 permanece fechada. Estratégia de fechamento da proposta mudou: núcleo primeiro, módulos novos depois |
| `plano-do-projeto.md` | Rev. 4. Três blocos da Fase 1 ficam com estimativa reaberta (proposta de adesão, onboarding/termos, envelope). Nova Fase 4 com placeholders de ordem de grandeza para os módulos novos. Estratégia de "mockup amplo, preço modular" documentada |
| `controle-de-horas.md` | Horas desta sessão registradas como item a preencher |
| `README.md` | Decisões fechadas e perguntas-chave atualizadas |
| `planejamento/atas-reunioes-wado.md` | Novo. Versão limpa das notas brutas das reuniões 1 e 2 |

---

## Decisões do cliente, com data

| # | Decisão | Onde |
|---|---|---|
| 1 | CPR é física; a análise de CPR financeira do escritório não se aplica | `entendimento-do-projeto.md` |
| 2 | Usar "membro", nunca "sócio" | Todos os documentos |
| 3 | Entrada é proposta de adesão, com 2 recomendantes que assinam, avaliada por comitê de admissão semanal | `regras-de-negocio.md` §1 |
| 4 | Sem bloqueio automático de proponente recusado | RN-110 |
| 5 | Qualquer parte membro cria o registro, envolvendo a outra; corretor opcional | RN-52 |
| 6 | Assinatura em envelope único, visualização completa antes de assinar | RN-116 a RN-118 |
| 7 | Janela de assinatura configurável, 15 minutos de partida | RN-119 |
| 8 | Cancelamento sem assinatura não exige motivo em texto | RN-72 |
| 9 | Membro assina termos do clube na entrada, reassina quando a versão mudar | RN-114, RN-134 a RN-136 |
| 10 | Falha de registro na B3 é "erro grave"; precisa de prevenção antes da assinatura | `maquina-de-estados.md`, T-08 |
| 11 | Escopo novo: modalidade de liquidação, armazéns, árbitros, amostras | RN-123 a RN-132 |
| 12 | Serviço de arbitragem de litígio roda fora da plataforma | RN-133 |
| 13 | Mesa de Negociação (whitelabel) é recurso opcional, do início do registro até a assinatura | RN-121, RN-122, RN-137 a RN-139 |
| 14 | Estratégia: mockup amplo cobrindo tudo, preço modular por bloco depois | `plano-do-projeto.md` |

---

## O que ficou pendente de esclarecimento do próprio cliente

A reunião trouxe dois pontos em que o próprio Wado não tinha certeza, e precisam ser levados de volta a ele (não ao escritório):

### Recomendante externo assina como?
A Hipótese A (RN-62) diz que todo signatário de registro é membro. Mas um recomendante da proposta de adesão pode ser "alguém de renome fora do clube". Como essa pessoa assina a recomendação sem ser membro? É uma exceção pontual, ou o recomendante externo precisa de algum tipo de conta mínima? Pendência 1.27.

### O que é washout e liquidação por diferença, numa CPR só física?
O próprio Wado disse não ter certeza — "possíveis conclusões precipitadas de CPRs físicas". Como o escopo do clube é CPR física (ver "Correção jurídica" acima), e washout/diferença/antecipada soam como liquidação financeira, pode haver uma tensão a esclarecer com ele e, depois, confirmar com o escritório. Pendências 1.36 e 2.21.

### O que é o item "Seguro"?
Não ficou claro se é seguro por operação (produto) ou apólice do próprio clube (mitigação de risco interno). Pendência 1.29.

---

## O que esta consolidação não fez, de propósito

| Item | Por quê |
|---|---|
| Redesenhar os diagramas `.drawio` | A máquina de estados mudou de forma relevante (novos estados, nova máquina da proposta). Diagramas 01 a 04 estão **desatualizados** e precisam de uma sessão própria de redesenho |
| Reestimar a Fase 1 em número fechado | Os três blocos mudados de verdade dependem do mockup ampliado para revelar o tamanho real — é o padrão já observado nas revisões anteriores |
| Precificar a Fase 4 (escopo novo) | Decisão explícita do cliente: mockup primeiro, preço depois, por módulo |
| Revisar `arquitetura-seguranca.md` | Nenhuma pergunta desta reunião muda ameaça ou controle do documento diretamente, mas o papel `comite_admissao` em potencial (pendência 1.28) e o envelope com múltiplos documentos merecem uma passada quando a Fase 1 reabrir estimativa |
| Resolver as pendências do próprio cliente (recomendante externo, washout, seguro) | Não são decisões desta sessão — precisam da resposta do Wado |

---

## Próximo passo

Ampliar o mockup (`mockup/`) para cobrir proposta de adesão com recomendantes e comitê, envelope de assinatura com sala de vídeo simulada, e os três módulos novos (armazéns, árbitros, amostras). Depois, enviar as pendências novas ao cliente e ao escritório, e reabrir a estimativa da Fase 1 e da Fase 4 a partir do que o mockup revelar.

---

## Adendo — ajustes de UX recebidos em 01/10/2026, mesmo dia

Depois da primeira entrega da rev. 5, o cliente revisou o mockup e pediu ajustes que mudam a UX da Mesa de Negociação e de duas telas. Aplicado no mesmo ciclo, sem nova revisão numerada dos documentos de regra — os números de regra (RN-121 a RN-139) já refletem a versão final.

| Ajuste | O que mudou |
|---|---|
| Recomendantes da proposta de adesão | De 2 fixos para 1 a 3 dinâmicos, cada um com telefone e texto de recomendação próprio. Anexos passam a aceitar múltiplos arquivos, em área de arrastar/selecionar |
| Resumo do envelope (tela 8) | Deixa de mostrar o documento inteiro por padrão. Mostra um resumo rápido do acordado, com os documentos completos a um clique (telas 8b, 8c) — porque o membro já aceitou termos e modelo no onboarding |
| Localidade mockada | Trocada de Patrocínio/MG e Franca/SP para **Varginha/MG**, com Sul de Minas, Cerrado Mineiro e Mogiana como as três regiões de exemplo nos armazéns |
| **Mesa de Negociação** (nome definido nesta rodada, antes "sala de negociação por vídeo") | Deixou de ser uma página de chamada isolada, acessível só perto da assinatura. Agora é um painel que acompanha o fluxo de criação do registro desde a etapa 2 (logo após definir as partes) até a assinatura completa, com o formulário sendo preenchido em tela compartilhada e a câmera ligada até o negócio fechar e ser registrado na B3 |

O fluxo de criação de registro passou de 3 para 4 etapas (Partes → Mesa de Negociação → Objeto e valor → Revisão), e os campos da etapa de objeto foram reduzidos à lista mínima: produto, classificação, safra, quantidade, preço, modalidade de liquidação (só física por ora), região, armazém e data de entrega. Os demais campos (garantia, qualidade, amostra, etc.) ficam escondidos até o formulário real da B3 ser fechado.

Impacto no plano: a estimativa de "Mesa de Negociação" na Fase 4 subiu de 12–20h para 16–26h, porque agora ela precisa acompanhar três telas do fluxo (objeto, revisão, assinatura), não só abrir perto da assinatura.
