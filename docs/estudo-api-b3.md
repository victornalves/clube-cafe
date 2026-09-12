# Estudo da API da B3 — Registro de CPR Física

**Frente 3** · 12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 3) e `maquina-de-estados.md`

---

## O que este documento responde

Autenticação, payload, códigos de erro classificados, consulta de status, idempotência, diferença entre homologação e produção, identidade do participante, e a estimativa fechada da Fase 3.

## O que ele não responde, e por quê

A documentação técnica da API de CPR da B3 é fechada. O portal B3 for Developers lista as APIs de CPR no grupo Balcão, com versão e descrição, mas o link de documentação técnica exige login de cliente B2B contratado. A página do catálogo diz, literalmente: "Não oferecemos acesso direto às APIs para pessoas físicas. Nossas APIs são exclusivamente destinadas ao consumo de clientes B2B." (https://developers.b3.com.br/apis, acesso 12/09/2026).

Consequência prática: **nomes de campo JSON, endpoints de CPR e códigos de erro de negócio não estão publicados.** Tudo que este documento afirma sobre eles vem de três fontes públicas adjacentes e está marcado como tal:

| Fonte pública usada | O que ela cobre | Confiabilidade para CPR |
|---|---|---|
| Layout em Implementação CPR 2.0 (arquivo posicional) | Os 94 campos do registro de CPR, com formato, tamanho e domínio | Alta para o modelo de dados. É o mesmo negócio, canal diferente |
| Manual API Gravame v1.2 e Catálogo APIs iMercado Balcão v1.01 | Autenticação, endpoints base, envelope de erro, códigos HTTP | Alta. Mesma plataforma (`api-balcao*.b3.com.br`), mesmo padrão de casa |
| Manual de Normas de CDA, WA e CPR (05/12/2022) | Papéis, responsabilidades, baixa e retificação | Alta. É norma, não implementação |

Quem quiser o nome exato do campo JSON precisa do pacote de acesso. Lista do que pedir na última seção.

---

## 1. Autenticação

Não é API key. É **OAuth 2.0 Client Credentials + Mutual SSL (mTLS)**, os dois juntos, em toda chamada.

Fonte: https://developers.b3.com.br/index.php?id=29&option=com_content&view=article (Autenticação Client Credentials Balcão, acesso 12/09/2026) e Manual API Gravame v1.2, seção 9 (https://clientes.b3.com.br/c/document_library/get_file?groupId=20119&uuid=5b28dc9d-7bf2-7d66-864d-5bb3a2efc837, acesso 12/09/2026).

### O fluxo, passo a passo

1. **Receber o pacote de acesso da B3.** Um `.zip` com os arquivos de certificado digital (`.cer`, `.crt`, `.csr`, `.key`, `.p12`) e um arquivo-texto com `client_id`, `client_secret` e a senha do `.p12`. Citação literal do manual Gravame: "O pacote de segurança é o seu passaporte e identificador na B3: alguém com esses dados pode se passar pela instituição acessando as APIs."
2. **Carregar o `.p12` no keystore da aplicação**, com a senha do pacote. Sem isso o handshake TLS falha antes de qualquer HTTP.
3. **Implementar certificate pinning** do certificado raiz da B3. A B3 pede isso explicitamente: "Pinagem do certificado é o processo de extrair a chave do certificado, para que possa ser inserida no código de sua aplicação" (https://developers.b3.com.br/seguranca, acesso 12/09/2026).
4. **POST no endpoint de token**, já dentro do canal mTLS:
   - Certificação: `https://api-balcao-cert.b3.com.br/api/oauth/token`
   - Produção: `https://api-balcao.b3.com.br/api/oauth/token`
   - Header: `Content-Type: application/x-www-form-urlencoded`
   - Body: `grant_type=client_credentials`, `client_id`, `client_secret`
5. **Guardar o `access_token`** (JWT) e o `expires_in` retornados. Resposta documentada: `access_token`, `token_type` ("Bearer"), `expires_in`, `scope` ("resource.WRITE resource.READ").
6. **Chamar a API de CPR** com `Authorization: Bearer <token>` **e o mesmo certificado mTLS**. O token sozinho não passa.
7. **Renovar o token antes de expirar.** A B3 recomenda uma autenticação e reúso do token para múltiplas chamadas (FAQ, https://developers.b3.com.br/faq, acesso 12/09/2026).

### Tempo de expiração: a documentação da B3 se contradiz

| Fonte | Valor | Acesso |
|---|---|---|
| Autenticação Client Credentials Balcão | `"expires_in": 3600` (1h) | 12/09/2026 |
| FAQ B3 for Developers | 43200 s (12h) | 12/09/2026 |
| Manual API Gravame v1.2 | texto diz 12h, exemplo mostra `"expires_in": "8640"` | 12/09/2026 |

Três números para a mesma plataforma. Decisão de implementação: **ler `expires_in` da resposta e renovar a 80% do valor.** Nunca constante no código, nunca `cron` de hora em hora presumindo 3600. Custa nada e elimina uma classe inteira de 401 em produção.

Um detalhe do exemplo: `expires_in` vem como string (`"8640"`) em um manual e como número (`3600`) no outro. Parsear tolerando os dois.

### Ciclo de vida e rotação

Nenhuma fonte pública documenta validade do certificado, procedimento de renovação ou rotação de `client_secret`. A página de Segurança da B3 cobre mTLS, pinning, TLS 1.2+ e rate limiting, e não cobre expiração nem rotação (acesso 12/09/2026).

Isso é problema operacional real e não técnico: certificado `.p12` vence, e quem recebe o aviso é o escritório sócio, não nós. Entra na lista de pedidos.

### Impacto no `arquitetura-seguranca.md`

O doc de segurança classifica a credencial B3 como "API key B3" no cofre de segredos. O ativo real é **um binário (`.p12`) mais três strings mais uma senha**, por ambiente. Cofre de segredos que só guarda string não resolve. Ver "Contradições" no fim.

---

## 2. Payload de registro de CPR física de café

### Como ler esta seção

A B3 aceita registro de CPR por três canais: tela do sistema, troca de arquivos e API (https://clientes.b3.com.br/w/novo-sistema-de-registro-da-cedula-do-produto-rural-cpr-, acesso 12/09/2026). O layout abaixo é o **canal de arquivo**, publicado no comunicado 044/2020-VPC. É o mesmo modelo de negócio que a API expõe, com nomes de campo diferentes.

O padrão de casa da B3 nas APIs de Balcão é JSON com envelope `{"data": {...}}` e nomes em inglês camelCase (`financialInstrumentCode`, `participantOriginAccountIdentification`, `selfNumber`), conforme Manual API Gravame v1.2 e Catálogo iMercado Balcão v1.01. **Use os campos abaixo para modelar o domínio e dimensionar o formulário. Não chute o nome JSON.**

Fonte: Layout em Implementação CPR 2.0, versão fevereiro/2021, atualização 27/11/2020 (https://www.b3.com.br/data/files/47/F4/77/28/C0526710DDCBB167AC094EA8/Layout%20em%20Implementacao%20-%20CPR%202.0_v4.pdf, acesso 12/09/2026). Registro de CPR, versão de layout 00011. Tamanho total do arquivo: 1739 caracteres.

Legenda da coluna Fonte: **OF** = confirmado no layout oficial. **INF** = inferência nossa, precisa de confirmação.

### Identificação e partes

| Campo | Tipo | Obrig. | Formato | Fonte | Observação |
|---|---|---|---|---|---|
| Conta do Registrador | numérico 8 | Sim | Código Cetip do participante | OF | **É a conta do escritório sócio.** Ver seção 7 |
| Cód. ISIN | texto 12 | Sim | ISIN | OF | Atribuído pela B3. Não é gerado por nós |
| Tipo CPR | texto 1 | Sim | `P` ou `F` | OF | **`P` = Produto.** É o nosso caso. `F` = Financeiro |
| Data de Emissão | numérico 8 | Sim | `AAAAMMDD` | OF | Entra na chave de unicidade interregistradoras |
| Data de Vencimento/Entrega | numérico 8 | Sim | `AAAAMMDD` | OF | |
| Nome (emitente) | texto 100 | Sim | Razão social ou nome | OF | Produtor rural. Se produção de terceiros, nome da cooperativa |
| CPF/CNPJ (emitente) | numérico 15 | Sim | Sem máscara | OF | |
| Natureza (emitente) | texto 2 | Sim | `PF` ou `PJ` | OF | Obrigatório explícito no layout |
| UF (emitente) | texto 2 | Sim | Sigla | OF | |
| Nome do Município (emitente) | texto 50 | Sim | Nome por extenso | OF | Texto livre, não código IBGE |
| Nome do Credor original | texto 100 | Sim | | OF | "Campo de preenchimento obrigatório" no layout |
| CPF/CNPJ Credor original | numérico 15 | Sim | | OF | Entra na chave de unicidade |
| Conta do Custodiante | numérico 8 | Sim | Código Cetip | OF | "Preenchimento obrigatório" |
| Conta do Favorecido | texto 8 | Cond. | Código Cetip | OF | Obrigatório se Depósito = `S` |
| CPF/CNPJ do Favorecido | texto 15 | Cond. | | OF | |
| Natureza do Favorecido | texto 2 | Cond. | `PF` / `PJ` | OF | |
| Código do Agente de Pagamento | numérico 8 | Não | Código Cetip | OF | |

O corretor opcional previsto em `entendimento-do-projeto.md` **não tem campo dedicado neste layout.** As partes que a B3 reconhece são emitente, credor original, garantidor, custodiante, favorecido e agente de pagamento. Corretor, se existir no contrato, é cláusula do documento e não campo do registro. Confirmar com o jurídico do escritório.

### Produto, quantidade e entrega

Esta é a parte que define o formulário do café.

| Campo | Tipo | Obrig. | Formato | Fonte | Observação |
|---|---|---|---|---|---|
| Código do Produto | texto 30 | Sim | Domínio fechado | OF | Vem do arquivo `AAAAMMDD_Cestas_Produtos` da B3 |
| CLASSE/TIPO PH | numérico 10 | Sim | Domínio fechado | OF | Vem de `AAAAMMDD_Cadastro_Curvas_Moedas_Feeder_Dominios` |
| SAFRA | numérico 10 | Sim | Domínio fechado | OF | "Período de Produção Agrícola". Mesmo arquivo de domínios |
| Característica | texto 35 | Não | Texto livre | OF | "Descrição detalhada sobre o produto". 35 caracteres é pouco |
| Quantidade | numérico 10 | Sim | Inteiro | OF | Quantidade do produto a entregar |
| Unidade de Medida | texto 30 | Sim | Domínio fechado | OF | Vem de `Cestas_Produtos`. **"Sacas" precisa existir nesse domínio** |
| Forma de Acondicionamento | texto 30 | Sim | Domínio fechado | OF | Vem de `Cestas_Produtos` |
| Situação | numérico 1 | Sim | `0` / `1` | OF | `0` = A PRODUZIR, `1` = PRODUZIDO |
| Produção | numérico 1 | Sim | `0` / `1` | OF | `0` = PRÓPRIA, `1` = TERCEIROS |
| Imóvel | texto 35 | Sim | Texto livre | OF | Local da produção. 35 caracteres |
| Prazo do Documento | numérico 3 | Sim | Dias | OF | |
| Local de Entrega | texto 35 | Sim | Texto livre | OF | |
| UF do Local de Entrega | texto 2 | Sim | Sigla | OF | |
| Município do Local de Entrega | texto 50 | Sim | Nome por extenso | OF | |
| Moeda | numérico 3 | Não | Anexo 1 do layout | OF | Moeda de cotação do produto agrícola |

**Achado que muda a estimativa.** Cinco campos centrais do café (produto, classe/tipo, safra, unidade de medida, forma de acondicionamento) têm domínio fechado carregado de **arquivos públicos da B3 distribuídos pelo módulo Transferência de Arquivos**, não por endpoint REST. São arquivos datados (`AAAAMMDD_`), ou seja, mudam. Isso é uma segunda integração, de natureza diferente da API, e não estava prevista em `plano-do-projeto.md`.

Se a API de CPR expuser endpoints de domínio equivalentes, esse trabalho some. Não dá para saber sem a documentação. Está refletido como faixa na estimativa.

### Valores e garantias

| Campo | Tipo | Obrig. | Formato | Fonte | Observação |
|---|---|---|---|---|---|
| Quantidade de emissão | numérico 14 | Sim | | OF | "Campo de preenchimento obrigatório" |
| Valor de Emissão | 9(10),(8) | Sim | Preço unitário | OF | 10 inteiros, 8 decimais |
| Valor Financeiro de emissão | 9(16)9(2) | Sim | | OF | Quantidade × preço unitário. **Calculado, precisa bater** |
| Tipo de Garantia | numérico 1 | Sim | `0`–`9` | OF | `0` Aval Próprio, `1` Sem Garantia, `2` Aval de Terceiros, `3` Seguro, `4` Hipoteca, `5` Fiança, `6` Penhor, `7` Alienação Fiduciária, `8` Cessão Fiduciária, `9` Outros |
| Garantidor | numérico 8 | Cond. | Código Cetip | OF | |
| CPF/CNPJ (Garantidor) | numérico 15 | Cond. | | OF | Obrigatório quando garantia = Aval de Terceiros e conta do garantidor vazia |
| Forma de Pagamento | numérico 2 | Sim | `01`–`07` | OF | **`07` = Parcelado, disponível apenas para CPR de produto** |
| Rentabilidade/Indexador | numérico 4 | Sim | `0000`,`0001`,`0099`,`0009`,`0018`,`0070`,`0567` | OF | VCP, DI, Prefixada, IGP-M, IPCA, Dólar PTAX, Euro |
| Data Início Rentabilidade | numérico 8 | Sim | `AAAAMMDD` | OF | ≥ Data de Emissão e < Data de Vencimento |
| Finalidade | numérico 10 | Sim | Domínio fechado | OF | Mais um domínio vindo de arquivo público |
| Emissão Eletrônica/Digital | texto 1 | Sim | `S` / `N` | OF | **`S` no nosso caso.** Amarra direto com a Frente 2 |

### SCR e identificação de operação

| Campo | Tipo | Obrig. | Formato | Fonte | Observação |
|---|---|---|---|---|---|
| Ativo Informado no SCR? | texto 1 | Sim | `S` / `N` | OF | Se `S`, sete campos adicionais viram obrigatórios e se `N`, o preenchimento deles é proibido |
| Detalhamento do Cliente | texto 14 | Cond. | | OF | Responsável pelo registro no SCR |
| Natureza do Cliente | texto 2 | Cond. | `PF`/`PJ` | OF | |
| Código do Cliente (CPF/CNPJ do Devedor) | texto 14 | Cond. | | OF | |
| Código do Contrato | texto 40 | Cond. | | OF | Entra na chave de unicidade interregistradoras |
| Modalidade da Operação | numérico 4 | Cond. | ~90 valores | OF | Domínio enorme, listado no layout |
| IPOC | texto 100 | Cond. | | OF | Identificador padronizado da operação de crédito |
| Código Ref Bacen | texto 11 | Não | Recor/Sicor | OF | |
| Número do Controle | numérico 10 | **Não** | | OF | Ver seção 5 |
| Descrição Adicional | texto 300 | Não | Texto livre | OF | |

**Decidir cedo se as CPRs do clube entram no SCR.** É um `S`/`N` que liga ou desliga sete campos obrigatórios e um domínio de 90 valores. Pergunta para o escritório sócio, não para nós.

### O que o layout não cobre e a lei exige

A Lei 8.929/1994, art. 3º, exige na CPR: denominação "Cédula de Produto Rural", data da entrega, nome do credor e cláusula à ordem, promessa pura e simples de entregar o produto com especificações de qualidade e quantidade, local e condições da entrega, descrição dos bens vinculados em garantia, data e lugar da emissão, e **assinatura do emitente** (https://www.normaslegais.com.br/legislacao/lei-8929-1994.htm, acesso 12/09/2026).

Cláusula à ordem, condições de entrega e assinatura ficam no documento, não no registro. O registro é a projeção estruturada do documento. Isso confirma a regra já escrita em `maquina-de-estados.md`: dado que só existe no documento e está errado exige reassinatura.

---

## 3. Códigos de erro, classificados

### O que está publicado

Três documentos públicos da B3 convergem no mesmo padrão.

**Envelope de erro** (Manual API Gravame v1.2 e Catálogo iMercado Balcão v1.01, acesso 12/09/2026):

| Campo | Card. | Tipo | Tamanho |
|---|---|---|---|
| `errors[].code` | 1..1 | string | max 10 |
| `errors[].title` | 1..1 | string | max 100 |
| `errors[].detail` | 1..1 | string | max 2000 |

**Regra de negócio explícita**, citada no manual Gravame: "Será informado o código 422 default para quando existir o retorno de um erro de negócio, no campo code."

**Componente `BusinessStatus`**: o documento "APIs B3 Considerações Gerais" v1.0 diz que as APIs retornam o componente `BusinessStatus` "com os códigos necessários para análise do requisitante", e manda consultar o Swagger de cada API para o comportamento (https://www.b3.com.br/data/files/2B/41/CC/5D/10F42610D290A226790D8AA8/APIs-B3-Visao-Geral-versao-1.0.pdf, acesso 12/09/2026). O Swagger da CPR é fechado.

**Subset HTTP oficial** (mesma fonte, e confirmado no Catálogo iMercado Balcão v1.01): 200, 201, 301, 400, 401, 404, 405, 408, 415, 421, 422, 429, 500, 501, 503, 504.

### A tabela

Classificação nossa, a partir da semântica documentada de cada código. Coluna "Caminho" remete aos quatro caminhos de `maquina-de-estados.md`.

| HTTP | Significado documentado | Classe | Caminho | Regra operacional |
|---|---|---|---|---|
| 201 | Recurso criado | Sucesso | — | `REGISTRADO`. Guardar o identificador retornado |
| 400 | "A requisição não foi executada porque está mal formada" | Definitivo | **2. Corrigir payload** | Erro nosso de serialização. Nunca chega no membro |
| 401 | "Operação recusada por problema de autenticação. Cabeçalho ausente/inválido ou token inválido" | Transitório **na 1ª vez** | **1. Retry** | Renovar token e reenviar **uma vez**. Falhou de novo, é credencial ou certificado. Alerta para infra, não para o backoffice |
| 404 | Recurso não encontrado | Definitivo | **2. Corrigir payload** | Endpoint ou versão errados. Bug de deploy |
| 405 | "Método não suportado" | Definitivo | **2. Corrigir payload** | Bug nosso. A API Gravame, por exemplo, só aceita POST |
| 408 | Request Timeout | Transitório | **1. Retry, com ressalva** | **Consultar antes de reenviar.** Ver seção 5 |
| 415 | Unsupported media type | Definitivo | **2. Corrigir payload** | `Content-Type` errado |
| 421 | Misdirected Request | Definitivo | **2. Corrigir payload** | Host/roteamento. Checar ambiente de destino |
| 422 | "Bem formada, mas não pôde ser processada devido à lógica de negócios" | **Depende do `errors[].code`** | **2 ou 3** | Ver abaixo. É o caso que mais vai aparecer |
| 429 | Too Many Requests. B3 aplica throttling por serviço e por usuário logado | Transitório | **1. Retry** | Backoff exponencial obrigatório. Retry imediato piora |
| 500 | "Erro no gateway da API ou no microsserviço" | Transitório | **1. Retry, com ressalva** | Consultar antes de reenviar |
| 501 | Not Implemented | Definitivo | **4. Cancelar** ou escalar | Funcionalidade indisponível. Ninguém corrige do nosso lado |
| 503 | "Serviço indisponível no momento" | Transitório | **1. Retry** | Janela de manutenção. Backoff longo |
| 504 | "Servidor não pôde responder em tempo hábil" | Transitório | **1. Retry, com ressalva** | Consultar antes de reenviar |
| Timeout de socket / TLS handshake | Sem resposta HTTP | Transitório | **1. Retry, com ressalva** | Consultar antes de reenviar |

### O 422 é o caso interessante

**O código HTTP nunca separa o caminho 2 do caminho 3.** Um 422 pode ser:

| Situação | Exemplo | Caminho |
|---|---|---|
| Domínio desatualizado do nosso lado | Código de produto que saiu do `Cestas_Produtos` | **2. Corrigir payload** |
| Erro de mapeamento nosso | Valor financeiro que não bate com quantidade × preço unitário | **2. Corrigir payload** |
| Campo condicional violado | `Ativo Informado no SCR = N` com campos de SCR preenchidos | **2. Corrigir payload** |
| Referência inválida | Conta Cetip de custodiante inexistente | **2. Corrigir payload**, ou cadastro |
| Dado do contrato assinado está errado | Safra, quantidade, local de entrega, CPF do emitente divergentes do documento | **3. Reassinatura** |
| Duplicidade na base interregistradoras | Mesma chave de unicidade já registrada | **4. Cancelar** ou reconciliar. Ver seção 5 |

Quem decide entre 2 e 3 é o operador, com a regra que já está escrita em `maquina-de-estados.md`: o dado errado aparece no documento assinado? Se não, corrige o payload. Se sim, reassina.

Isso tem consequência direta na tela de resolução: ela precisa mostrar `errors[].code`, `errors[].title` e `errors[].detail` **na íntegra**, lado a lado com o campo correspondente do documento assinado. `detail` tem até 2000 caracteres. A tela precisa comportar isso sem truncar.

### O que falta para fechar a tabela

Os valores concretos de `errors[].code` da API de CPR. São strings de até 10 caracteres, definidas no Swagger fechado. Sem eles, o roteamento automático entre caminho 2 e caminho 3 não existe e **todo 422 vai para a fila do backoffice**, com um humano decidindo. Isso é aceitável no MVP e é exatamente o desenho de `maquina-de-estados.md`. Com a lista de códigos em mãos, dá para pré-classificar os 422 mais comuns e reduzir a fila.

---

## 4. Consulta de status e reconciliação

### Existe consulta

Sim. O catálogo Balcão do portal B3 for Developers descreve a API de CPR incluindo "Consulta de Características de CPR por Instrumento Financeiro", "Consulta de Características de CPR por Número de Controle Interno", "Consulta de Custódia" e "Consulta de Operação" (https://developers.b3.com.br/apis/api-balcao, acesso 12/09/2026).

Duas dessas resolvem reconciliação:

| Consulta | Serve para |
|---|---|
| Por Instrumento Financeiro | Confirmar que o ativo existe na B3, a partir do código que a B3 devolveu |
| **Por Número de Controle Interno** | **Descobrir se um registro existe quando não temos o retorno da B3.** É a consulta que fecha o buraco do timeout |

A segunda é a peça que torna a reconciliação independente de retorno síncrono. Se conseguirmos gravar o nosso identificador no campo "Número do Controle" (numérico, 10 posições, opcional no layout CPR 2.0), consultamos por ele depois de qualquer falha ambígua.

### Existe webhook

**Para a API de CPR, não há evidência pública de webhook.** O que existe, e é coisa diferente, é o iMercado.

O Catálogo de APIs iMercado Balcão v1.01 descreve um modelo de difusão para "acompanhamento de status de operações registradas no NoMe", em que "a implementação do endpoint se dá por parte do cliente e deve ter um canal aberto via Internet, de maneira que a B3 será a consumidora do webservice (...) entregando as informações de status de operação através do verbo POST" (https://www.b3.com.br/data/files/63/D1/10/34/DD9FE710638D2FE7AC094EA8/Catalogo_APIs_iMercado_AcompanhamentoeCaracteristicas_v1.01.pdf, acesso 12/09/2026).

Três razões para não contar com isso:

1. É produto separado (iMercado), com contratação e parametrização próprias, pelo telefone (11) 2565-5996 ou `ProdutoiMercado@b3.com.br`, conforme o próprio catálogo.
2. A autenticação é **basic auth**, com usuário e senha enviados à B3 por e-mail ao SAT. Modelo de segurança mais fraco que o mTLS da API de registro, e exige expor um endpoint público nosso.
3. O escopo publicado na v1.01 é captação bancária, debêntures e comitentes. CPR não aparece.

### Decisão de arquitetura

**Polling. Sem webhook no desenho da Fase 3.**

| Gatilho | Ação |
|---|---|
| Resposta 201 síncrona | Grava identificador, vai para `REGISTRADO`. Consulta de confirmação assíncrona em seguida |
| Resposta 4xx/5xx conhecida | Aplica a tabela da seção 3 |
| Timeout, 5xx ou erro de rede | **Consulta por Número de Controle Interno antes de qualquer reenvio** |
| Job periódico | Varre registros parados em `ENVIANDO_B3` há mais de N minutos e reconcilia |

O job de reconciliação não é enfeite. É o que impede que uma janela de instabilidade da B3 deixe registros travados em `EM PROCESSAMENTO` para o membro, sem ninguém saber.

Respeitar o throttling da B3 nesse job. O limite é definido pela B3 e não é publicado, e o estouro devolve 429 (https://developers.b3.com.br/seguranca, acesso 12/09/2026).

Prazo legal que dá folga ao desenho: a CPR emitida a partir de 11/08/2022 tem **30 dias úteis** da emissão para ser registrada, sob pena de perder validade e eficácia (Lei 8.929/1994, art. 12, com redação da Lei 14.421/2022; antes eram 10 dias úteis, redação da Lei 13.986/2020). Trinta dias úteis é muito tempo para reconciliar. Retry com backoff longo não põe o ativo em risco, e o backoffice tem folga real para resolver uma falha. Esse número deveria aparecer na fila de pendências do painel como prazo restante por registro.

---

## 5. Idempotência

### A resposta curta

**Não há chave de idempotência documentada publicamente.** Nenhum dos três manuais públicos de Balcão menciona `Idempotency-Key`, header de deduplicação ou semântica de reenvio seguro.

### O que existe, e que usamos no lugar

**Campo "Número do Controle"** — numérico, 10 posições, marcado como "Campo de preenchimento opcional" no layout CPR 2.0. O equivalente na API Gravame é o campo `selfNumber` (string, max 10, descrito como "Meu Número"). A API de CPR tem consulta "por Número de Controle Interno", o que confirma que esse valor é consultável depois.

É o identificador do participante. Preenchido com o nosso id de registro, ele dá:
- Consulta determinística após falha ambígua.
- Correlação entre o nosso banco e a base da B3, para auditoria.

O que ele **não** dá, até prova em contrário: garantia de que a B3 rejeita um segundo POST com o mesmo valor. Nenhuma fonte pública diz que o campo é único.

**Chave de unicidade interregistradoras.** Desde 29/04/2024 a B3 opera interoperabilidade de CPR sob a Resolução BCB nº 304. A unicidade é verificada "por meio de uma chave única, gerada automaticamente pela concatenação dos seguintes campos: documento do credor originário; documento do devedor; data de emissão; e código do contrato original" (https://clientes.b3.com.br/w/interoperabilidade-cpr, acesso 12/09/2026). A validação roda contra uma base centralizada compartilhada entre as registradoras autorizadas.

Essa chave é uma rede de proteção contra duplicata real. Ela impede que a mesma CPR seja registrada duas vezes, inclusive em registradoras diferentes. Mas ela funciona rejeitando, e a rejeição chega como erro de negócio (422), não como "já existe, aqui está o registro anterior".

### A regra de implementação

> Nenhum reenvio automático depois de resposta ambígua. Timeout, 5xx e erro de rede disparam **consulta**, não POST.

Fluxo do caminho 1 (retry) de `maquina-de-estados.md`, ajustado à realidade da B3:

```
falha ambígua (timeout / 5xx / rede)
        │
        ▼
consulta por Número de Controle Interno
        │
   ┌────┴────┐
   ▼         ▼
 achou    não achou
   │         │
   ▼         ▼
REGISTRADO  reenviar mesmo payload
(reconcilia)
```

Sem esse passo, um timeout de rede vira CPR duplicada, ou 422 de duplicidade que o operador vai passar meia hora investigando.

Isso acrescenta uma caixa ao diagrama de `maquina-de-estados.md`. Anotado em "Contradições".

---

## 6. Homologação vs. produção

| Dimensão | Certificação | Produção |
|---|---|---|
| Host | `https://api-balcao-cert.b3.com.br` | `https://api-balcao.b3.com.br` |
| Token | `/api/oauth/token` no mesmo host | `/api/oauth/token` no mesmo host |
| Healthcheck | `/healthcheck` | `/healthcheck` |
| Credencial | Pacote de acesso próprio | Pacote de acesso próprio, distinto |
| Certificado mTLS | Do pacote de certificação | Do pacote de produção |

Fonte: https://developers.b3.com.br/index.php?id=29&option=com_content&view=article e Manual API Gravame v1.2, seção 5 (acesso 12/09/2026).

Só o hostname muda. Todo o resto do código é idêntico, o que torna a troca de ambiente uma variável de configuração. Isso está alinhado com o que `arquitetura-seguranca.md` já exige.

**Existe `/healthcheck` nos dois ambientes.** Usar. É o jeito de distinguir "a B3 está fora" de "o nosso registro foi recusado" antes de acordar alguém do backoffice.

### O ambiente de certificação é fiel?

Não temos como afirmar para a API de CPR. O que dá para dizer:

- A B3 mantém ambiente de certificação dedicado à homologação de participantes, com os mesmos caminhos de endpoint.
- Em outro produto (Nova Área Logada), a B3 descreve o ambiente de Certificação como autosserviço, gratuito, disponível 24/7, com massa de testes, e a produção como contratação formal precedida de self-assessment de segurança e avaliação via Security Scorecard (Manual Técnico APIs Área Logada da B3, 31/03/2022, https://www.b3.com.br/data/files/60/72/19/05/45CDF7104532BBF7AC094EA8/Manual%20Tecnico%20-%20APIs%20vf.pdf, acesso 12/09/2026). **Esse manual é de outro produto.** Não assumir que o mesmo autosserviço vale para Balcão/CPR.
- O contexto do projeto diz que a homologação já está aprovada via conta do escritório sócio, o que sugere que esse passo já foi vencido.

Três perguntas que só o pacote de acesso responde: a massa de testes de certificação inclui produto café com safra válida? Os arquivos de domínio (`Cestas_Produtos`, `Cadastro_Curvas_Moedas_Feeder_Dominios`) existem em certificação com o mesmo conteúdo de produção? O ambiente de certificação valida a chave de unicidade interregistradoras, ou isso só existe em produção?

A terceira é a que dói. Se a validação de duplicidade não roda em certificação, o comportamento de duplicata só aparece em produção, com CPR real.

---

## 7. Identidade do participante

### Como ela entra na chamada

Por três caminhos ao mesmo tempo, e isso importa.

| Vetor | Onde aparece | Configurável? |
|---|---|---|
| **Certificado mTLS** | Handshake TLS. O manual Gravame diz: "APIs de lançamento usarão client credentials (Client ID + Secret) no padrão OAuth 2.0 para obtenção de tokens JWT + Mutual SSL **contendo login NoMe**" | Sim. É um arquivo `.p12` + senha |
| **client_id / client_secret** | Body do POST de token | Sim. São strings |
| **Contas Cetip no payload** | Campos "Conta do Registrador" (8 dígitos), "Conta do Custodiante", "Conta do Favorecido", "Código do Agente de Pagamento" | Sim. São valores de dado |

A frase "Mutual SSL contendo login NoMe" é o achado importante: **a identidade do participante está embutida no certificado.** Trocar de participante é trocar o `.p12`, o `client_id`, o `client_secret` e as contas Cetip do payload. Não é reescrever código.

### Confirma a mitigação de risco?

**Confirma, com uma correção de escopo.**

`entendimento-do-projeto.md` pede que "a identidade do participante B3 vire configuração, nunca constante, para que uma conta própria no futuro seja troca de variável e não reescrita". Isso é viável e é o desenho certo. O que muda é o que entra no pacote de configuração:

```
b3:
  ambiente: certificacao | producao
  host: https://api-balcao-cert.b3.com.br
  oauth:
    client_id:      <do cofre>
    client_secret:  <do cofre>
  mtls:
    keystore_p12:   <do cofre, binário>
    keystore_senha: <do cofre>
  participante:
    conta_registrador:   <8 dígitos>
    conta_custodiante:   <8 dígitos>
    conta_favorecido:    <8 dígitos>
    agente_pagamento:    <8 dígitos>
```

Nove valores, nenhum deles constante no código. Trocar o escritório sócio por conta própria é trocar esse bloco inteiro e rodar o ciclo de certificação de novo.

Duas coisas que a configuração não resolve, e que precisam de acordo escrito com o escritório:

1. **Responsabilidade legal.** O Manual de Normas de CDA, WA e CPR (05/12/2022, art. 36, inciso II) diz que cabe ao Agente de Registro "incluir no sistema da B3 e se responsabilizar pela autenticidade e veracidade das informações relacionadas à CPR e suas garantias" (https://www.b3.com.br/lumis/portal/file/fileDownload.jsp?fileId=8AE490CA824456A301825A0EA0AD6677, acesso 12/09/2026). Quem responde pelo dado que a nossa plataforma envia é o escritório. Isso já está identificado como risco em `entendimento-do-projeto.md` e a norma confirma.
2. **Vencimento do certificado.** O aviso vai para o escritório. Precisa de um canal e um responsável nomeado, ou a integração cai em produção sem aviso.

---

## 8. Estimativa fechada da Fase 3

`plano-do-projeto.md` traz 32 a 40h, "a fechar depois da leitura da documentação na Fase 0". A leitura foi feita, dentro do que é público. O número sobe.

Premissa: a Fase 1 já entregou a máquina de estados em duas camadas, a tela de resolução, os quatro caminhos e o envio B3 mockado. A Fase 3 troca o mock pela API real.

| # | Bloco | Horas | O que está dentro |
|---|---|---|---|
| 1 | Autenticação mTLS + OAuth2 | 10–14 | Keystore `.p12`, certificate pinning, cliente TLS, cache de token lendo `expires_in`, renovação a 80%, tolerância a `expires_in` string ou número, tratamento de 401 |
| 2 | Mapeamento do payload | 12–18 | ~45 campos relevantes para CPR física de café, campos condicionais (SCR, depósito, garantia, rentabilidade), validação de consistência antes do envio (valor financeiro = quantidade × PU, data início rentabilidade dentro da janela) |
| 3 | **Domínios da B3** | 6–14 | Carga e atualização de `Cestas_Produtos` e `Cadastro_Curvas_Moedas_Feeder_Dominios`. **6h se houver endpoint REST de domínio. 14h se for integração com o módulo de Transferência de Arquivos** |
| 4 | Cliente da API + erros | 8–10 | Chamada de registro, parse do envelope `errors[]`, `BusinessStatus`, tabela da seção 3, roteamento automático dos casos claros, fila de pendências para os 422 ambíguos |
| 5 | Consulta e reconciliação | 8–10 | Consulta por Número de Controle Interno, consulta por instrumento financeiro, job periódico de varredura, respeito ao throttling, uso do `/healthcheck` para distinguir indisponibilidade de recusa |
| 6 | Idempotência | 4–6 | Número do Controle preenchido com o nosso id, guarda de "consultar antes de reenviar", detecção de duplicidade pela chave de unicidade, trava contra POST concorrente do mesmo registro |
| 7 | Identidade como configuração | 3–4 | Os nove valores da seção 7, cofre com suporte a binário, troca de ambiente por variável |
| 8 | Ciclo de certificação com a B3 | 8–14 | Conectividade, massa de testes, registro de ponta a ponta em certificação, ida e volta com o SAT. **É o bloco menos previsível: depende do tempo de resposta da B3** |
| 9 | Observabilidade e testes | 6–8 | Id de correlação por chamada (exigência de `arquitetura-seguranca.md`), mascaramento de credencial em log, testes com respostas de erro simuladas para os quatro caminhos |
| | **Total** | **65–98h** | |

### A faixa é larga. O que a fecha

| Informação que falta | Fecha qual bloco | Amplitude que elimina |
|---|---|---|
| Swagger da API de CPR (nomes de campo, endpoints, obrigatoriedade real) | 2, 4 | ~6h |
| Existe endpoint REST de domínios, ou é arquivo? | 3 | **~8h. É a maior incerteza única** |
| Lista de valores de `errors[].code` | 4 | ~2h |
| Campo de idempotência tem unicidade garantida? | 6 | ~2h |
| Certificação tem massa de teste de café com safra válida? | 8 | ~6h |
| As CPRs do clube entram no SCR? | 2 | ~4h |

**Ponto médio defensável: 80h.** Se a documentação chegar e as respostas forem favoráveis (domínio por REST, massa de testes pronta, fora do SCR), 65h. Se forem desfavoráveis, 98h.

### Comparação com o plano atual

| | `plano-do-projeto.md` | Este estudo |
|---|---|---|
| Fase 3 | 32–40h | 65–98h |
| Total do projeto | ~332–356h | ~365–414h |

De onde vem a diferença, item por item:

| Trabalho | Estava previsto? |
|---|---|
| mTLS com keystore `.p12` e certificate pinning | Não. O plano fala em "API key" |
| Integração de arquivos de domínio | Não. Nem como possibilidade |
| Job de reconciliação por polling | Não explicitamente. O plano não diz se haveria webhook |
| Consulta antes de reenviar | Não. O caminho 1 era "reenvia o mesmo payload sem tocar em nada" |
| Ciclo de certificação com a B3 | Parcialmente. "Sem gate externo" subestima o ida e volta com o SAT |

O escopo que apareceu tem a mesma natureza do que já aconteceu entre o dossiê original e a revisão 2. **Levar ao cliente antes da proposta**, junto com a informação de que a faixa fecha assim que o pacote de acesso chegar.

---

## 9. O que preciso pedir ao escritório sócio

Em ordem de urgência. Os quatro primeiros destravam trabalho imediatamente.

| # | Item | Por quê | O que trava sem isso |
|---|---|---|---|
| 1 | **Pacote de acesso de certificação** (`.zip` com `.cer`, `.crt`, `.csr`, `.key`, `.p12` + arquivo-texto com `client_id`, `client_secret` e senha do `.p12`) | É o que a B3 envia. Não é uma API key | Blocos 1, 8. Nada de integração real |
| 2 | **Documentação técnica da API de CPR** (Swagger ou manual do participante, versão 2.5.3 ou 1.3.6 do catálogo Balcão) | Nomes de campo, endpoints, obrigatoriedade e códigos de erro de negócio | Blocos 2, 4, 6. A faixa não fecha |
| 3 | **Códigos de conta Cetip do escritório**: registrador, custodiante, favorecido, agente de pagamento | Vão no payload de todo registro | Bloco 7 |
| 4 | **Arquivos de domínio vigentes** (`AAAAMMDD_Cestas_Produtos` e `AAAAMMDD_Cadastro_Curvas_Moedas_Feeder_Dominios`) ou a informação de que a API expõe isso por endpoint | Define produto, classe/tipo, safra, unidade de medida, acondicionamento e finalidade | Bloco 3. Sem isso o formulário de café não tem domínio |
| 5 | **Resposta: as CPRs do clube entram no SCR?** | Liga ou desliga sete campos obrigatórios e um domínio de 90 valores | Bloco 2 |
| 6 | **Confirmação do papel**: o escritório atua como Agente de Registro? Conta própria, de cliente 1 ou de cliente 2? | Muda quem comanda baixa e retificação, conforme o Manual de Normas art. 21 | Regras de negócio (Frente 4) |
| 7 | **Acordo escrito de uso da credencial**: responsabilidade, rotação, procedimento de revogação, e quem recebe o aviso de vencimento do certificado | Já pedido em `entendimento-do-projeto.md`. A norma da B3 confirma que a responsabilidade pela veracidade é do Agente de Registro | Nada tecnicamente. Tudo juridicamente |
| 8 | **Canal de suporte**: o RM do escritório na B3 e acesso ao SAT (`sat@b3.com.br`, (11) 2565-5120, atendimento das 6h de segunda às 6h de sábado) | Dúvida de integração sem canal vira semana perdida | Bloco 8 |
| 9 | **Pacote de acesso de produção**, quando a Fase 3 estiver homologada | Credencial distinta da de certificação | Go-live |

Itens 1 a 4 podem ser pedidos hoje, no mesmo e-mail.

---

## 10. Contradições com os docs existentes

Quatro, todas pequenas e todas com correção proposta. Nenhuma invalida decisão já tomada.

### 1. "API key de homologação" não existe

**Onde:** `entendimento-do-projeto.md` (tabela "O que mudou da revisão 2" e seção Riscos), `plano-do-projeto.md` (Fase 3 e Sequência recomendada, passo 1), `arquitetura-seguranca.md` (tabela de classificação, linha Credencial).

**O que dizem:** "Falta só pedir a API key de homologação."

**O que é:** pacote de acesso com certificado digital mTLS (`.p12` e afins) mais `client_id`, `client_secret` e a senha do `.p12`.

**Por que importa:** muda o que se pede, muda o cofre de segredos (precisa guardar binário, não só string), e acrescenta certificate pinning e gestão de keystore ao escopo. Parte da diferença de estimativa vem daí.

**Correção sugerida na rev. 4:** trocar "API key de homologação" por "pacote de acesso de certificação (certificado mTLS + client_id/secret)" nos três documentos.

### 2. O caminho 1 (retry) precisa de um passo a mais

**Onde:** `maquina-de-estados.md`, seção "Os quatro caminhos de resolução", item 1.

**O que diz:** "Falha transitória: timeout, instabilidade, erro 5xx. Reenvia o mesmo payload sem tocar em nada."

**O problema:** timeout e 5xx são respostas ambíguas. Não se sabe se a B3 processou. Sem chave de idempotência documentada, reenviar cego pode duplicar ou gerar 422 de duplicidade contra a base interregistradoras.

**Correção sugerida:** o caminho 1 vira consulta e depois, se não achou, reenvio. Diagrama na seção 5 deste documento.

### 3. A credencial B3 não é um valor só

**Onde:** `arquitetura-seguranca.md`, seção 6 "Credencial da B3 como ativo de terceiro".

**O que diz:** "Identidade do participante B3 é configuração, não constante."

**Está certo.** O que falta é o tamanho: são **nove** valores por ambiente, um deles binário. A seção 7 deste documento traz a lista.

**Correção sugerida:** substituir a linha pela lista de nove itens, e registrar que o cofre precisa suportar segredo binário.

### 4. "Sem gate externo" na Fase 3

**Onde:** `plano-do-projeto.md`, Fase 3.

**O que diz:** "Sem gate externo: falta apenas solicitar a API key de homologação."

**O que muda:** a homologação de acesso está aprovada, o que é a parte difícil. Mas o ciclo de certificação técnica com a B3 (conectividade, massa de testes, registro ponta a ponta, ida e volta com o SAT) é dependência de terceiro com tempo de resposta que não controlamos. O bloco 8 da estimativa reflete isso com 8 a 14h e é o menos previsível dos nove.

**Correção sugerida:** manter "sem gate externo" para o acesso e acrescentar que o ciclo de certificação técnica tem prazo dependente da B3.

---

## Anexo — fontes, com data de acesso

Todas acessadas em 12/09/2026.

| Fonte | URL |
|---|---|
| Portal B3 for Developers, catálogo de APIs | https://developers.b3.com.br/apis |
| Catálogo Balcão (APIs de CPR: v2.5.3-rc41, v1.3.6-rc13, CprPublicity v2.0.0-rc2) | https://developers.b3.com.br/apis/api-balcao |
| Autenticação Client Credentials Balcão | https://developers.b3.com.br/index.php?id=29&option=com_content&view=article |
| FAQ B3 for Developers | https://developers.b3.com.br/faq |
| Segurança das APIs B3 | https://developers.b3.com.br/seguranca |
| APIs B3 Considerações Gerais v1.0 (subset HTTP, BusinessStatus) | https://www.b3.com.br/data/files/2B/41/CC/5D/10F42610D290A226790D8AA8/APIs-B3-Visao-Geral-versao-1.0.pdf |
| Layout em Implementação CPR 2.0, fev/2021, comunicado 044/2020-VPC | https://www.b3.com.br/data/files/47/F4/77/28/C0526710DDCBB167AC094EA8/Layout%20em%20Implementacao%20-%20CPR%202.0_v4.pdf |
| Manual API Gravame v1.2 (OAuth2, mTLS, envelope de erro, selfNumber) | https://clientes.b3.com.br/c/document_library/get_file?groupId=20119&uuid=5b28dc9d-7bf2-7d66-864d-5bb3a2efc837 |
| Catálogo APIs iMercado Balcão v1.01 (códigos HTTP, modelo de difusão) | https://www.b3.com.br/data/files/63/D1/10/34/DD9FE710638D2FE7AC094EA8/Catalogo_APIs_iMercado_AcompanhamentoeCaracteristicas_v1.01.pdf |
| Manual de Normas de CDA, WA e CPR, vigente desde 05/12/2022 | https://www.b3.com.br/lumis/portal/file/fileDownload.jsp?fileId=8AE490CA824456A301825A0EA0AD6677 |
| Manual Técnico APIs Área Logada da B3, 31/03/2022 (outro produto, usado só como referência de modelo de acesso) | https://www.b3.com.br/data/files/60/72/19/05/45CDF7104532BBF7AC094EA8/Manual%20Tecnico%20-%20APIs%20vf.pdf |
| Novo sistema de registro da CPR (três canais: tela, arquivo, API) | https://clientes.b3.com.br/w/novo-sistema-de-registro-da-cedula-do-produto-rural-cpr- |
| Interoperabilidade CPR (chave de unicidade, Resolução BCB 304) | https://clientes.b3.com.br/w/interoperabilidade-cpr |
| CPR, consulta de exposição do emitente via API | https://clientes.b3.com.br/w/cpr-consulta-de-exposicao-do-emitente-via-api |
| Aditamento de CPR (distinção aditamento vs. correção) | https://clientes.b3.com.br/w/aditamento-de-cedula-de-produto-rural-cpr- |
| Lei 8.929/1994, art. 3º (requisitos da CPR) | https://www.normaslegais.com.br/legislacao/lei-8929-1994.htm |
| Lei 8.929/1994, art. 12 (prazo de 30 dias úteis, redação da Lei 14.421/2022) | https://modeloinicial.com.br/lei/L-8929-1994/lei-8929/art-12 |

---

## Nota de conferência (sessão de consolidação, 12/09/2026)

A seção 2 cita a Lei 8.929/1994, art. 3º, com base em `normaslegais.com.br`. **Essa fonte serve o texto original de 1994**, sem as alterações da Lei 13.986/2020 e da Lei 14.421/2022. Conferido em 12/09/2026: a página não contém o § 4º sobre assinatura eletrônica nem o prazo de 30 dias úteis, e apresenta o art. 12 na redação antiga, de 3 dias úteis.

O conteúdo citado (denominação, data de entrega, credor, cláusula à ordem, promessa de entrega, especificações, local, garantias, data e lugar da emissão, assinatura do emitente) sobrevive nas duas redações. **O que falta é o que foi acrescentado depois**, e que importa para este projeto:

- `art. 3º, VIII` na redação da Lei 13.986/2020 acrescenta que a assinatura "poderá ser feita de forma eletrônica".
- `art. 12` na redação da Lei 14.421/2022 estabelece 30 dias úteis entre emissão e registro, para títulos emitidos a partir de 11/08/2022. Esse prazo não está em `maquina-de-estados.md` e precisa entrar. Ver `estudo-assinatura-panorama.md`, seção 8, item 3.

**Trocar a fonte pelo texto consolidado antes de usar este documento em proposta.**
