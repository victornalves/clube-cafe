# Consolidação das Frentes — Revisão 4

12/09/2026 · lê os sete resultados das seis frentes e registra o que eles mudaram nos documentos principais.

Este arquivo é o registro da consolidação. Os documentos principais já estão atualizados; aqui fica o porquê de cada mudança e a fonte.

---

## Resultado por frente

| Frente | Documento | O que mudou no projeto |
|---|---|---|
| 1 | `estudo-assinatura-panorama.md` | ICP-Brasil é escolha do cliente, a lei admite outros níveis. Existe prazo legal de 30 dias úteis para registrar. Certificado em nuvem não garante assinatura embutida |
| 2a | `estudo-assinatura-api-clicksign.md` | Fase 2 com Clicksign: 51–75h. O documento fica guardado também na Clicksign. Três provedores de nuvem confirmados, não seis. Só e-CPF |
| 2b | `estudo-assinatura-api-lacuna.md` | Fase 2 com Lacuna: 57–118h conforme o tipo de certificado. Preço publicado, R$ 200/mês de mínimo. Única que cobre token, nuvem e e-CNPJ |
| 3 | `estudo-api-b3.md` | Fase 3: 65–98h. A credencial é um pacote mTLS, não uma API key. Sem idempotência: reenvio exige consulta antes. Formulário real tem ~45 campos |
| 4 | `regras-de-negocio.md` + 5 diagramas | 100 regras, 32 decisões pendentes do cliente, 8 lacunas na máquina de estados |
| 5 | `estudo-ui-identidade.md` | Três direções. Recomenda Cartório com números em monoespaçada. Não entra no mockup |
| 6 | `mockup/` | 24 telas, roteiro de reunião, 16 perguntas que só apareceram ao desenhar |

---

## Contradições com os documentos principais

Todas aplicadas na revisão 4.

| # | Tema | O doc dizia | O estudo mostrou | Fonte | Aplicado em |
|---|---|---|---|---|---|
| C-01 | Nível de assinatura | ICP-Brasil é requisito confirmado | Requisito do cliente. A Lei 8.929/1994 admite assinatura simples, avançada ou qualificada na CPR; com garantia real o mínimo sobe para avançada. Número do artigo ainda a conferir pelo escritório | Panorama §3, §8.1 e nota de conferência | entendimento, regras RN-58 |
| C-02 | Prazo de registro | Nenhum | 30 dias úteis entre emissão e registro (art. 12, redação da Lei 14.421/2022) | Panorama §8.3, B3 §4 | máquina, plano, regras RN-93 |
| C-03 | Credencial B3 | "Falta só pedir a API key" | Pacote de acesso: certificado mTLS (`.p12`), `client_id`, `client_secret` e senha | B3 §1, §10.1 | entendimento, arquitetura, plano |
| C-04 | Tamanho da credencial | Um valor no cofre | Nove valores por ambiente, um deles binário | B3 §7 | arquitetura |
| C-05 | Caminho 1, retry | Reenvia o mesmo payload | A B3 não documenta idempotência. Timeout e 5xx disparam consulta por Número de Controle; só reenvia se não achar | B3 §5 | máquina |
| C-06 | Gate da Fase 3 | Sem gate externo | O acesso não tem gate. O ciclo de certificação técnica depende do tempo de resposta do SAT da B3 | B3 §10.4 | plano |
| C-07 | Horas da Fase 3 | 32–40h | 65–98h, ponto médio 80h | B3 §8 | plano |
| C-08 | Assinatura embutida | Nuvem mantém quase tudo na nossa tela | Depende da rota. Clicksign e sessão do Rest PKI Core redirecionam. Só fluxo push (Bird ID, NeoID) ou PWD da Lacuna ficam na tela | Panorama §8.2, Clicksign §3, Lacuna §3 | entendimento |
| C-09 | Horas da Fase 2 | 32–40h | Clicksign 51–75h. Lacuna 57–78h nuvem, 68–94h token, 86–118h os dois | Clicksign §10, Lacuna §10 | plano |
| C-10 | Guarda do documento | "Queremos guardar nós" | Clicksign guarda também, em painel com controle de acesso deles. Lacuna Core e Signer também. Só o Rest PKI clássico em assinatura remota recebe apenas o hash | Clicksign §7, Lacuna §7 | arquitetura |
| C-11 | Corretor | Parte do registro | O layout da B3 não tem campo de corretor. Ele existe no documento, não no registro | B3 §2 | entendimento, regras |
| C-12 | Formulário | Poucos campos: partes, objeto, data, valor | ~45 campos no layout B3, seis com domínio fechado vindo de arquivo da B3, blocos condicionais (SCR, garantia, depósito) | B3 §2 | plano, regras §3.2 |
| C-13 | Opex | R$ 295/mês, sem detalhe | A linha de assinatura cabe: Clicksign R$ 39–119 sem carimbo do tempo, Lacuna R$ 200 com carimbo. Tarifa da B3 não levantada | Clicksign §11, Lacuna §11 | plano |

---

## Contradições entre os próprios estudos

O panorama foi escrito antes dos estudos de API. Onde divergem, valem os estudos de API. O panorama ganhou um aviso no topo e não foi reescrito.

| # | O panorama dizia | O estudo de API mostrou |
|---|---|---|
| C-14 | Clicksign documenta seis provedores de nuvem | Três confirmados nas páginas de comportamento: SafeID, BirdID, VIDaaS |
| C-15 | Clicksign: preço confuso, API a partir de plano maior | Preço cheio publicado. API e widget disponíveis desde o Start |
| C-16 | Lacuna: preço não publicado | Tabela publicada, mínimo de R$ 200/mês, licença do Web PKI isenta com Rest PKI em nuvem |
| C-17 | Lacuna: webhook não se aplica | Rest PKI Core tem 1 evento, Signer tem 9 |
| C-18 | Lacuna: nenhuma tela de terceiro | Verdade para Web PKI e PKI Express. A sessão do Rest PKI Core é redirect |
| C-19 | Links da Lacuna com `.html` | Devolvem 404 desde a migração da documentação |

---

## Achados novos desta consolidação

Nenhum estudo isolado enxergava estes, porque aparecem só cruzando dois ou mais.

### I-01. Na Lacuna, a rota mais segura e a rota estimada são diferentes
O estudo da Lacuna diz, na seção 7, que só o **Rest PKI clássico** em assinatura remota recebe apenas o hash do documento. As estimativas da seção 10 usam o **Rest PKI Core**, cujo `POST /api/signature` recebe `FileReferenceModel`. A isenção de licença do Web PKI está escrita para "Rest PKI em nuvem", sem citar o Core.

Consequência: o argumento de segurança a favor da Lacuna depende de uma rota que não foi a estimada. **Perguntar à Lacuna:** o Core aceita assinatura só com hash? A isenção do Web PKI vale para o Core?

### I-02. O prazo legal pode estar começando antes da assinatura
`regras-de-negocio.md` §3.2 define a data de emissão como "data do envio para assinatura". Se for assim, os 30 dias úteis correm durante a coleta de assinaturas, a correção e a reassinatura. A alternativa é a data de emissão ser a da última assinatura. **Decisão do escritório sócio.** Define quando o relógio liga.

### I-03. Retry automático contra human in the loop
A decisão da rev. 3 foi que toda falha na B3 gera alerta e uma pessoa decide, inclusive o retry. O estudo da B3 propõe tratar automaticamente o que é claramente transitório: renovar token uma vez no 401, backoff no 429 e 503, consultar antes de reenviar no timeout. `regras-de-negocio.md` já tinha anotado a tensão (L-07).

**Proposta na máquina de estados rev. 2:** automático para transitório, com limite de tentativas, e humano para todo o resto, incluindo todo 422. **Precisa do seu aceite**, porque muda uma decisão sua.

### I-04. Aditivo depois de registrado é outra operação na B3
A lacuna L-04 (aditivo a partir de `REGISTRADO`) depende de aditamento de CPR na B3, que é operação separada do registro e não está em nenhuma estimativa. **Proposta: fora do MVP.** `REGISTRADO` continua terminal na plataforma.

### I-05. Ninguém levantou a tarifa de registro da B3
A B3 cobra pelo registro. Nenhuma frente levantou valor nem quem paga: escritório, clube ou membro. Afeta o modelo de monetização, que ainda é pergunta aberta desde o dossiê. **Perguntar ao escritório.**

### I-06. Falha de certificado não avisa ninguém
A Clicksign não tem evento para falha de autenticação por certificado. O signatário que não encontra certificado some em silêncio e o registro fica parado em `AGUARDANDO_ASSINATURAS`. Só um relógio detecta. **Aplicado:** alerta de assinatura parada na máquina de estados rev. 2.

---

## Divergências entre o mockup e os estudos

O mockup foi feito antes dos estudos de assinatura e da B3. Nada disso invalida a reunião de fluxo, mas cinco telas mostram algo que já sabemos estar errado.

| # | Tela | Mostra | Deveria mostrar | Fonte |
|---|---|---|---|---|
| M-01 | `02b` | "Prazo médio de dois dias úteis" | `regras-de-negocio.md` RN-88 propõe três. Escolher um número | Regras |
| M-02 | `06` | Espécie, safra, bebida, tipo, peneira, qualidade, quantidade, preço, pagamento, entrega, frete | Faltam situação (a produzir/produzido), produção (própria/terceiros), imóvel, acondicionamento, tipo de garantia, indexador, vencimento, finalidade. Bebida e peneira não existem no registro da B3, só no documento | B3 §2 |
| M-03 | `09` | Certificado em nuvem assinando "dentro desta tela" | Só é verdade com fluxo push ou PWD. Com Clicksign ou Rest PKI Core há saída para o provedor | Clicksign §3, Lacuna §4 |
| M-04 | `15` | Fila ordenada por tempo parado | Fila ordenada por prazo legal restante | Panorama §8.3, B3 §4 |
| M-05 | `16a` | Reenviar direto | Consultar a B3 antes de reenviar, e mostrar o resultado da consulta | B3 §5 |

Ajustes listados como tarefa em `plano-do-projeto.md`, antes da reunião.

---

## O que esta consolidação não fez, de propósito

| Item | Por quê |
|---|---|
| Redesenhar os diagramas 02, 03 e 04 | A máquina de estados rev. 2 tem sete transições novas marcadas como proposta. Redesenhar antes do aceite do cliente é desenhar duas vezes |
| Ajustar o mockup | É trabalho de tela, separado. Listado no plano |
| Reescrever os estudos | São registro do que se sabia em cada momento. Ganharam aviso onde foram superados |
| Escolher o fornecedor de assinatura | Depende da resposta do cliente sobre tipo de certificado e emitente PJ. O plano traz a recomendação condicionada |
| Emitir proposta | A faixa de horas ainda varia 30% por falta de respostas externas. Ver `pendencias.md` |
