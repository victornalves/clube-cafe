# Estudo da API da Clicksign — Assinatura ICP-Brasil

**Frente 2** · 12/09/2026 · complementa `estudo-assinatura-panorama.md`, `plano-do-projeto.md` (rev. 2) e `arquitetura-seguranca.md`

Avalia **apenas a Clicksign**, primeira colocada da trilha A do panorama. A Lacuna é avaliada em documento separado.

---

## O que este documento responde

Fluxo de integração endpoint por endpoint na **API v3 (Envelope)**, autenticação e rotação de token, o que é embutido e o que é redirect, provedores de certificado em nuvem, catálogo de eventos de webhook com HMAC e IP de origem, sandbox, guarda do documento, manifesto e PAdES, tabela de preço cheio recuperada da própria página de planos, estimativa fechada da Fase 2 e opex para 20, 50 e 100 documentos por mês.

**Versão documentada: API REST v3, path `/api/v3/`, especificação JSON:API.** A v1 (1.9, sem envelope) está em descontinuação, e a própria Clicksign publica guia de migração 1.9 → 3.0 (https://developers.clicksign.com/docs/faq-migracao, acesso 12/09/2026). O envelope só está ativo para contas criadas a partir de 01/07/2024; conta mais antiga recebe `503 service_unavailable` e precisa de acionamento do suporte (https://developers.clicksign.com/docs/primeiros-passos, acesso 12/09/2026).

## O que ele não responde, e por quê

**A política de reentrega de webhook.** Não existe em lugar nenhum da documentação pública. A página de melhores práticas fala em responder 200 e nada sobre o que acontece se não respondermos; a página de segurança fala de HMAC e IP; a referência do endpoint `/webhooks` expõe `endpoint`, `status`, `events` e `secret` e nada de tentativas. Também não há endpoint de reenvio manual nem listagem de entregas. Ver seção 5 e a seção "O que não consegui confirmar".

**Se o certificado ICP-Brasil funciona dentro do Widget Embedded.** As três páginas do widget (introdução, implementação, assinatura incorporada) não citam certificado digital uma vez sequer. A pergunta 7 do panorama continua aberta, e ela é a diferença entre assinatura embutida e promessa quebrada.

**Se o sandbox reproduz o fluxo de certificado em nuvem.** A documentação diz que sandbox e produção estão sempre na mesma versão e que documentos do sandbox não têm validade jurídica. Não diz se a busca de certificado por CPF nos provedores funciona lá. Só se descobre usando.

**Preço do plano Avançado e do carimbo do tempo.** Os dois são "sob medida" e "cobrança adicional variável". Não publicado, exige contato comercial.

**Como baixar o PDF assinado sem webhook.** As URLs de download (`original_file_url`, `signed_file_url`, `ziped_file_url`) aparecem documentadas no payload do webhook. Não encontrei endpoint REST da v3 que devolva esses campos. Ver seção 7.

---

## 1. Mapa do fluxo de integração

Base: `https://app.clicksign.com` (produção) e `https://sandbox.clicksign.com` (sandbox). Todas as chamadas levam `Authorization: {{access_token}}`, `Accept: application/vnd.api+json` e `Content-Type: application/vnd.api+json`. Datas em ISO 8601, respostas em UTC. Fonte: https://developers.clicksign.com/docs/informacoes-gerais (acesso 12/09/2026).

| # | Passo | Método e endpoint | O que vai dentro |
|---|---|---|---|
| 1 | Criar o envelope | `POST /api/v3/envelopes` | `name`, `deadline_at`, `auto_close`, `remind_interval`, `block_after_refusal`, `locale`, `default_subject`, `default_message`, `deadline_partial_signature_action`. Nasce em `draft` |
| 2 | Anexar o contrato | `POST /api/v3/envelopes/{envelope_id}/documents` | Três caminhos mutuamente exclusivos: `content_base64` (upload), `template` (gera a partir de modelo `.docx`) ou `duplicate` (cópia não assinada de documento finalizado). Mais `filename` e `metadata` |
| 3 | Criar cada parte | `POST /api/v3/envelopes/{envelope_id}/signers` | `name` (nome e sobrenome, sem números), `email`, `phone_number` (DDD sem DDI), `has_documentation`, `documentation` (CPF), `birthday`, `refusable`, `group` (ordem de assinatura), `location_required_enabled`, `communicate_events` |
| 4 | Qualificação de cada parte | `POST /api/v3/envelopes/{envelope_id}/requirements` | `action: "agree"` + `role`. Liga um signatário a um documento |
| 5 | Autenticação de cada parte | `POST /api/v3/envelopes/{envelope_id}/requirements` | `action: "provide_evidence"` + `auth: "icp_brasil"`. Liga o mesmo par signatário/documento |
| 6 | Disparar | `PATCH /api/v3/envelopes/{envelope_id}` | `status: "running"` |
| 7 | Notificar | `POST /api/v3/envelopes/{envelope_id}/notifications` | Solicitação de assinatura. Rate limit de 1 notificação por minuto por endpoint |
| 8 | Assinar | Widget na nossa página, ou link no e-mail | Ver seção 3 |
| 9 | Receber o retorno | `POST` da Clicksign na nossa URL | Ver seção 5 |
| 10 | Baixar o assinado | `GET` no host de conteúdo | Ver seção 7 |
| 11 | Reconciliar | `GET /api/v3/envelopes/{id}` | `status`: `draft`, `running`, `closed`, `canceled`. Polling de documento é proibido |

Fontes dos passos 1 a 7: https://developers.clicksign.com/docs/guia-de-criacao-o-passo-a-passo-padrao, https://developers.clicksign.com/recipes/criação-e-configuração-do-envelope, https://developers.clicksign.com/reference/criar-requisito-qualificacao, https://developers.clicksign.com/reference/criar-requisito-de-autenticacao, https://developers.clicksign.com/docs/notificacoes (acesso 12/09/2026).

### Upload ou modelo

Os dois existem. Para o nosso caso, **upload**.

| | Upload | Modelo |
|---|---|---|
| Campo | `content_base64`, no formato `data:<mimetype>;base64,<dados>` | `template.key` + dados das variáveis |
| Extensões | `doc`, `docx`, `pdf`, `jpg`, `jpeg`, `png`, `txt` | Só `.docx` |
| Limite | 10 MB por arquivo, 100 MB por envelope | Mesmo limite |
| Quem monta o documento | Nós | Clicksign |

Fontes: https://developers.clicksign.com/docs/documentos, https://developers.clicksign.com/reference/documento-campos-e-regras-de-negocio, https://developers.clicksign.com/docs/faq-duvidas-e-problemas-comuns (acesso 12/09/2026).

A Fase 1 já tem 20h orçadas para "Geração de documento, 1 modelo". O PDF sai pronto do nosso lado, e a Clicksign recebe base64. Usar modelo da Clicksign jogaria o conteúdo do contrato para dentro do fornecedor, contra o que `arquitetura-seguranca.md` pede, e prenderia o texto da CPR a um `.docx` hospedado por terceiro.

### Qualificação: os papéis da CPR já existem no domínio

A referência do endpoint expõe `role` com enum `sign`, `party`, `contractor`. A página de tipos de qualificação lista cerca de 60 valores, entre eles `issuer` (Emitente), `buyer` (Parte compradora), `broker` (Corretor(a)), `guarantor` (Avalista) e `intervening_guarantor` (Interveniente Garantidor). Fonte: https://developers.clicksign.com/docs/adicionar-requisito-de-qualificacao (acesso 12/09/2026).

As três partes de `entendimento-do-projeto.md` (produtor, comprador, corretor opcional) têm papel nominal no domínio da Clicksign, e esse papel sai impresso no log do documento. Confirmar com o suporte se o enum curto da referência é limitação real da API ou erro de documentação, porque a diferença é entre "Emitente" e "Assinar" na prova jurídica.

### Ativação: usar `PATCH`, não `/activate`

Existe uma página descrevendo ativação assíncrona por `POST /api/v3/envelopes/{key}/activate` com resposta `202 Accepted`. Ela abre com "Ativação em alta escala está em desenvolvimento", e a referência do endpoint repete "Funcionalidade em desenvolvimento". Fontes: https://developers.clicksign.com/docs/ativacao-escala-performatica e https://developers.clicksign.com/reference/api-ativar-envelope (acesso 12/09/2026). Dezenas de documentos por mês não pedem ativação assíncrona. `PATCH` com `status: "running"`.

---

## 2. Autenticação da API

**Access Token estático, sem OAuth, sem expiração documentada.**

| Item | Valor |
|---|---|
| Tipo | `apiKey` em header, nome `Authorization`, conforme o `securitySchemes` do OpenAPI da própria referência |
| Como se obtém | Login na conta, *Configurações* → *API* → *Gerar Access Token*, com descrição. Depois associar o e-mail do operador à API e salvar |
| Escopo | Por conta e por ambiente. Sandbox e produção têm tokens distintos |
| Expiração | Não documentada |
| Rotação | Não há endpoint. Gera-se outro token na tela de Configurações e descarta-se o anterior |
| Também aceito | Query string `?access_token=`, usado no teste de autenticação da própria documentação |
| Erro sem token | 401 |

Fontes: https://developers.clicksign.com/docs/primeiros-passos, https://developers.clicksign.com/docs/informacoes-gerais, https://developers.clicksign.com/reference/api-criar-webhook (acesso 12/09/2026).

Três consequências de projeto:

1. **Rotação é operação manual de painel.** Não dá para automatizar por API. O acordo de credencial que `entendimento-do-projeto.md` pede para a B3 vale aqui também, com procedimento escrito e responsável nomeado.
2. **O token aceito em query string precisa ser proibido no nosso código.** URL vai para log de proxy, log de acesso e histórico de navegador. Usar sempre header, e mascarar o valor em log, como `arquitetura-seguranca.md` já exige para credencial.
3. **Não há escopo por operação.** Um token que cria envelope também exclui rascunho, cria webhook e lista usuários. Guardar no mesmo cofre da credencial B3, com o mesmo rigor.

### Rate limit

| Ambiente | Limite |
|---|---|
| Produção | 50 requisições por conta / 10 segundos |
| Sandbox | 20 requisições por conta / 10 segundos |

Headers de resposta: `X-Rate-Limit`, `X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset` (Unix time, UTC). Excedeu, `429 Too Many Requests`. Links de download não contam para a cota. Fonte: https://developers.clicksign.com/docs/limite-de-requisicoes (acesso 12/09/2026).

Um envelope de CPR com três partes gasta 9 requisições (1 envelope + 1 documento + 3 signatários + 6 requisitos = 11, na verdade, com qualificação e autenticação por parte). Cabe folgado em 50/10s. O limite só importa se alguém escrever um laço de reconciliação, e a Clicksign proíbe polling de documento por contrato de uso, com pedido explícito de autorização prévia ao suporte.

---

## 3. Assinatura embutida: existe, mas o certificado em nuvem sai da tela

**O panorama está certo. Confirmado na documentação oficial.**

### O que é embutido

O **Widget Embedded** é uma biblioteca JS que monta a tela de assinatura dentro de um `div` da nossa página.

| Item | Valor |
|---|---|
| Biblioteca | `https://cdn-public-library.clicksign.com/embedded/embedded.min-2.1.0.js` |
| Inicialização | `new Clicksign(ID_DO_SIGNATARIO)`, com o `id` devolvido no passo 3 do fluxo |
| Pré-condição | Envelope em `running` |
| Configuração | `widget.endpoint` (sandbox ou produção), `widget.origin`, `widget.mount('container')`, `widget.unmount()` |
| Eventos JS | `loaded`, `signed`, `resized` (traz `event.data.height`) |
| Protocolo | HTTP ou HTTPS no sandbox, **exclusivamente HTTPS em produção** |
| Ativação | Ativo por padrão no sandbox. **Em produção exige contratar**, em *Configurações* → aba *API* → *Contratar* |

Fontes: https://developers.clicksign.com/docs/implementando-o-widget-embedded e https://developers.clicksign.com/docs/introducao-ao-widget-embedded (acesso 12/09/2026).

A própria documentação manda não confiar nos callbacks: "Os callbacks são javascript rodando no browser do usuário e podem ser manipulados de forma indevida. Por segurança, confie nas informações recebidas através dos Webhooks." Isso define a arquitetura: o `signed` do widget serve para trocar a tela do usuário, e o estado do registro só muda quando o webhook chegar.

Existe ainda a **Assinatura Incorporada** (`embedded_signature`, também chamada tokenless), que na v3 dispensa iframe e usa uma classe `noWidget` em JS, coletando nome, CPF e data de nascimento do signatário. É um requisito de autenticação próprio, diferente de `icp_brasil`. A documentação não diz se os dois podem coexistir no mesmo par signatário/documento. Fontes: https://developers.clicksign.com/docs/instalacao-de-widget-assinatura-tokenless e https://developers.clicksign.com/docs/assinatura-incorporada-implementacoes-e-testes (acesso 12/09/2026).

### Onde exatamente o usuário sai da nossa tela

A sequência publicada na central de ajuda, passo a passo:

| Passo | Onde acontece |
|---|---|
| 1. Abre o documento para assinar | Nossa página, dentro do widget |
| 2. Lê o documento e confirma os dados | Nossa página |
| 3. Escolhe o tipo de certificado: **Local** ou **em Nuvem** | Nossa página |
| 4a. Local | Exige a extensão **Web PKI** instalada. A plataforma oferece o botão *Instalar* se não houver |
| 4b. Nuvem | A Clicksign pesquisa o CPF informado nos provedores atendidos. Achou, **"o signatário é direcionado para o ambiente do provedor para realizar a autenticação"** |
| 5. Autentica no app do provedor | **Fora da nossa tela e fora da Clicksign** |
| 6. Volta e conclui | Retorna ao fluxo |

Fontes: https://ajuda.clicksign.com/article/659-assinando-com-certificado-digital e https://ajuda.clicksign.com/article/973-certificado-digital-em-nuvem (acesso 12/09/2026).

O ponto de saída é o passo 4b, depois da confirmação de dados e da escolha do tipo de certificado. Se houver mais de um certificado ligado ao CPF, a Clicksign oferece a escolha antes de redirecionar.

Consequência de produto: a tela 9 do mockup (`plano-do-projeto.md`) precisa de dois estados novos que não existem hoje, "saiu para autenticar no provedor" e "voltou", e de um caminho de suporte para quem não volta. `plano-do-projeto.md` pede zero jargão na interface; "você será levado ao aplicativo do seu certificado para confirmar" resolve sem citar provedor.

---

## 4. Certificado em nuvem: a documentação diz três, o marketing diz seis

A API não tem parâmetro de provedor. O requisito de autenticação aceita `auth: "icp_brasil"` e nada mais. Quem escolhe é o signatário, na tela, e a busca é feita pelo CPF que mandamos em `documentation`. Fonte: https://developers.clicksign.com/reference/criar-requisito-de-autenticacao (acesso 12/09/2026).

As duas páginas de ajuda da Clicksign discordam entre si sobre a lista:

| Fonte | Provedores listados |
|---|---|
| Artigo 973, "Certificado digital em nuvem", que descreve o comportamento real da busca por CPF | **Três**: SAFEWEB (SafeID), SOLUTI (BirdID), VALID (VIDaaS) |
| Artigo 659, "Assinando um documento com Certificado Digital", na mensagem de certificado não encontrado | **Os mesmos três**: SafeID, BirdID, VIDaaS |
| Artigo 935, "Certificados Digitais aceitos pela Clicksign", parágrafo "Autoridades aceitas" | **Seis**: BirdID, SafeID, VIDaaS, DS Cloud, SerproID/NeoID, SyngularID |

Fontes: https://ajuda.clicksign.com/article/973-certificado-digital-em-nuvem, https://ajuda.clicksign.com/article/659-assinando-com-certificado-digital, https://ajuda.clicksign.com/article/935-certificados-digitais-aceitos-pela-clicksign (acesso 12/09/2026).

Duas das três páginas, e as duas que descrevem o comportamento do sistema em vez de vender, dizem **três**. A lista de seis aparece uma vez, em parágrafo promocional, sem detalhamento. **Tratar como três até o suporte confirmar por escrito.** Isso derruba parte do argumento que colocou a Clicksign em primeiro na trilha A do panorama: a vantagem sobre os cinco trust services pré-configurados da Lacuna vira empate ou desvantagem.

O que entra na chamada, para os três confirmados: nada. Não há `clientId`, `clientSecret`, `kms_type` nem redirect URI para cadastrar. A integração com o PSC é da Clicksign. Isso é a metade boa do trade-off: zero trabalho de integração com Valid, Soluti e Safeweb, zero controle sobre ela.

### Só e-CPF

"Atualmente, a Clicksign aceita a autenticação com os seguintes certificados digitais: A1 e A3, **ambos de pessoa física (e-CPF)**." E, no artigo 659: "O signatário apenas poderá assinar o documento utilizando o Certificado Digital em seu CPF." Fonte: https://ajuda.clicksign.com/article/935-certificados-digitais-aceitos-pela-clicksign (acesso 12/09/2026).

CPR emitida por cooperativa não assina aqui com e-CNPJ. Ou a PJ assina por representante legal com e-CPF, qualificado como `legal_representative`, ou a Clicksign não serve. É a pergunta 4 da seção 9 do panorama, e continua sendo a que pode derrubar o fornecedor sozinha.

---

## 5. Webhooks

Registro por API: `POST /api/v3/webhooks`, com `data.type: "webhooks"` e `attributes.endpoint` (obrigatório), `attributes.status` (`active` ou `inactive`) e `attributes.events` (array com os nomes exatos). A resposta 201 devolve `id`, `endpoint`, `secret`, `status`, `events`, `created`, `modified`. O `secret` é gerado automaticamente no cadastro. Também há `GET /webhooks`, `GET /webhooks/{id}`, `PATCH /webhooks/{id}` e `DELETE /webhooks/{id}`. Fonte: https://developers.clicksign.com/reference/api-criar-webhook (acesso 12/09/2026).

### Tabela de eventos

Nomes exatos, como devem ser escritos em `attributes.events`. Fonte: https://developers.clicksign.com/docs/eventos (acesso 12/09/2026).

| Grupo | Evento | Quando ocorre | Usamos? |
|---|---|---|---|
| Ciclo de vida | `upload` | Upload de um documento | Não |
| Ciclo de vida | `add_image` | Imagem adicionada ao documento | Não |
| Ciclo de vida | `close` | Documento finalizado manualmente | Sim |
| Ciclo de vida | `auto_close` | Documento finalizado automaticamente após a última assinatura | **Sim, é o caminho feliz** |
| Ciclo de vida | `deadline` | Data limite de assinatura atingida | **Sim, art. 12 da Lei 8.929/1994** |
| Ciclo de vida | `document_closed` | Documento finalizado e **pronto para download** | **Sim, é o gatilho do download** |
| Ciclo de vida | `cancel` | Documento cancelado manualmente | Sim |
| Assinatura | `add_signer` | Signatários adicionados | Não |
| Assinatura | `remove_signer` | Signatários removidos | Não |
| Assinatura | `sign` | Um signatário assinou | **Sim, é o progresso parcial da tela 9** |
| Assinatura | `signature_started` | Fluxo de assinatura iniciado por um signatário | Sim, alimenta a trilha de auditoria |
| Assinatura | `refusal` | Documento recusado | **Sim, caminho de erro** |
| Autenticação | `attempts_by_whatsapp_exceeded` | Tentativas de reenvio de token por WhatsApp excedidas | Não |
| Autenticação | `attempts_by_liveness_or_facematch_exceeded` | Tentativas de selfie dinâmica ou biometria facial excedidas | Não |
| Autenticação | `liveness_refused` | Prova de vida recusada | Não |
| Autenticação | `facematch_refused` | Biometria facial recusada | Não |
| Autenticação | `biometric_refused` | Biometria SERPRO recusada | Não |
| Autenticação | `identity_biometrics_refused` | Biometria base ampliada recusada, inconclusiva ou não validada | Não |
| Autenticação | `documentscopy_refused` | Documentoscopia recusada | Não |
| Autenticação | `ocr_refused` | Análise de OCR recusada | Não |
| Configuração | `update_deadline` | Data limite alterada | Sim, auditoria |
| Configuração | `update_auto_close` | Finalização automática alterada | Não |
| Configuração | `update_locale` | Idioma alterado | Não |
| Configuração | `custom` | Fluxos de eventos customizados | Não |
| Aceite WhatsApp | `acceptance_term_enqueued`, `acceptance_term_sent`, `acceptance_term_completed`, `acceptance_term_refused`, `acceptance_term_canceled`, `acceptance_term_expired`, `acceptance_term_error` | Fluxo de Aceite via WhatsApp | Não |

**Não existe evento de falha de autenticação por certificado digital.** A lista de recusas cobre biometria, selfie, documentoscopia e OCR. Se o signatário não tiver certificado no CPF, ou se a autenticação no provedor falhar, nada chega no webhook. O registro fica parado em `AGUARDANDO_ASSINATURAS` e só o relógio de prazo detecta. Isso é trabalho de backoffice que `maquina-de-estados.md` não previu.

O panorama cita apenas `close` e `document_closed`. São 25 eventos de documento mais 7 de aceite por WhatsApp.

### Autenticação da origem

Dois mecanismos, ambos publicados. Fonte: https://developers.clicksign.com/docs/seguranca-de-webhooks (acesso 12/09/2026).

| Mecanismo | Detalhe |
|---|---|
| **HMAC SHA256** | Gerado automaticamente no cadastro do webhook. A cada disparo a Clicksign calcula o hash SHA256 do body somado ao secret e envia no header `Content-Hmac`, no formato `sha256=<hex>`. Validar sem formatar o JSON antes do cálculo |
| **IP fixo** | Produção `34.204.113.69`, sandbox `3.232.199.65`. Um IP por ambiente, dá para travar no firewall |
| HTTP Basic | Aceito por URL no formato `https://usuario:senha@host/webhook`. Não usar, coloca senha na URL |
| HTTPS | "Fortemente sugerido" pela Clicksign. Para nós é obrigatório |

Header `Event` traz o tipo do evento, o que permite rotear antes de fazer parse do JSON.

### Se a nossa ponta cair

**Não publicado.** Nenhuma das quatro páginas de webhook (visão geral, segurança, melhores práticas, referência do endpoint) menciona número de tentativas, intervalo, backoff, fila de mortos ou reenvio manual. Nem existe endpoint de listagem de entregas. O que está escrito é o oposto: "Qualquer resposta fora do intervalo 2XX informará que você não recebeu seu webhook, incluindo o 301 Redirect. A plataforma Clicksign não segue redirecionamentos". Fonte: https://developers.clicksign.com/docs/melhores-praticas-webhooks (acesso 12/09/2026).

Enquanto o suporte não responder por escrito, **projetar assumindo entrega única e sem reentrega**. Na prática:

- Responder 200 antes de processar, com o evento gravado cru em fila própria.
- Job de varredura por `GET /api/v3/envelopes/{id}` para todo registro em `AGUARDANDO_ASSINATURAS` há mais de N horas, com frequência baixa, porque polling de documento é proibido por contrato e o de envelope não é o que a Clicksign proíbe nominalmente. **Confirmar essa distinção com o suporte antes de ligar o job.**
- Idempotência pelo par (documento, evento, `occurred_at`), já que não há id de entrega.

---

## 6. Sandbox

| Pergunta | Resposta |
|---|---|
| Existe? | Sim, `https://sandbox.clicksign.com`, cadastro em `/signup` |
| É gratuito? | Sim. "Crie uma conta gratuita para testes". Sem cartão de crédito |
| Exige contrato? | Não |
| É fiel à produção? | **Na versão, sim.** "Os ambientes Sandbox e Produção estão sempre na mesma versão. Todas as atualizações realizadas no ambiente de Produção também são refletidas automaticamente no ambiente Sandbox" |
| Migração | Trocar host e access token. Nada mais |
| Validade jurídica | `false`. Documento de sandbox não tem valor legal |
| Rate limit | 20 req/conta/10s, contra 50 em produção |
| Widget Embedded | **Ativo por padrão no sandbox.** Em produção exige contratar |

Fontes: https://developers.clicksign.com/docs/informacoes-gerais, https://developers.clicksign.com/docs/primeiros-passos, https://developers.clicksign.com/docs/introducao-ao-widget-embedded, https://developers.clicksign.com/docs/limite-de-requisicoes (acesso 12/09/2026).

**Dá para testar assinatura com certificado ICP-Brasil real no sandbox?** Não publicado. A documentação afirma paridade de versão, não paridade de integração com os PSC. O certificado de uma pessoa física é o mesmo objeto nos dois ambientes, então o cenário provável é que a busca por CPF funcione e a assinatura saia sem validade jurídica. Isso é inferência, não fonte. Item 1 da lista de pendências.

O sandbox gratuito e sem contrato destrava a Fase 1 no mesmo dia, e é a vantagem competitiva mais sólida da Clicksign neste estudo. O teste grátis de produção são 14 dias e até 30 documentos (https://www.clicksign.com/planos, acesso 12/09/2026), que serve como janela de validação do certificado real antes de contratar.

---

## 7. Armazenamento do documento

`arquitetura-seguranca.md` classifica o documento como o dado mais sensível do sistema e diz "Queremos guardar nós". Dá para guardar nós. Não dá para ser os únicos.

| Pergunta | Resposta |
|---|---|
| Quem guarda | Clicksign, em bucket S3 próprio. Hosts de conteúdo: `https://clicksign-content-production.s3.amazonaws.com/` e `https://clicksign-content-sandbox.s3.amazonaws.com/` |
| Por quanto tempo | "Os documentos enviados para assinatura ficam disponíveis dentro da plataforma Clicksign **enquanto você tiver conta conosco**". Sem prazo, sem política de expurgo publicada |
| Conseguimos guardar nós | **Sim.** O payload do evento traz `downloads.original_file_url`, `downloads.signed_file_url` e `downloads.ziped_file_url`, caminhos relativos ao host de conteúdo do ambiente. Download não consome rate limit |
| Conseguimos apagar do lado deles | **Não por API.** `DELETE /envelopes/{id}` e `DELETE /envelopes/{id}/documents/{id}` funcionam apenas em `draft`. Pela plataforma, documento finalizado ou cancelado vai para a Lixeira e depois precisa de *Excluir definitivamente*, ação restrita a usuário administrador |

Fontes: https://developers.clicksign.com/docs/limite-de-requisicoes, https://ajuda.clicksign.com/article/564-armazenamento-de-documentos, https://developers.clicksign.com/reference/api-excluir-envelope, https://developers.clicksign.com/reference/api-excluir-documento, https://ajuda.clicksign.com/article/119-e-possivel-excluir-um-documento-pasta (acesso 12/09/2026).

O que isso obriga:

1. **Rotina de download imediata**, disparada por `document_closed`, baixando os três arquivos e gravando no nosso storage cifrado, com hash conferido. Enquanto isso não roda, a única cópia do contrato está no fornecedor.
2. **Procedimento manual de expurgo**, com responsável e periodicidade, porque a exclusão definitiva é clique de administrador no painel. Isso contradiz o item 4 da seção 7 de `arquitetura-seguranca.md`, que trata pedido de exclusão como procedimento e não como tarefa manual em sistema de terceiro.
3. **O documento fica em dois lugares por padrão.** O modelo de ameaça de `arquitetura-seguranca.md` ("o adversário mais provável é um membro do clube") ganha uma superfície nova: o painel da Clicksign, com controle de acesso por usuário e por pasta que é deles, não nosso, e sem integração com a nossa tabela de acessos. Quem tem login de administrador na Clicksign vê todos os contratos de todos os membros e isso não aparece na nossa auditoria de leitura.

O item 3 é o achado mais desconfortável deste estudo. Ele não desqualifica a Clicksign, e vale igualmente para ZapSign e D4Sign. Vale registrar na avaliação de risco antes da assinatura do contrato, com o número de pessoas que terão login no painel mantido no mínimo.

O plano Avançado inclui "Backup de documentos gratuito" e "Logs de Auditoria" (https://www.clicksign.com/planos, acesso 12/09/2026). Os dois são exatamente o que mitigaria o item 3, e os dois estão no plano cujo preço não é publicado.

---

## 8. Manifesto de assinatura e trilha de auditoria

O que volta junto com o PDF, quando há certificado digital:

| Artefato | O que é | Fonte |
|---|---|---|
| **PAdES** | Arquivo PDF separado, com prefixo `Pades` no nome, gerado quando o documento foi assinado com certificado digital. Padrão de assinatura digital para PDF com chave pública. Disponível após a finalização, ou seja, depois que todos assinarem | https://ajuda.clicksign.com/article/818-como-obter-o-arquivo-pades-do-documento-assinado |
| **Log do documento** | Página anexa na última folha do arquivo assinado, com o histórico completo: nomes, endereços de IP, e-mails, métodos de autenticação e assinatura, dia e horário. Latitude e longitude se o signatário compartilhou localização | https://ajuda.clicksign.com/article/230-log-presente-nos-documentos-assinados |
| **Número do documento** | Impresso em todas as páginas | mesma fonte |
| **Hash do arquivo original** | Impresso no documento finalizado | mesma fonte |
| **Certificado ICP-Brasil da Clicksign** | Todos os documentos finalizados são carimbados com o certificado digital da própria Clicksign, atestando a procedência | mesma fonte |
| **Carimbo do tempo** | Selo de Autoridade Certificadora do Tempo credenciada pela ICP-Brasil, no horário oficial de Brasília. **Não vem por padrão** | https://ajuda.clicksign.com/article/1019-carimbo-do-tempo |

Acesso a todas em 12/09/2026.

A validação externa existe e é gratuita: o arquivo PAdES sobe em `validar.iti.gov.br`, o validador do ITI, que devolve data, hora por signatário e um relatório PDF de conformidade (https://ajuda.clicksign.com/article/1020-carimbo-do-tempo-como-consultar, acesso 12/09/2026). Isso é bom para nós: a prova da assinatura não depende da Clicksign continuar existindo.

**Política de assinatura não é mencionada em nenhuma página.** Nem o perfil PAdES usado (B-B, B-T, B-LT, B-LTA), nem validação de longo prazo. Para um documento que precisa ser provado anos depois, a diferença entre PAdES básico e PAdES com carimbo e validação de longo prazo é a diferença entre prova e discussão pericial.

### O carimbo do tempo é o problema comercial deste estudo

> "O carimbo do tempo está disponível para os planos personalizados (Automação e Integração) e pode ser contratado mediante uma **cobrança adicional variável por quantidade de carimbos** utilizados por mês."

A mesma página abre dizendo "Esta funcionalidade está disponível no plano Avançado". As duas frases estão no mesmo artigo e não batem. Fonte: https://ajuda.clicksign.com/article/1019-carimbo-do-tempo (acesso 12/09/2026).

De um jeito ou de outro, carimbo do tempo **não está nos planos Start e Plus**, e tem custo por uso não publicado. Sem ele, a CPR fica com a data que o servidor da Clicksign registrou, atestada pelo certificado da Clicksign, e não por uma ACT credenciada. Para contrato de café com prazo de safra, é uma economia que se paga cara em disputa.

---

## 9. Preço

A página de planos mostra preço promocional de primeira mensalidade no cabeçalho e mistura com o preço cheio no texto, exatamente como o panorama registrou. O objeto `pricing` do script da própria página traz a tabela completa, com `from` (preço cheio) e `to` (primeira mensalidade com 15% de desconto, válido só a partir de 50 documentos, cupom GB15 até 30/09). Fonte: https://www.clicksign.com/planos (acesso 12/09/2026).

### Preço cheio, mensal, por volume contratado

| Documentos/mês | Start | Plus | Automação |
|---|---|---|---|
| 20 | **R$ 39,00** | R$ 59,00 | R$ 85,00 |
| 50 | **R$ 69,00** | R$ 99,00 | R$ 135,00 |
| 100 | **R$ 119,00** | R$ 179,00 | R$ 235,00 |
| 200 | **R$ 199,00** | R$ 299,00 | R$ 385,00 |
| 350 | não oferecido | R$ 509,00 | R$ 645,00 |
| 500 | não oferecido | R$ 699,00 | R$ 875,00 |

Avançado: "sob medida", 300+ documentos por mês, cobrança mensal ou anual conforme contrato. **Não publicado, exige contato comercial.**

### Documento excedente, por plano e por faixa contratada

| Faixa | Start | Plus | Automação |
|---|---|---|---|
| 20 | R$ 3,00 | R$ 4,90 | R$ 6,90 |
| 50 | R$ 2,70 | R$ 4,20 | R$ 5,70 |
| 100 | R$ 2,50 | R$ 4,00 | R$ 5,20 |
| 200 | R$ 2,40 | R$ 3,60 | R$ 4,50 |
| 350 | não oferecido | R$ 3,50 | R$ 4,40 |
| 500 | não oferecido | R$ 3,40 | R$ 4,30 |

### O que libera a API

**Todos os planos, do Start em diante.** A tabela comparativa marca "Integração via API", "Widget Embedded", "Modelos via API", "Integração via Zapier" e "MCP Server" como disponíveis no Start, e o cartão do Start lista "Integre nossa API ao seu sistema" e "Assine com Certificado Digital" entre as características. Fonte: https://www.clicksign.com/planos (acesso 12/09/2026).

Isso muda a comparação do panorama com a ZapSign, onde API só existe a partir do plano Team.

Ressalva: o cartão do plano Automação vende "Crie documentos automaticamente a partir de modelos" como diferencial dele, enquanto a linha "Modelos via API" da tabela comparativa aparece marcada nos quatro planos. As duas afirmações estão na mesma página e não batem. Para nós não muda nada, porque o PDF sai do nosso lado.

### Cobrança

| Item | Valor |
|---|---|
| Unidade cobrada | **Documento enviado, não assinatura.** Uma CPR com três partes é um documento |
| Usuários inclusos | 5 no Start, 10 no Plus e no Automação, ilimitado no Avançado |
| Usuário adicional | R$ 15,00 nos três primeiros planos, R$ 0 no Avançado |
| Ciclo | Mensal no Start, Plus e Automação. Mensal ou anual no Avançado |
| Pagamento | Cartão de crédito ou boleto |
| Cancelamento | A qualquer momento no Start, Plus e Automação |
| Mínimo mensal | Não publicado como cláusula. O piso prático é a menor faixa, R$ 39,00 no Start com 20 documentos |
| Certificado digital do signatário | Custo do titular. A Clicksign não emite certificado, não é AC |
| Documentoscopia | R$ 4,50 por solicitação |
| Biometria SERPRO | R$ 4,50 por consulta |
| Biometria facial | R$ 1,50 por validação |
| Carimbo do tempo | Cobrança adicional variável por quantidade. **Não publicado** |

Fontes: https://www.clicksign.com/planos e https://developers.clicksign.com/docs/tipos-de-requisitos-de-autenticacao (acesso 12/09/2026).

A cobrança por documento, e não por assinatura, é a diferença comercial real contra a ZapSign, que cobra R$ 0,50 por assinatura com certificado digital além do plano. Numa CPR com três partes, a ZapSign cobra três vezes e a Clicksign uma.

---

## 10. Estimativa fechada da Fase 2

`plano-do-projeto.md` traz 32 a 40h, com a faixa dependendo de certificado em nuvem contra token físico. A leitura da documentação foi feita. O número sobe mesmo no cenário de nuvem, que era o barato.

Premissa: a Fase 1 já entregou o PDF gerado, a máquina de estados em duas camadas, a tela de assinatura mockada, a fila de pendências e a interface de uma porta só (`criarSolicitacao`, `obterStatus`, `receberRetorno`). A Fase 2 troca a implementação.

| # | Bloco | Horas | O que está dentro |
|---|---|---|---|
| 1 | Cliente HTTP JSON:API + segredo | 4–6 | Serialização `data/type/attributes/relationships`, headers `vnd.api+json`, access token no cofre com mascaramento em log, proibição do token em query string, tratamento de 429 lendo `X-Rate-Limit-Reset`, backoff, mapa de erros 400/401/404/422/429/500/503 |
| 2 | Montagem do envelope | 8–10 | Seis a onze chamadas encadeadas por CPR (envelope, documento em base64, 2 ou 3 signatários, qualificação e autenticação por parte, `PATCH` de ativação), com **compensação**: falhou no meio, `DELETE` do envelope em `draft` e reinício limpo. Mapeamento dos papéis da CPR para `role`, validação de CPF e nome antes do envio, controle do limite de 10 MB |
| 3 | Correlação e reconciliação | 3–5 | `metadata` do documento carregando o id do registro, tabela de `envelope_id` / `document_id` / `signer_id` por parte, `GET /envelopes/{id}` sob demanda para a tela de resolução do backoffice |
| 4 | Webhook | 8–12 | Endpoint HTTPS, validação de `Content-Hmac` SHA256 sem reformatar o body, allowlist dos dois IPs, roteamento pelo header `Event`, 200 imediato com gravação crua e processamento em background, idempotência sem id de entrega, tradução dos 9 eventos relevantes para a máquina de estados, **fila própria de reprocessamento porque a reentrega da Clicksign não é publicada** |
| 5 | Download e guarda | 6–8 | Consumo de `downloads.original_file_url`, `signed_file_url` e `ziped_file_url` prefixados pelo host S3 do ambiente, download dos três, conferência de hash, gravação no storage cifrado com URL assinada de curta duração, registro na tabela de acessos |
| 6 | Tela de assinatura | 8–12 | Widget Embedded na tela 9 (`mount`, `unmount`, `loaded`, `signed`, `resized`, altura dinâmica), **mais os dois estados novos de saída e retorno do provedor de nuvem**, mais o caminho de quem não volta, mais a regra de nunca confiar no callback `signed` |
| 7 | Prazo, recusa e cancelamento | 5–7 | `deadline_at` alinhado aos 30 dias úteis do art. 12 da Lei 8.929/1994, `block_after_refusal`, eventos `refusal`, `cancel` e `deadline` ligados aos caminhos de resolução, cancelamento por `PATCH` do documento, reenvio de notificação respeitando 1/min por endpoint |
| 8 | Sandbox para produção | 4–8 | Conta e token de produção, **contratação do Widget Embedded em produção junto à Clicksign**, teste ponta a ponta com certificado ICP real, ajuste do host de conteúdo. A faixa é larga porque depende de resposta comercial da Clicksign |
| 9 | Observabilidade e testes | 5–7 | Id de correlação por chamada, testes com payloads de webhook gravados, teste de HMAC inválido, teste de entrega duplicada, teste de IP não autorizado, simulação dos quatro caminhos de resolução |
| | **Total** | **51–75h** | |

### A faixa é larga. O que a fecha

| Informação que falta | Fecha qual bloco | Amplitude que elimina |
|---|---|---|
| Política de reentrega de webhook | 4 | **~4h. É a maior incerteza única.** Se houver reentrega com backoff documentado, a fila própria encolhe para deduplicação |
| ICP-Brasil funciona dentro do Widget Embedded? | 6 | ~4h. Se não funcionar, o widget não serve para o nosso caso e a tela 9 vira redirect puro |
| Prazo da Clicksign para contratar o widget em produção | 8 | ~4h |
| Sandbox aceita certificado real? | 8, 9 | ~3h de testes que só dariam para fazer em produção |
| `role` aceita os 60 valores ou só os 3 do enum? | 2 | ~2h |
| São três provedores de nuvem ou seis? | 6 | ~2h de tratamento de caso "certificado não encontrado" |

**Ponto médio defensável: 62h.** Com respostas favoráveis (reentrega documentada, ICP no widget, sandbox fiel), 51h. Com respostas desfavoráveis, 75h.

### Comparação com o plano atual

| | `plano-do-projeto.md` | Este estudo |
|---|---|---|
| Fase 2 | 32–40h | 51–75h |
| Estouro | | **+19h no melhor caso, +35h no pior** |

De onde vem a diferença, item por item:

| Trabalho | Estava previsto? |
|---|---|
| Fila própria de reprocessamento de webhook | Não. O plano supõe webhook confiável |
| Estados de saída e retorno do provedor de certificado em nuvem | Não. `entendimento-do-projeto.md` diz que nuvem "mantém quase tudo dentro da nossa tela" |
| Compensação da montagem em seis a onze chamadas | Não. O plano fala em "criar documento, signatários, webhook, reconciliação" |
| Download e guarda própria dos três arquivos | Parcialmente. "Queremos guardar nós" está em `plano-do-projeto.md` como critério, não como bloco de horas |
| Contratação do Widget Embedded em produção | Não. É gate comercial dentro da fase técnica |
| Ausência de evento de falha de certificado | Não. Vira trabalho de backoffice e de relógio de prazo |

O panorama já apontava 32 a 40h como custo do caminho "plataforma, só nuvem". A leitura da documentação mostra que aquela estimativa tratava o certificado em nuvem como assinatura embutida, e ele não é. A linha correta da tabela do panorama, para a Clicksign, é a segunda: "plataforma, com fluxo que sai da nossa tela".

---

## 11. Custo real de opex

Cenário: 3 usuários de backoffice (dentro dos 5 do Start), PDF gerado por nós, `auth: icp_brasil`, uma CPR por documento independente do número de partes, sem carimbo do tempo, sem biometria, sem documentoscopia. Preço cheio, sem o desconto promocional de primeira mensalidade.

| Volume | Faixa contratada | Plano Start | Excedente | **Total/mês** | Contra os R$ 295 do dossiê |
|---|---|---|---|---|---|
| 20 documentos | 20 | R$ 39,00 | R$ 0,00 | **R$ 39,00** | Sobram R$ 256,00 |
| 50 documentos | 50 | R$ 69,00 | R$ 0,00 | **R$ 69,00** | Sobram R$ 226,00 |
| 100 documentos | 100 | R$ 119,00 | R$ 0,00 | **R$ 119,00** | Sobram R$ 176,00 |

Contratar a faixa exata é sempre mais barato que contratar a faixa abaixo e pagar excedente. 100 documentos na faixa de 50 custaria R$ 69,00 + 50 × R$ 2,70 = R$ 204,00, contra R$ 119,00 na faixa certa. Isso vira regra de gestão do contrato: revisar a faixa contratada trimestralmente.

**A conta fecha com folga.** Nos três cenários. O dossiê previa R$ 295/mês de opex e a linha de assinatura consome entre 13% e 40% disso, sobrando espaço para a linha da B3 e para infraestrutura.

Três ressalvas que podem virar a conta:

| Ressalva | Efeito | Status |
|---|---|---|
| **Carimbo do tempo** | Exige plano Avançado ou personalizado, mais cobrança variável por carimbo. Sai da faixa publicada inteira | **Não publicado.** É a única variável capaz de estourar os R$ 295 sozinha |
| **Certificado dos membros** | Custo do titular. Se o clube bancar, é segunda linha de opex, na ordem de R$ 100 a R$ 640/mês pelas tabelas públicas de SafeID que o panorama levantou | Pergunta 5 ao cliente |
| **Backup e logs de auditoria da Clicksign** | Só no Avançado. É o que mitigaria o risco da seção 7 | **Não publicado** |

Perguntar ao comercial, em um único e-mail: preço do Avançado para 100 documentos/mês, preço unitário do carimbo do tempo, e se carimbo do tempo pode ser contratado como add-on sobre o Start.

---

## 12. O que não consegui confirmar

| # | Item | Com quem | Por que trava |
|---|---|---|---|
| 1 | **Política de reentrega de webhook**: quantas tentativas, em que intervalo, existe reenvio manual ou listagem de entregas | Suporte técnico | Bloco 4 da estimativa. Define se construímos fila própria |
| 2 | **Certificado ICP-Brasil dentro do Widget Embedded** | Suporte técnico | Bloco 6. É a pergunta 7 do panorama, ainda sem resposta |
| 3 | **São três provedores de nuvem ou seis?** O artigo 973 e o 659 dizem três; o 935 diz seis | Suporte técnico, pedindo por escrito | Muda a posição da Clicksign contra a Lacuna na trilha A |
| 4 | **Sandbox reproduz assinatura com certificado ICP real?** | Suporte técnico | Bloco 8. Sandbox que não testa certificado não valida a Fase 1 |
| 5 | **Preço do plano Avançado** e **preço unitário do carimbo do tempo** | Comercial | Único item capaz de estourar os R$ 295/mês |
| 6 | **Carimbo do tempo pode ser add-on sobre Start?** A página de ajuda diz "plano Avançado" em uma frase e "planos personalizados (Automação e Integração)" em outra | Comercial | Define se a prova de tempo cabe no orçamento |
| 7 | **Perfil PAdES entregue** (B-B, B-T, B-LT, B-LTA) e política de assinatura aplicada | Suporte técnico | É o que prova a assinatura em 2033 |
| 8 | **Enum real de `role`**: os 3 valores da referência ou os ~60 da página de qualificações | Suporte técnico | Bloco 2. Define se "Emitente" existe ou se vira "Assinar" |
| 9 | **Aceite de e-CNPJ por representante legal com e-CPF**, e se a qualificação `legal_representative` resolve juridicamente para CPR de cooperativa | Comercial e escritório sócio | Pergunta 4 do panorama. Pode derrubar o fornecedor |
| 10 | **Endpoint REST que devolva as URLs de download** sem depender do payload do webhook | Suporte técnico | Bloco 5. Sem ele, perder um webhook significa perder o caminho do arquivo |
| 11 | **Polling de envelope é permitido?** A proibição publicada é nominal para documento | Suporte técnico | Bloco 4. Define se o job de varredura pode existir |
| 12 | **Prazo e custo de contratação do Widget Embedded em produção** | Comercial | Bloco 8. É gate comercial dentro da fase técnica |
| 13 | **Existe evento de falha de autenticação por certificado digital** fora da lista publicada | Suporte técnico | Sem ele, falha de certificado é silêncio |

Itens 1 a 4 e 8 são um único e-mail ao suporte técnico. Itens 5, 6, 9 e 12 são um único e-mail ao comercial. Os dois podem sair hoje, sem conta criada.

---

## 13. Contradições com os docs existentes

Cinco. Quatro mudam texto, uma muda número.

### 1. A Clicksign documenta três provedores de nuvem, não seis

**Onde:** `estudo-assinatura-panorama.md`, Tabela A, linha Clicksign: "Sim, seis provedores nominais: BirdID, SafeID, VIDaaS, DS Cloud, SerproID/NeoID, SyngularID". E a seção 6: "Único fornecedor que documenta nominalmente seis provedores de nuvem".

**O que as fontes dizem:** os seis aparecem uma vez, em parágrafo promocional do artigo 935. As duas páginas que descrevem o comportamento do sistema, o artigo 973 e o artigo 659, listam três: SafeID (Safeweb), BirdID (Soluti) e VIDaaS (Valid).

**Por que importa:** o argumento que colocou a Clicksign em 1º na trilha A era a cobertura de nuvem. Contra os cinco trust services pré-configurados da Lacuna (BirdID, NeoID, RemoteID, SafeID, VIDaaS), três é desvantagem. NeoID, que o panorama documenta como o mais detalhado dos cinco PSC, não aparece na lista de comportamento.

**Correção sugerida:** trocar "seis provedores nominais" por "três provedores confirmados na documentação de comportamento (SafeID, BirdID, VIDaaS); o material promocional cita mais três (DS Cloud, SerproID/NeoID, SyngularID) sem detalhamento".

### 2. O webhook da Clicksign tem 25 eventos de documento, não 2

**Onde:** `estudo-assinatura-panorama.md`, Tabela A, linha Clicksign: "eventos `close` e `document_closed`".

**O que muda:** a página de eventos lista 25 eventos de documento em quatro grupos, mais 7 de Aceite via WhatsApp. Nove são relevantes para a nossa máquina de estados, entre eles `sign` (progresso parcial por parte), `refusal`, `deadline` e `auto_close`.

**Correção sugerida:** substituir pela tabela da seção 5 deste documento, ou pela contagem e pelos nove relevantes.

### 3. O preço cheio da Clicksign está publicado, e é mais barato do que parecia

**Onde:** `estudo-assinatura-panorama.md`, Tabela B: "A página mistura preço promocional de primeira mensalidade com preço cheio". E a seção 7, item 1: "Preço real da Clicksign" listado como pendência comercial.

**O que muda:** o preço cheio por faixa está no objeto `pricing` do script da própria página de planos. Start começa em R$ 39,00/mês para 20 documentos e vai a R$ 199,00 para 200. A pendência deixa de existir para Start, Plus e Automação, e permanece só para o Avançado e para o carimbo do tempo.

**Também muda:** o panorama escreve "Start, Plus e Automação com limites de 200, 350 e 500 docs/mês". O Start vai até 200; Plus e Automação vão até 500 cada. E "API e webhook só nos planos Team e Enterprise" é regra da ZapSign; na Clicksign a API está no Start.

**Correção sugerida:** substituir a linha de preço da Clicksign pela tabela da seção 9 deste documento, e reduzir o item 1 da seção 7 do panorama ao Avançado e ao carimbo do tempo.

### 4. "Queremos guardar nós" não significa "só nós"

**Onde:** `plano-do-projeto.md`, tabela de critérios, linha "Quem guarda o documento: Queremos guardar nós". E `arquitetura-seguranca.md`, seção 7, item 4, que trata pedido de exclusão como procedimento definido.

**O que muda:** com a Clicksign, o documento assinado existe em dois lugares por padrão, e o segundo é um painel com controle de acesso próprio, invisível para a nossa tabela de acessos. A exclusão pela API só funciona em rascunho; apagar um documento finalizado é Lixeira mais "Excluir definitivamente" por administrador, no painel deles.

**Correção sugerida:** o critério vira "conseguimos guardar nós, e o fornecedor também guarda". Acrescentar em `arquitetura-seguranca.md` o painel do fornecedor como superfície de acesso a dado de registro, com número mínimo de logins e revisão periódica, e transformar o expurgo do lado do fornecedor em procedimento manual com responsável nomeado.

### 5. A Fase 2 não cabe em 32 a 40h nem no cenário de nuvem

**Onde:** `plano-do-projeto.md`, Fase 2: "Estimativa: 32 a 40h. A faixa depende de certificado em nuvem (mais simples) ou token físico". E `estudo-assinatura-panorama.md`, seção 6: "Plataforma (Clicksign ou ZapSign), só nuvem: 32 a 40h, como previsto".

**O que muda:** 51 a 75h, ponto médio 62h. A origem do estouro está na seção 10. A premissa errada dos dois documentos é que certificado em nuvem equivale a assinatura embutida. Na Clicksign o signatário é direcionado ao ambiente do provedor, o que coloca esta integração na linha "plataforma, com fluxo que sai da nossa tela" da própria tabela do panorama.

**Correção sugerida:** na rev. 3 de `plano-do-projeto.md`, Fase 2 passa a 51–75h para a Clicksign, com a nota de que a faixa fecha assim que o suporte responder os itens 1, 2, 4 e 8 da seção 12 deste documento. Total do projeto passa de ~332–356h para ~351–391h, antes da revisão da Fase 3 que `estudo-api-b3.md` já pediu.

---

## Anexo — fontes, com data de acesso

Todas acessadas em 12/09/2026.

### Documentação de desenvolvedor

| Fonte | URL |
|---|---|
| Índice completo da documentação | https://developers.clicksign.com/llms.txt |
| Informações gerais: ambientes, autenticação, JSON:API, versões | https://developers.clicksign.com/docs/informacoes-gerais |
| Primeiros passos: conta sandbox, geração de Access Token | https://developers.clicksign.com/docs/primeiros-passos |
| Guia de criação: o passo a passo padrão | https://developers.clicksign.com/docs/guia-de-criacao-o-passo-a-passo-padrao |
| Receita completa em cURL: criação e configuração do envelope | https://developers.clicksign.com/recipes/criação-e-configuração-do-envelope |
| Envelope: campos e regras de negócio | https://developers.clicksign.com/reference/envelope-campos-e-regras-de-negocio |
| Documentos: upload, modelo e duplicação | https://developers.clicksign.com/docs/documentos |
| Documento: campos e regras de negócio | https://developers.clicksign.com/reference/documento-campos-e-regras-de-negocio |
| Signatário: campos e regras de negócio | https://developers.clicksign.com/reference/signatario-campos-e-regras-de-negocio |
| Criar requisito de qualificação | https://developers.clicksign.com/reference/criar-requisito-qualificacao |
| Tipos de requisitos de qualificação (lista de papéis) | https://developers.clicksign.com/docs/adicionar-requisito-de-qualificacao |
| Criar requisito de autenticação | https://developers.clicksign.com/reference/criar-requisito-de-autenticacao |
| Tipos de requisitos de autenticação (`icp_brasil` e custos) | https://developers.clicksign.com/docs/tipos-de-requisitos-de-autenticacao |
| Ativar e editar envelope | https://developers.clicksign.com/reference/api-editar-envelope |
| Ativação assíncrona (em desenvolvimento) | https://developers.clicksign.com/docs/ativacao-escala-performatica |
| Referência da ativação dedicada (em desenvolvimento) | https://developers.clicksign.com/reference/api-ativar-envelope |
| Notificações e rate limit de 1/min | https://developers.clicksign.com/docs/notificacoes |
| Gerenciamento e consultas de envelopes | https://developers.clicksign.com/docs/gerenciamento-consultas-envelope |
| Excluir envelope (só `draft`) | https://developers.clicksign.com/reference/api-excluir-envelope |
| Excluir documento (só `draft`) | https://developers.clicksign.com/reference/api-excluir-documento |
| Webhooks: visão geral e proibição de polling | https://developers.clicksign.com/docs/introducao-a-webhooks |
| Criar webhook (OpenAPI, campos e `secret`) | https://developers.clicksign.com/reference/api-criar-webhook |
| Segurança de webhooks: HMAC `Content-Hmac` e IPs fixos | https://developers.clicksign.com/docs/seguranca-de-webhooks |
| Melhores práticas de webhooks | https://developers.clicksign.com/docs/melhores-praticas-webhooks |
| Eventos do documento (catálogo completo) | https://developers.clicksign.com/docs/eventos |
| Evento `document_closed` | https://developers.clicksign.com/docs/evento-document-closed |
| Exemplo do campo `document` (URLs de download) | https://developers.clicksign.com/docs/exemplo-documento |
| Limite de requisições e hosts de conteúdo S3 | https://developers.clicksign.com/docs/limite-de-requisicoes |
| Segurança: TLS 1.2 e cifras | https://developers.clicksign.com/docs/seguranca |
| FAQ da API: limites de tamanho, erros, autenticações | https://developers.clicksign.com/docs/faq-duvidas-e-problemas-comuns |
| Widget Embedded: introdução e ativação | https://developers.clicksign.com/docs/introducao-ao-widget-embedded |
| Widget Embedded: implementação, eventos JS | https://developers.clicksign.com/docs/implementando-o-widget-embedded |
| Assinatura incorporada (`embedded_signature`) | https://developers.clicksign.com/docs/instalacao-de-widget-assinatura-tokenless |
| Assinatura incorporada: implementações e testes | https://developers.clicksign.com/docs/assinatura-incorporada-implementacoes-e-testes |
| FAQ de migração 1.9 para 3.0 | https://developers.clicksign.com/docs/faq-migracao |

### Central de ajuda

| Fonte | URL |
|---|---|
| Certificado digital em nuvem (redirect ao provedor, três provedores) | https://ajuda.clicksign.com/article/973-certificado-digital-em-nuvem |
| Certificados digitais aceitos (A1 e A3, só e-CPF, seis autoridades) | https://ajuda.clicksign.com/article/935-certificados-digitais-aceitos-pela-clicksign |
| Assinando com certificado digital (Web PKI, escolha local ou nuvem) | https://ajuda.clicksign.com/article/659-assinando-com-certificado-digital |
| Log presente nos documentos assinados | https://ajuda.clicksign.com/article/230-log-presente-nos-documentos-assinados |
| Como obter o arquivo PAdES | https://ajuda.clicksign.com/article/818-como-obter-o-arquivo-pades-do-documento-assinado |
| Carimbo do tempo: o que é e como contratar | https://ajuda.clicksign.com/article/1019-carimbo-do-tempo |
| Carimbo do tempo: como consultar, validador do ITI | https://ajuda.clicksign.com/article/1020-carimbo-do-tempo-como-consultar |
| Armazenamento de documentos | https://ajuda.clicksign.com/article/564-armazenamento-de-documentos |
| Como excluir um documento ou pasta | https://ajuda.clicksign.com/article/119-e-possivel-excluir-um-documento-pasta |

### Comercial

| Fonte | URL |
|---|---|
| Planos e preços (tabela de preço cheio no objeto `pricing` do script da página) | https://www.clicksign.com/planos |
