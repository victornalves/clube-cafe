# Estudo da API Lacuna Software — Assinatura ICP-Brasil

**Frente 2** · 12/09/2026 · complementa `estudo-assinatura-panorama.md`, `plano-do-projeto.md` (rev. 2) e `frentes-de-trabalho.md`

---

## O que este documento responde

O catálogo real da Lacuna e qual combinação mínima de produtos este projeto precisa contratar; como o Web PKI funciona em 2026, em quais navegadores e sistemas; como a Lacuna assina com certificado em nuvem e se dá para manter o usuário na nossa tela; o fluxo de integração passo a passo nos dois cenários; webhooks, sandbox, armazenamento e manifesto; o preço publicado, que existe; e a estimativa fechada da Fase 2, com número separado para nuvem e para token físico.

Avalia apenas a Lacuna. A Clicksign é objeto de outro documento.

## O que ele não responde, e por quê

**Preço do PKI Express e do PKI SDK.** A Lacuna publica tabela para a modalidade em nuvem e para as licenças de servidor do PKI Suite, para o Signer e para o Amplia. Não publica valor unitário do PKI Express nem do PKI SDK. A própria documentação do PKI Express diz "Para usar o PKI Express, você precisará de uma licença. Por favor fale conosco" (https://docs.lacunasoftware.com/pt-br/articles/pki-express, acesso 12/09/2026).

**O que conta como uma "transação".** A tabela de preços cobra por transação e a palavra não é definida em nenhuma página pública. Se uma assinatura consumir duas transações (preparar e completar), a conta de opex da seção 11 muda de faixa. Isso está modelado como sensibilidade, não estimado.

**Política de reentrega de webhook.** Nem o Rest PKI Core nem o Signer documentam retry, backoff ou fila de entregas. A documentação descreve como configurar e como autenticar, e para aí.

**Retenção do arquivo no Rest PKI Core.** O modelo `DocumentModel` tem o campo `availableUntil`, descrito como "Date and time until which the document will be available for download". O valor padrão não está publicado.

**Credenciais de dois dos cinco PSCs.** A Lacuna oferece página própria de cadastro de aplicação, mas ela é "disponível apenas para BirdID, SafeID e VIDaaS" (https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/cloud-certificates/brazil-trust-services, acesso 12/09/2026). NeoID e RemoteID exigem cadastro direto no provedor.

---

## 1. O catálogo, e o que precisamos dele

A Lacuna tem treze produtos na documentação. Nove não têm relação com este projeto.

| Produto | O que é | Onde roda |
|---|---|---|
| **Web PKI** | Extensão de navegador mais aplicativo nativo, com biblioteca JS, que dá à página acesso aos certificados do usuário | Navegador e máquina do usuário |
| **Rest PKI** | Serviço em nuvem de assinatura, validação e carimbo de tempo, consumido por client libs em 6 linguagens | Nuvem da Lacuna (ou on premises) |
| **Rest PKI Core** | Reescrita do Rest PKI, com Linux, Docker, PostgreSQL, sessões de assinatura, biometria e webhook | Nuvem da Lacuna (`core.pki.rest`) ou on premises |
| **PKI Express** | Binário instalável que assina no nosso servidor, chamado por linha de comando a partir de PHP, Java, Python, Node.js ou Ruby | Nosso servidor, Windows ou Linux |
| **PKI SDK** | Biblioteca .NET de criptografia, assinatura e validação | Nosso servidor, .NET |
| **Signer** (`dropsigner.com`) | Plataforma pronta de assinatura: fluxo, ordem, convite por e-mail, lembrete, widget embutido, webhook | Nuvem da Lacuna ou instância nossa |
| Amplia / Amplia Reg | Plataforma para ser Autoridade Certificadora | Fora de escopo |
| PSC | Prestador de Serviço de Confiança, guarda certificado em nuvem sob DOC-ICP-17.01 | Fora de escopo |
| TSA | Servidor de carimbo de tempo RFC 3161 próprio | Fora de escopo |
| Bulk Signer, Scanner, Digiploma, GrantID | Assinatura em massa, digitalização, diploma digital, identidade OpenID | Fora de escopo |

Fonte: índice da documentação e https://docs.lacunasoftware.com/pt-br/articles/pki-guide (acesso 12/09/2026).

### A combinação mínima

| Produto | Para que serve neste projeto | Onde roda | Obrigatório? |
|---|---|---|---|
| **Rest PKI Core, SaaS** | Motor da assinatura. Recebe o PDF, monta o PAdES, pede o carimbo de tempo, devolve o assinado, dispara o webhook, guarda a chave de validação | Nuvem da Lacuna | **Sim.** É a peça que não dá para escrever |
| **Web PKI** | Ler o certificado A1 ou A3 do usuário e devolver a assinatura do hash sem sair da nossa página | Navegador do usuário | **Sim no cenário token.** Não no cenário nuvem |
| **PKI Express** ou **PKI SDK** | Só se quisermos o fluxo de certificado em nuvem embutido na nossa tela, em vez da página hospedada pela Lacuna. É quem fala com BirdID, NeoID, RemoteID, SafeID e VIDaaS | Nosso servidor | **Opcional.** Compra a tela, custa licença e horas |
| Rest PKI clássico | Alternativa ao Core. Mais maduro, sem sessões de assinatura e sem webhook | Nuvem da Lacuna | Não |
| **Signer** | Substitui tudo acima e ainda entrega convite, ordem, lembrete e painel. Custa R$ 1.750,00/mês | Nuvem da Lacuna | Não, pelo preço. Ver seção 9 |

**A conta é Rest PKI Core mais Web PKI.** Os outros são alavancas: PKI Express compra a tela no cenário nuvem, Signer compra o fluxo inteiro por seis vezes o orçamento de opex.

---

## 2. Web PKI em 2026

É extensão de navegador **e** aplicativo nativo. As duas coisas, sempre.

A página de segurança do produto descreve a arquitetura sem rodeio: os componentes "Web Extension" são submetidos às lojas oficiais de cada navegador e assinados digitalmente por elas; os componentes "Native App" são baixados de um domínio centralizado, assinados com CodeSign EV e carimbo DigiCert de 10 anos, e "não necessitam de privilégios de administrador para sua execução" (https://docs.lacunasoftware.com/pt-br/articles/web-pki/security, acesso 12/09/2026). O Native App conversa com o token pelo repositório padrão do sistema operacional, e o PIN não trafega por ele.

### Navegadores e sistemas

| Navegador | Versão mínima | Sistemas |
|---|---|---|
| Chrome | 44+ | Windows, Linux, Mac |
| Firefox | 50+ | Windows, Linux, Mac |
| Internet Explorer | 9+ | Windows |
| Microsoft Edge | 42+ | Windows |

Sistemas: Windows 7 SP2 ou superior, Linux baseado em Debian, RedHat e Slackware, Mac OS X 10.12+ (https://docs.lacunasoftware.com/pt-br/articles/web-pki/browser-support, acesso 12/09/2026).

**O panorama afirma suporte a Windows, Linux e macOS. Confirmado, com dois asteriscos.**

Asterisco 1: **não há Safari.** A página de segurança lista "Safari App Store (em breve)" entre as lojas, e a tabela de navegadores suportados não traz Safari. Um produtor com Mac assina pelo Chrome ou pelo Firefox.

Asterisco 2: assinatura **local** (tudo no frontend, sem backend) só funciona em Windows. Assinatura **remota** (frontend assina o hash, backend monta o documento) funciona em Windows, macOS e Linux, e é a que a própria Lacuna recomenda: "recomendamos escolher a abordagem de assinaturas web remotas na maioria dos casos" (https://docs.lacunasoftware.com/pt-br/articles/pki-guide/web-signatures, acesso 12/09/2026). Nosso desenho usa a remota, então os três sistemas entram.

### O que o usuário instala, e quando

O método `init()` da biblioteca JS verifica três condições: navegador suportado, componentes instalados, componentes atualizados. Se qualquer uma falhar, o usuário é redirecionado para a página de instalação "de uma forma específica tal que, quando a instalação for concluída, ele será automaticamente redirecionado para a página original" (https://docs.lacunasoftware.com/pt-br/articles/web-pki/customizing-not-installed, acesso 12/09/2026).

A página de instalação é `https://get.webpkiplugin.com`, única e centralizada. Ela detecta o navegador por JavaScript e redireciona para `/Setup?browser=...&returnUrl=...` (verificado em 12/09/2026). O usuário instala a extensão da loja e executa o instalador nativo.

Uma vez instalado, o componente **se atualiza sozinho**: "O Web PKI é atualizado automaticamente nos computadores dos usuários" (https://docs.lacunasoftware.com/pt-br/articles/web-pki/update, acesso 12/09/2026). Quem atualiza manualmente é a biblioteca JS na nossa aplicação, hoje na versão 2.16.5, disponível por CDN com hash SRI ou pelo pacote npm `web-pki`.

**Quantos cliques até a primeira assinatura: a Lacuna não publica esse número.** O que está documentado é a sequência: nossa página chama `init()`, o usuário é mandado para `get.webpkiplugin.com`, instala dois artefatos (extensão da loja e executável nativo) e volta sozinho para a nossa página. Da segunda vez em diante, zero instalação.

---

## 3. Certificado em nuvem

Sim, e por três produtos diferentes.

Os cinco serviços vêm pré-configurados, com os nomes que `entendimento-do-projeto.md` pediu mais o RemoteID: **BirdID (Soluti/VaultID), NeoID (Serpro), RemoteID (Certisign), SafeID (Safeweb) e VIDaaS (Valid)**. Configuram-se por `clientId` e `clientSecret`; serviços fora da lista pedem também `endpoint` (https://docs.lacunasoftware.com/pt-br/articles/pki-express/config/trust-services e https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/cloud-certificates/brazil-trust-services, acesso 12/09/2026).

No PKI Express, a configuração é por linha de comando:

```
pkie config --set trustServices:<serviço>:clientId=<valor>
pkie config --set trustServices:<serviço>:clientSecret=<valor>
```

### Os dois fluxos, e qual mantém o usuário na nossa tela

| | **Fluxo PWD** | **Fluxo OAuth** |
|---|---|---|
| Passos | Discover, Authorize | Discover, Redirect, Complete |
| Como o usuário autoriza | Digita um código de autorização na **nossa** tela | É levado ao ambiente do PSC, autoriza lá, volta com `code` e `state` |
| Sai da nossa tela? | **Não** | Sim, por um redirect |
| Descoberta | `DiscoverByCpfAsync(cpf)` ou `DiscoverByCnpjAsync` varre todos os provedores configurados e devolve os que têm certificado daquele CPF ou CNPJ | `DiscoverByCpfAndStartAuthAsync(cpf, redirectUrl, tipoDeSessão, customState)` |

Fonte: https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/cloud-certificates/brazil-trust-services (acesso 12/09/2026).

**O fluxo PWD é o que entrega a promessa de assinar sem sair da plataforma.** Ele exige PKI Express ou PKI SDK rodando no nosso servidor. A descoberta por CPF ou CNPJ também resolve, de graça, a pergunta 2 de `entendimento-do-projeto.md` sobre certificado de PJ: `DiscoverByCnpjAsync` existe e é simétrica.

Os tipos de sessão são quatro: `SingleSignature` (um hash), `MultiSignature` (vários hashes, uma autorização), `SignatureSession` (várias assinaturas dentro do prazo, até revogação) e `AuthenticationSession` (só autentica). O `SignatureSession` é o que `estudo-assinatura-panorama.md` identificou como útil para o caminho 3 da `maquina-de-estados.md`, reassinatura sem trazer o produtor de volta.

Alternativa sem PKI Express: a **sessão de assinatura do Rest PKI Core** também assina com certificado em nuvem, com a vantagem de não instalar nada no nosso servidor e o custo de usar uma página hospedada pela Lacuna. A documentação de requisitos de certificado confirma o suporte ao mencionar que o requisito `Cpf` "permite que o sistema não precise solicitar ao usuário que digite seu CPF para consultar os certificados em nuvem disponíveis" (https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/signature-sessions/certificate-requirements, acesso 12/09/2026).

---

## 4. Mapa do fluxo de integração

### Cenário token físico, embutido na nossa tela

| # | Onde | O que acontece |
|---|---|---|
| 1 | Nosso backend | Gera o PDF do contrato e guarda no nosso storage |
| 2 | Nossa página | `new LacunaWebPKI(licença)` e `pki.init({ready, notInstalled})`. Se não instalado, `redirectToInstallPage()` |
| 3 | Nossa página | `listCertificates()`, filtra ICP-Brasil, usuário escolhe, guardamos o `thumbprint` |
| 4 | Nossa página | `readCertificate(thumbprint)` devolve o certificado codificado |
| 5 | Nosso backend | `POST {endpoint}/api/signature` com `file` (FileReferenceModel), `certificate` (CertificateReferenceModel), `signatureType: "Pdf"` e `pdfSignatureOptions`. A resposta traz `toSignHash` e `state` |
| 6 | Nossa página | `signHash({thumbprint, hash, digestAlgorithm})`. O PIN é pedido pelo diálogo do componente, nunca pela nossa página |
| 7 | Nosso backend | `POST {endpoint}/api/signature/completion` com `{state, signature}`. A resposta é o `DocumentModel`, com `signedFile`, `key` e `formattedKey` |
| 8 | Nosso backend | Baixa o `signedFile` pela URL temporária e grava no nosso storage. Registra o evento na tabela append-only |

Endpoints verificados no Swagger público do Rest PKI Core (https://core.pki.rest/swagger/api/swagger.json, acesso 12/09/2026). O método `signWithRestPki({thumbprint, token})` do Web PKI encurta os passos 5 a 7 quando se usa o Rest PKI clássico (https://github.com/LacunaSoftware/docs/blob/master/typedocs/lacuna-web-pki.d.ts, acesso 12/09/2026).

**Nenhuma tela de terceiro. Nenhum redirect. Um componente instalado na máquina do usuário.**

### Cenário nuvem, caminho curto, com sessão de assinatura

| # | Onde | O que acontece |
|---|---|---|
| 1 | Nosso backend | `POST {endpoint}/api/signature-sessions` com os documentos pré-definidos, `certificateRequirements` (`Cpf` do signatário) e `callbackArgument` com o id do nosso registro. Sem `returnUrl` e com `enableBackgroundProcessing: true` se formos pelo webhook |
| 2 | Nossa página | Abre o `redirectUrl` em nova aba com `target="_blank"`. O Rest PKI Core fecha a aba ao final |
| 3 | Página da Lacuna | Usuário escolhe o PSC, autoriza no app do celular, assina |
| 4 | Nosso backend | Recebe `POST` do webhook `DocumentSignatureCompleted` com `document.signedFile.location` |
| 5 | Nosso backend | Baixa, grava no nosso storage, avança a máquina de estados |

Se optarmos pelo `returnUrl` em vez do webhook, o passo 4 vira um handler que lê `?signatureSessionId=` e chama `GET /api/signature-sessions/{id}`, checando `status` contra `Completed`, `UserCancelled`, `Expired`, `Processing`, `ProcessingError` e `Pending`.

**Custo desse caminho: o usuário sai da nossa tela.** Ganha-se o fluxo de escolha de PSC pronto.

### Cenário nuvem, caminho longo, embutido

| # | Onde | O que acontece |
|---|---|---|
| 1 | Nosso backend | `DiscoverByCpfAsync(cpf)` no PKI Express. Devolve a lista de PSCs que têm certificado daquele CPF |
| 2 | Nossa página | Mostra os PSCs encontrados. Usuário escolhe um e digita o código de autorização do app |
| 3 | Nosso backend | `PasswordAuthorizeAsync(serviço, cpf, código, SignatureSession)` e depois `GetCertificatesWithKeyAsync()` |
| 4 | Nosso backend | Assina PAdES com a chave remota, no nosso servidor |
| 5 | Nosso backend | Grava no nosso storage |

**Nenhum redirect, nenhuma instalação no navegador.** Custo: PKI Express instalado, licenciado e mantido, mais a tela de escolha de PSC escrita por nós.

---

## 5. Webhooks

Existem, e a resposta muda conforme o produto.

### Rest PKI Core

Um evento só: `DocumentSignatureCompleted`, "disparado quando um documento é assinado e tem seu processamento concluído". A notificação é um `POST` HTTP com um `WebhookEventModel`, que carrega `type` e o `document` completo, incluindo `id`, `key`, `formattedKey`, `originalFile`, `signedFile`, `status` e `signatureType`.

Autenticação da origem, à escolha na configuração: **Basic** (usuário e senha no header `Authentication`), **Bearer** (token no header `Authentication`) ou **API Key** (chave no header `X-Api-Key`). Fonte: https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/webhooks (acesso 12/09/2026).

Não há assinatura HMAC do corpo. A autenticação é um segredo compartilhado no header, o que significa que o endpoint tem que estar sob TLS e o segredo no cofre, junto com os nove valores da B3 previstos em `estudo-api-b3.md`.

**Reentrega não é documentada.** Tratamos como não existente e escrevemos um job de varredura chamando `GET /api/signature-sessions/{id}`, que é o mesmo padrão de reconciliação que `estudo-api-b3.md` já previu para a B3. Existe ainda `GET /api/signature-sessions/{id}/when-completed`, que o Swagger expõe e a documentação em prosa não descreve.

### Signer

Nove eventos, verificados no Swagger público do `dropsigner.com` (https://www.dropsigner.com/swagger/api/swagger.json, acesso 12/09/2026), enum `WebhookTypes`:

`DocumentConcluded`, `DocumentSigned`, `DocumentApproved`, `DocumentRefused`, `DocumentCanceled`, `DocumentExpired`, `DocumentsCreated`, `DocumentDeleted`, `InvoiceClosed`.

Cada um tem modelo próprio. O `DocumentSignedModel` traz a assinatura; o `DocumentRefusedModel` traz a recusa com motivo; o `DocumentCanceledModel` traz quem cancelou e por quê. A URL se registra na tela da Organização, opção Integração, e "é possível adicionar múltiplos webhooks por organização". Não há endpoint de API para configurar webhook, e nem autenticação de origem nem reentrega estão documentadas.

O guia de integração é explícito sobre o que fazer com isso: "Sempre verifique no backend se o documento foi de fato concluído, dado que os callbacks podem ser acionados por outros arquivos javascript" (https://docs.lacunasoftware.com/pt-br/articles/signer/integration-guide, acesso 12/09/2026). O aviso é sobre o widget, e vale igual para o webhook.

---

## 6. Sandbox

Três coisas diferentes, e nenhuma delas é um ambiente de homologação nomeado.

| Item | Existe? | Gratuito? |
|---|---|---|
| **Web PKI em localhost** | Sim. "A licença do Web PKI não é necessária para testar o Web PKI em uma aplicação web rodando no localhost (qualquer porta)" | Sim |
| **Web PKI em IP privado** | Sim. As licenças são emitidas com `homologDomains` contendo `ip4:10.0.0.0/8`, `ip4:127.0.0.0/8`, `ip4:172.16.0.0/12` e `ip4:192.168.0.0/16`, mais os subdomínios de homologação contratados | Sim, dentro da licença |
| **Certificados de teste ICP-Brasil** | Sim. Zip com quatro `.pfx`, senha `1234`: três pessoas físicas com CPF e uma pessoa jurídica com CNPJ e representante legal | Sim |
| **Conta de teste do Rest PKI em nuvem** | Sim: "150 transações grátis por 3 meses" e "Início imediato sem burocracia" | Sim, por 3 meses |
| **Parâmetros do Rest PKI Core SaaS** | "solicite seus parâmetros ao nosso suporte ao desenvolvedor". Não é autosserviço | Não publicado |

Fontes: https://docs.lacunasoftware.com/pt-br/articles/web-pki/licensing, https://docs.lacunasoftware.com/pt-br/articles/pki-guide/test-certs, https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/get-started e https://www.lacunasoftware.com/pt-br/pricing/ (acesso 12/09/2026).

**Dá para testar sem certificado real, e essa é a resposta que faltava no panorama.** Os certificados de teste "mimetizam" certificado ICP-Brasil de pessoa física e jurídica, e o contexto de segurança que os aceita tem id fixo e publicado: `803517ad-3bbc-4169-b085-60053a8f6dbf`. A própria Lacuna manda remover a confiança nessa ICP em produção, e recomenda compilação condicional para que ela valha só em modo debug. Vamos seguir isso à risca: o id do contexto de segurança entra na mesma configuração por ambiente que a identidade do participante B3 já ocupa.

Para certificado em nuvem há ainda um usuário de teste do BirdID em homologação, com CPF publicado e pareamento por QR Code, usado no exemplo online do widget do Signer.

**O que continua não sendo respondido: se o sandbox reproduz o fluxo de PSC de verdade.** O exemplo do BirdID sugere que sim para um dos cinco. Para os outros quatro, só usando.

---

## 7. Quem guarda o documento

Depende do produto. O panorama diz "Nós. Integralmente". Isso é verdade para uma das três rotas.

| Rota | O que a Lacuna recebe | O que a Lacuna guarda |
|---|---|---|
| **Rest PKI clássico, assinatura web remota** | O hash do documento, o certificado e o IP | Nada do documento. A política de privacidade do Rest PKI lista exatamente três dados de usuário final: "Certificado digital; Endereço IP; Hash de documento" |
| **Rest PKI Core, sessão de assinatura** | O arquivo inteiro, por upload ou por URL | O original e o assinado, com `availableUntil` e `key` de validação |
| **Signer** | O arquivo inteiro | Tudo, com pastas, organização e cobrança por storage (`totalStorageUsed` no `InvoiceClosedModel`) |

Fonte: https://docs.lacunasoftware.com/pt-br/articles/rest-pki/privacy-policy (acesso 12/09/2026) e os dois Swaggers citados.

Três consequências para `arquitetura-seguranca.md`:

1. **A rota que não expõe o documento é a do Rest PKI clássico com assinatura web remota.** Trafega da ordem de 3KB por assinatura, segundo a própria Lacuna.
2. **Se formos de sessão de assinatura do Rest PKI Core, o PDF da CPR sai da nossa infraestrutura.** Termos comerciais, partes e volume vão junto. Isso contraria o adversário que `entendimento-do-projeto.md` nomeia como mais provável, e precisa de decisão explícita, não de default.
3. A URL de download que a API devolve é temporária, "expiring after a short period of time (normally 1 hour), so DO NOT STORE IT". Ela nunca vai para o banco nem para o log. Baixamos e guardamos o binário.

---

## 8. Manifesto, padrões e trilha de auditoria

O ponto forte deles, como o panorama diz. Com uma lacuna concreta.

### Padrões

PAdES para PDF, CAdES/CMS para qualquer arquivo e XAdES/XmlDSig para XML, nos três produtos de assinatura. O PKI SDK segue a especificação ETSI 102778-x no PAdES. O Rest PKI Core expõe endpoints separados para `PadesSignatures`, `CadesSignatures` e `XmlSignatures`, nas versões v1, v2 e v3.

### Políticas ICP-Brasil

O PKI SDK traz objetos de política já configurados segundo o DOC-ICP-15.03, acessíveis por classe. Estão documentadas nominalmente:

- **AD-RT** (referência de tempo, exige carimbo no momento da assinatura): `BrazilCadesPolicySpec.GetAdrTempoV21()`
- **AD-RC** (referência completa), com mapeador que escolhe entre as versões **1.0, 1.1, 2.0 e 2.1** pelo certificado do signatário: `BrazilCadesPolicyMappers.GetAdrCompleta()`

**A política PAdES ICP-Brasil não existe ainda.** A documentação é literal: ao lado de `BrazilCadesPolicySpec` para CAdES, está escrito "Pades. (Em desenvolvimento e aguardando decisão do Comitê Gestor da ICP-Brasil)" (https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/signatures/policies/pki-brazil, acesso 12/09/2026).

Consequência para a CPR: assinar o PDF com política PAdES genérica mais carimbo de tempo é o que dá para fazer hoje em PAdES. Quem quiser política ICP-Brasil explícita, com OID no atributo assinado, assina em CAdES destacado ao lado do PDF. Isso é uma pergunta para o escritório sócio, não para o fornecedor.

### Carimbo do tempo e longo prazo

O carimbo é serviço contratado, e a Lacuna vende o dela. Requisitos publicados para qualquer provedor: TSP sobre HTTP ou HTTPS conforme RFC 3161, com autenticação por HTTP basic, mTLS ou OAuth Bearer Token. A URL da carimbadora do Rest PKI em nuvem é publicada: `https://pki.rest/tsp/a402df41-8559-47b2-a05c-be555bf66310` (https://docs.lacunasoftware.com/pt-br/articles/rest-pki/on-premises/configure-timestamping, acesso 12/09/2026).

O que prova a assinatura anos depois está no endpoint `POST /api/signature/archival-extension` do Rest PKI Core, descrito no Swagger como "Request for extending an archive timestamp (AD-RA)". Ele recebe `minActiveTimestampValidityDays`, devolve `extended`, `activeTimestampBefore`, `activeTimestampAfter`, `daysUntilExpiration` e `recommendedExtensionDate`, "calculated as (ValidUntil - MinDaysToExtend)".

**Isso é a peça que nenhum concorrente da lista publica.** Uma CPR de café vive anos. O carimbo de arquivamento vence junto com o certificado da carimbadora, e alguém precisa reestampar antes disso. A Lacuna entrega o endpoint e a data recomendada; a rotina que chama esse endpoint é nossa, e **não está em nenhuma estimativa dos docs atuais**. Entra na Fase 2 como bloco 8.

### Manifesto e validação

Todo documento assinado no Rest PKI Core recebe uma `key` e uma `formattedKey` de 16 caracteres em quatro grupos (exemplo da documentação: `FUFY-Q7SL-6XKM-BW9A`), "usada para consultar este documento na página de validação". A consulta é por `GET /api/documents/keys/{key}`.

O Signer vai além e entrega cinco versões para download: Arquivo Assinado, **Versão para impressão**, Etiquetas de assinatura, Marcas de Assinatura e Arquivo Original. A versão para impressão é "seu documento pronto para impressão com o manifesto de assinaturas e o código de validação". A validação por chave devolve, por signatário: `subjectName`, `emailAddress`, `issuerName`, `identifier` (CPF), `companyIdentifier` (CNPJ), `isElectronic`, `signingTime`, `certificateThumbprint` e `validationResults.isValid`.

O validador reconhece 49 tipos de falha (`ValidationItemTypes` no Swagger), entre eles `InvalidArchiveTimestamp`, `RevocationDataIssuedBeforeGracePeriod`, `SignaturePolicyMismatch` e `SignatureVulnerableToSignerSubstitution`. Para a tela de auditoria do backoffice, prevista em `plano-do-projeto.md`, isso é insumo direto.

---

## 9. Preço e licenciamento

**O panorama está desatualizado neste ponto. A Lacuna publica tabela.** Ela está em `https://www.lacunasoftware.com/pt-br/pricing/`, renderizada por JavaScript, o que explica por que uma leitura por fetch não a encontra. Os valores abaixo foram lidos do arquivo de tradução que a própria página carrega (`https://www.lacunasoftware.com/assets/i18n/pt.json`) e da lógica do simulador no bundle da aplicação (`main-VBIYTGQZ.js`), ambos públicos e sem autenticação, acesso 12/09/2026.

### Modalidade em nuvem, pagamento por transação

| Faixa | Preço por transação | Preço por carimbo de tempo |
|---|---|---|
| 1 a 400 | R$ 0,50 | R$ 0,15 |
| 401 a 500 | R$ 0,40 | R$ 0,12 |
| 501 a 5.000 | R$ 0,30 | R$ 0,09 |
| 5.001 a 30.000 | R$ 0,20 | R$ 0,07 |
| 30.001 a 40.000 | R$ 0,05 | R$ 0,05 |

Condições publicadas: **"Consumo mínimo mensal de R$ 200 até 400 transações"**, **"150 transações grátis por 3 meses"**, "Início imediato sem burocracia", "Hospedagem no servidor da Lacuna".

### Modalidade servidor, pagamento por licença

| Versão | O que inclui | Preço |
|---|---|---|
| **Full, perpétua** | Licença perpétua, 3 subdomínios ou hostnames, 3 servidores, 12 meses de atualizações, 8h de suporte a dev/infra | **R$ 54.000,00** |
| **Anual** | Licença de 1 ano, 2 subdomínios ou hostnames, 2 servidores, atualização de versão durante o contrato, 4h de suporte | **R$ 23.000,00** |
| Subdomínio ou hostname extra, versão Full | | R$ 8.000,00 |
| Subdomínio ou hostname extra, versão PKI | | R$ 3.000,00 |
| Extensão da garantia | | 1,5% ao mês, contrato anual |
| Pacote extra de 4h de suporte a dev/infra | | R$ 800,00 |

### Outros produtos, para referência

| Produto | Preço publicado |
|---|---|
| Signer, nuvem | **R$ 1.750,00/mês**, limite inicial de mil documentos enviados por mês, instância, banco e storage individuais |
| Signer, instância própria | R$ 74.000,00, licença perpétua com 1 ano de atualizações |
| Amplia | R$ 79.000,00, mais R$ 200,00 por AC ativa e R$ 1,00 por certificado ativo/mês |

### A licença do Web PKI, que o panorama listou como incógnita

Ela é por domínio, entregue em dois formatos equivalentes, binário ou JSON, e o JSON traz `allowedDomains`, `homologDomains`, `productLevel` e `expiration`. O preço unitário não é publicado.

**E, na maior parte dos casos, não precisa ser.** A documentação de licenciamento diz: "A licença do Web PKI não é necessária para testar o Web PKI em uma aplicação web rodando no localhost (qualquer porta) **ou ainda quando sendo utilizado em conjunto com o Rest PKI em nuvem (nesse caso, inclusive em produção)**" (https://docs.lacunasoftware.com/pt-br/articles/web-pki/licensing, acesso 12/09/2026).

Como a combinação recomendada na seção 1 é exatamente Rest PKI em nuvem mais Web PKI, **o item 9 da lista de pendências do panorama deixa de ser custo fixo de produção e vira zero**, desde que fiquemos no Rest PKI em nuvem. Confirmar com o comercial se a isenção se estende ao Rest PKI **Core** SaaS, já que a frase diz "Rest PKI".

**Custo mínimo de entrada:** R$ 200,00 por mês. É o consumo mínimo da modalidade em nuvem. Antes disso, três meses com 150 transações grátis.

---

## 10. Estimativa fechada da Fase 2

`plano-do-projeto.md` traz 32 a 40h, com a faixa dependendo de nuvem ou token. `estudo-assinatura-panorama.md` estima 60 a 80h para a Lacuna cobrindo os dois cenários. **Os dois números são baixos.**

Premissa: a Fase 1 já entregou a máquina de estados em duas camadas, a tela de resolução, o storage com URL assinada, a assinatura mockada e a interface de uma porta (`criarSolicitacao`, `obterStatus`, `receberRetorno`). A Fase 2 troca a implementação.

### Cenário nuvem

Desenho: Rest PKI Core SaaS com sessão de assinatura hospedada, fluxo com webhook. Sem Web PKI, sem PKI Express.

| # | Bloco | Horas | O que está dentro |
|---|---|---|---|
| 1 | Conta, chave de API e contexto de segurança | 3–4 | Solicitação dos parâmetros ao suporte, `Endpoint` e `ApiKey` no cofre, `securityContextId` por ambiente, chave sem expiração |
| 2 | Adaptador da interface de uma porta | 6–8 | `criarSolicitacao` sobre `POST /api/signature-sessions`, `obterStatus` sobre `GET /api/signature-sessions/{id}`, `receberRetorno` sobre o webhook. Mock e real atrás da mesma assinatura de método |
| 3 | Criação da sessão com documentos pré-definidos | 5–7 | `SignatureSessionDocumentData` por parte, `certificateRequirements` com `Cpf` do signatário, `callbackArgument` com o id do registro, `pdfSignatureOptions` com representação visual e `reason`, `disableDownloads` |
| 4 | Tratamento dos seis estados da sessão | 5–7 | `Pending`, `Processing`, `Completed`, `UserCancelled`, `Expired` (4h), `ProcessingError` com o código de 6 caracteres para suporte. Mapeamento para os estados em português da `maquina-de-estados.md` |
| 5 | Webhook e reconciliação | 8–10 | Endpoint autenticado por `X-Api-Key`, idempotência por `document.id`, job de varredura porque reentrega não é documentada, correlação com o id do registro, trava contra processamento concorrente |
| 6 | Download e guarda do assinado | 4–6 | URL temporária de 1h nunca persistida, download, gravação no nosso storage, hash de integridade, evento append-only |
| 7 | Orquestração de 2 a 3 signatários | 10–14 | Convite, ordem, sessão por parte, expiração, reenvio, reassinatura do caminho 3 da `maquina-de-estados.md`, corretor opcional |
| 8 | Manifesto, chave de validação e carimbo de arquivamento | 6–8 | Guarda de `key` e `formattedKey`, tela de verificação, e a rotina periódica que chama `POST /api/signature/archival-extension` respeitando `recommendedExtensionDate` |
| 9 | Ambiente de teste | 4–6 | ICP de testes da Lacuna por contexto de segurança configurável, os quatro `.pfx`, compilação condicional, credencial de homologação de ao menos um PSC |
| 10 | Erros, observabilidade e testes | 6–8 | Id de correlação por chamada, mascaramento de chave de API em log, testes com os seis estados e com falha de webhook |
| | **Total** | **57–78h** | |

### Cenário token físico

Desenho: Web PKI na nossa página, assinatura remota em duas etapas contra o Rest PKI Core. Sem redirect.

| # | Bloco | Horas | O que está dentro |
|---|---|---|---|
| 1 | Conta, chave de API e licença do Web PKI | 4–6 | O do bloco 1 acima, mais a licença por domínio nos dois formatos, `allowedDomains` de produção e `homologDomains` de staging |
| 2 | Web PKI no navegador | 12–16 | Biblioteca por npm ou CDN com SRI, `init()` na forma extensa com callback `notInstalled`, mensagem antes de `redirectToInstallPage()`, `listCertificates()`, filtro de certificado ICP-Brasil, leitura de CPF e CNPJ, seleção, `readCertificate()` |
| 3 | Assinatura remota em duas etapas | 8–10 | `POST /api/signature` com `FileReferenceModel` e `CertificateReferenceModel`, `signHash()` no navegador, `POST /api/signature/completion` com `state` e `signature`, tratamento dos seis `PrepareSignatureFailures` (`PdfAlreadySigned`, `CorruptedPdf`, `CertificateValidationFailed`, `PasswordProtectedPdf` e os dois de PDF/A) |
| 4 | Adaptador da interface de uma porta | 6–8 | Igual ao bloco 2 do cenário nuvem, sem webhook: aqui a assinatura fecha síncrona |
| 5 | Matriz de navegador e sistema, e a trilha de erro de instalação | 8–12 | Teste em Chrome e Firefox sobre Windows, Linux e macOS; mensagem específica para Safari, que não é suportado; instrução de driver do fabricante do token; token conectado depois da página aberta; certificado vencido; PIN errado; PIN bloqueado |
| 6 | Download e guarda do assinado | 4–6 | Igual ao cenário nuvem |
| 7 | Orquestração de 2 a 3 signatários | 10–14 | Igual ao cenário nuvem |
| 8 | Manifesto, chave de validação e carimbo de arquivamento | 6–8 | Igual ao cenário nuvem |
| 9 | Ambiente de teste | 4–6 | Igual ao cenário nuvem, mais um token físico de verdade para pelo menos um teste de ponta a ponta |
| 10 | Erros, observabilidade e testes | 6–8 | Igual ao cenário nuvem, mais log de versão do componente instalado |
| | **Total** | **68–94h** | |

### Se o cliente responder "os dois"

Os blocos 6 a 10 são compartilhados. Os específicos somam.

| Parte | Horas |
|---|---|
| Compartilhado (blocos 6 a 10) | 30–42 |
| Específico de nuvem (blocos 1 a 5) | 27–36 |
| Específico de token (licença, Web PKI, prepare/complete, matriz de SO) | 29–40 |
| **Total** | **86–118h** |

Some 12 a 18h se o cenário nuvem também tiver que ser embutido, o que exige PKI Express instalado, licenciado e mantido no nosso servidor, mais a tela de escolha de PSC e o fluxo PWD escritos por nós.

### A faixa é larga. O que a fecha

| Informação que falta | Fecha qual bloco | Amplitude que elimina |
|---|---|---|
| A isenção de licença do Web PKI vale para o Rest PKI **Core**? | 1 do token | ~2h, e um custo fixo |
| Uma "transação" é uma assinatura, ou preparar e completar contam duas? | Nenhum bloco. Fecha a opex | Ver seção 11 |
| Reentrega de webhook existe? | 5 do cenário nuvem | **~4h. É o job de varredura inteiro** |
| Valor padrão de `availableUntil` no Rest PKI Core | 6 | ~2h |
| Credencial de homologação de quantos dos cinco PSCs | 9 | ~4h |
| A CPR vai assinada em PAdES ou em CAdES destacado? | 3, 8 | ~6h. Depende do escritório sócio, não da Lacuna |

**Ponto médio defensável: 67h no cenário nuvem, 80h no cenário token, 100h nos dois.**

### Comparação com os docs atuais

| | `plano-do-projeto.md` | `estudo-assinatura-panorama.md` | Este estudo |
|---|---|---|---|
| Fase 2, só nuvem | 32–40h | 32–40h para plataforma pronta | 57–78h |
| Fase 2, só token | 32–40h | 40–50h para plataforma pronta | 68–94h |
| Fase 2, os dois com Lacuna | — | 60–80h | 86–118h |
| Total do projeto, com a Fase 3 de `estudo-api-b3.md` | ~332–356h | — | **~390–472h** |

De onde vem a diferença para o panorama:

| Trabalho | O panorama previa? |
|---|---|
| Rotina de extensão de carimbo de arquivamento (AD-RA) | Não. Nem como possibilidade |
| Job de varredura por falta de reentrega de webhook documentada | Não. O panorama escreveu "Webhook: não se aplica" para a Lacuna |
| Matriz de teste navegador × sistema operacional, com Safari fora | Parcialmente. Cita os três sistemas, não o custo de testá-los |
| Seis estados de sessão e seis falhas de preparação | Não |
| Download por URL temporária de 1h, com guarda separada | Não |

**Alavanca de corte, se necessário:** o Lacuna Signer elimina os blocos 7 e metade do 8 em qualquer cenário, porque entrega fluxo, ordem, convite, lembrete e versão para impressão com manifesto. Economia estimada: 12 a 18h. Custo do corte: R$ 1.750,00/mês de opex e o PDF da CPR hospedado por terceiro. A conta está na seção 11.

---

## 11. Custo real de opex

Premissa: uma CPR com **três partes** (produtor, comprador, corretor opcional), logo três assinaturas por documento. Um carimbo de tempo por assinatura. Uma transação por assinatura.

| Volume | Assinaturas/mês | Transações | Carimbos | Consumo calculado | **Fatura, com mínimo de R$ 200** | Ano |
|---|---|---|---|---|---|---|
| 20 docs/mês | 60 | R$ 30,00 | R$ 9,00 | R$ 39,00 | **R$ 200,00** | R$ 2.400,00 |
| 50 docs/mês | 150 | R$ 75,00 | R$ 22,50 | R$ 97,50 | **R$ 200,00** | R$ 2.400,00 |
| 100 docs/mês | 300 | R$ 150,00 | R$ 45,00 | R$ 195,00 | **R$ 200,00** | R$ 2.400,00 |

**Nos três volumes a conta é a mesma: R$ 200,00 por mês.** O mínimo mensal domina até 100 CPRs com três partes. Só a partir de aproximadamente 103 documentos por mês o consumo passa do piso.

**A opex de R$ 295/mês do dossiê fecha, com R$ 95,00 de folga.** Somando a licença do Web PKI, que é zero na combinação com o Rest PKI em nuvem, a folga não muda.

### Sensibilidade: se uma transação não for uma assinatura

| Se cada assinatura consumir | 20 docs | 50 docs | 100 docs |
|---|---|---|---|
| 1 transação | R$ 200,00 | R$ 200,00 | R$ 200,00 |
| 2 transações (preparar e completar) | R$ 200,00 | R$ 200,00 | **R$ 315,00** |
| 3 transações | R$ 200,00 | R$ 212,50 | **R$ 385,00** |

Na hipótese de duas transações por assinatura, 100 documentos por mês estouram os R$ 295,00. **Perguntar a definição de "transação" ao comercial antes de fechar preço com o cliente.** É a única variável que muda a resposta.

### Custos que não estão nessa conta

| Item | Quanto | De quem |
|---|---|---|
| Certificado em nuvem dos membros | Tabela do SafeID Integração já levantada no panorama: 50/mês grátis, 100 por R$ 100,00, 500 por R$ 400,00 | Do signatário, salvo se o clube decidir bancar |
| Licença do Web PKI | R$ 0,00 na combinação com Rest PKI em nuvem. Não publicado fora dela | Nosso |
| Licença do PKI Express | Não publicado, exige contato comercial | Nosso, só se formos pelo cenário nuvem embutido |

### Comparação com as duas alternativas de arquitetura

| Desenho | Opex mensal | Opex anual | Fase 2 |
|---|---|---|---|
| **Rest PKI Core nuvem + Web PKI** | R$ 200,00 | R$ 2.400,00 | 57–94h |
| Rest PKI on premises, versão Anual | R$ 0,00 de transação, R$ 23.000,00/ano de licença, mais carimbo de tempo contratado | R$ 23.000,00 + carimbos | Some infraestrutura e operação |
| Lacuna Signer, nuvem | R$ 1.750,00 | R$ 21.000,00 | 45–76h |

Signer custa **5,9 vezes** o orçamento de opex do dossiê para economizar de 12 a 18h de desenvolvimento, uma vez. O payback não existe: a economia de horas vale cerca de R$ 4.500,00 a R$ 5.400,00 na taxa de R$ 300/h, e o primeiro ano de Signer custa R$ 21.000,00.

---

## 12. O que não consegui confirmar

| # | Item | Com quem | Por que trava |
|---|---|---|---|
| 1 | **Definição de "transação"** na tabela de preços | Comercial Lacuna | É a única variável que decide se a opex fecha em R$ 295/mês com 100 docs |
| 2 | **A isenção de licença do Web PKI vale para o Rest PKI Core?** A frase publicada diz "Rest PKI em nuvem" | Comercial Lacuna | É a diferença entre R$ 0,00 e um custo fixo de produção não publicado |
| 3 | **Preço do PKI Express e do PKI SDK** | Comercial Lacuna | Define se o cenário nuvem embutido é viável |
| 4 | **O Rest PKI Core SaaS usa a mesma tabela de preços do PKI Suite em nuvem?** O Core não tem autosserviço: os parâmetros saem do suporte | Suporte ao desenvolvedor da Lacuna | Toda a seção 11 assume que sim |
| 5 | **Reentrega e política de retry de webhook**, nos dois produtos | Suporte técnico | Vale ~4h de job de varredura |
| 6 | **Valor padrão de `availableUntil`** no Rest PKI Core | Suporte técnico | Define a janela para baixar o assinado antes de perdê-lo |
| 7 | **Autenticação de origem do webhook do Signer.** O Rest PKI Core documenta três modos; o Signer não documenta nenhum | Suporte técnico | Só importa se formos de Signer |
| 8 | **Safari em 2026.** A página de segurança diz "em breve" desde pelo menos a versão atual do documento | Suporte técnico | Decide se um membro com Mac precisa instalar outro navegador |
| 9 | **Status da política PAdES ICP-Brasil**, hoje "em desenvolvimento e aguardando decisão do Comitê Gestor" | Comercial Lacuna e ITI | Decide se a CPR vai em PAdES ou em CAdES destacado |
| 10 | **Credencial de homologação de NeoID e RemoteID.** A página de cadastro da Lacuna cobre só BirdID, SafeID e VIDaaS | Serpro e Certisign, direto | Dois dos cinco PSCs só se testam com cadastro no provedor |
| 11 | **Se existe plano do Signer abaixo de R$ 1.750,00/mês** para volume de dezenas de documentos | Comercial Lacuna | Muda a alavanca de corte da seção 10 |

---

## 13. Contradições com os docs existentes

Sete. Seis são com o `estudo-assinatura-panorama.md`, que é o documento mais recente, e nenhuma invalida a recomendação dele de deixar a Lacuna como 1ª da trilha B.

### 1. "Não existe fluxo pronto" vale para dois produtos, não para o fornecedor

**Onde:** `estudo-assinatura-panorama.md`, seção 6, trilha B: "O custo: **não existe fluxo pronto.** Convite ao signatário, ordem das assinaturas, reenvio, expiração e manifesto viram código nosso."

**O que é:** verdade para Web PKI mais Rest PKI. Falso para a Lacuna como fornecedor. O **Lacuna Signer** tem `flowActions` com `step` de ordenação, tipos `Signer`, `Approver`, `SignRule` e `ApproverRule`, notificação automática por e-mail ao criar o documento, `POST /api/notifications/flow-action-reminder` para lembrete, widget de assinatura embutido com eventos `documentSigned` e `documentApproved`, versão para impressão com manifesto e nove eventos de webhook.

**Correção sugerida:** trocar por "não existe fluxo pronto **na combinação Web PKI mais Rest PKI**. O Lacuna Signer tem, a R$ 1.750,00/mês".

### 2. A linha de webhook da Lacuna está errada

**Onde:** `estudo-assinatura-panorama.md`, Tabela A, coluna Webhook, linha Lacuna: "Não se aplica. O fluxo é nosso, a assinatura fecha síncrona no nosso backend".

**O que é:** o Rest PKI Core tem webhook, com evento `DocumentSignatureCompleted` e três modos de autenticação de origem. O Signer tem nove eventos. A frase só vale para o desenho do cenário token, onde de fato a assinatura fecha síncrona.

**Correção sugerida:** "Sim. Rest PKI Core com 1 evento e 3 modos de autenticação. Signer com 9 eventos. Dispensável no cenário token, em que a assinatura fecha síncrona".

### 3. "Preço não publicado" é falso

**Onde:** `estudo-assinatura-panorama.md`, seção "O que ele não responde" e Tabela B: "Lacuna licencia o Web PKI por domínio sem tabela pública" e "Não publicado, exige contato comercial".

**O que é:** a tabela existe, em `lacunasoftware.com/pt-br/pricing/`, com cinco faixas de transação, cinco faixas de carimbo de tempo, mínimo mensal de R$ 200,00, 150 transações grátis por 3 meses, licenças de servidor a R$ 54.000,00 e R$ 23.000,00, Signer a R$ 1.750,00/mês e Amplia a R$ 79.000,00. A página é renderizada por JavaScript, o que explica a leitura anterior.

**Correção sugerida:** substituir a linha da Lacuna na Tabela B pela tabela da seção 9 deste documento, e riscar o item 3 e o item 9 da lista de pendências do panorama. Acrescentar que **a licença do Web PKI é isenta quando usada com o Rest PKI em nuvem, inclusive em produção**.

### 4. "Totalmente embutida. Nenhuma tela de terceiro" depende da rota

**Onde:** `estudo-assinatura-panorama.md`, Tabela A, coluna "Embutida ou redirect", linha Lacuna.

**O que é:** três rotas, três respostas. Web PKI na nossa página é embutida de verdade. PKI Express com fluxo PWD é embutida de verdade. **Sessão de assinatura do Rest PKI Core é redirect**, para uma página hospedada pela Lacuna: "sua aplicação especifica um `returnUrl` e recebe de volta um `redirectUrl`. Sua aplicação então redireciona o usuário".

**Correção sugerida:** "Embutida nas rotas Web PKI e PKI Express. Redirect na rota de sessão de assinatura do Rest PKI Core, que é a mais barata de integrar".

### 5. "Quem guarda o documento: nós, integralmente" vale para uma das três rotas

**Onde:** `estudo-assinatura-panorama.md`, Tabela B, linha Lacuna.

**O que é:** verdade no Rest PKI clássico com assinatura web remota, cuja política de privacidade lista exatamente três dados de usuário final, "Certificado digital; Endereço IP; Hash de documento". Falso na sessão de assinatura do Rest PKI Core e no Signer, onde o arquivo é enviado e guardado.

**Correção sugerida:** qualificar com a tabela da seção 7. Isso interage com `arquitetura-seguranca.md` e merece decisão explícita do cliente, não default de implementação.

### 6. A estimativa de 60 a 80h

**Onde:** `estudo-assinatura-panorama.md`, seção 6, tabela "Ordem de grandeza": "Lacuna, cobrindo os dois: 60 a 80h".

**O que é:** 86 a 118h pela quebra da seção 10. A diferença vem de cinco itens que a estimativa anterior não tinha como enxergar sem ler o Swagger, listados na mesma seção. O maior deles é a rotina de extensão de carimbo de arquivamento, que nenhum documento do projeto previa.

**Correção sugerida:** atualizar a linha para 86 a 118h e a linha da Fase 2 em `plano-do-projeto.md` para 57 a 94h conforme o cenário, com a ressalva de que a resposta do cliente sobre tipo de certificado ainda está aberta.

### 7. As URLs de documentação citadas no panorama devolvem 404

**Onde:** `estudo-assinatura-panorama.md`, anexo de fontes, seis links da Lacuna terminados em `.html`.

**O que é:** a documentação migrou para Docusaurus e o sufixo `.html` foi removido. `https://docs.lacunasoftware.com/pt-br/articles/web-pki/get-started.html` devolve 404; sem o `.html`, devolve 200. As URLs deste documento estão na forma que resolve hoje.

**Correção sugerida:** remover o `.html` das seis fontes da Lacuna no anexo do panorama.

---

## Anexo: fontes, com data de acesso

Todas acessadas em 12/09/2026.

### Documentação oficial Lacuna

| Assunto | URL |
|---|---|
| Soluções para certificação digital, o catálogo | https://docs.lacunasoftware.com/pt-br/articles/pki-guide |
| Assinaturas web: remota versus local, e o limite de Windows | https://docs.lacunasoftware.com/pt-br/articles/pki-guide/web-signatures |
| Certificados de teste, os quatro `.pfx` e o id do contexto de segurança | https://docs.lacunasoftware.com/pt-br/articles/pki-guide/test-certs |
| Web PKI, primeiros passos, CDN e npm | https://docs.lacunasoftware.com/pt-br/articles/web-pki/get-started |
| Web PKI, navegadores e sistemas suportados | https://docs.lacunasoftware.com/pt-br/articles/web-pki/browser-support |
| Web PKI, licenciamento por domínio e a isenção com Rest PKI em nuvem | https://docs.lacunasoftware.com/pt-br/articles/web-pki/licensing |
| Web PKI, atributos de segurança: Web Extension e Native App | https://docs.lacunasoftware.com/pt-br/articles/web-pki/security |
| Web PKI, comportamento quando não instalado | https://docs.lacunasoftware.com/pt-br/articles/web-pki/customizing-not-installed |
| Web PKI, atualização automática e versão 2.16.5 da biblioteca | https://docs.lacunasoftware.com/pt-br/articles/web-pki/update |
| Web PKI, definições de tipo com `signWithRestPki` e `preauthorizeSignatures` | https://github.com/LacunaSoftware/docs/blob/master/typedocs/lacuna-web-pki.d.ts |
| Rest PKI, visão geral e on premises | https://docs.lacunasoftware.com/pt-br/articles/rest-pki |
| Rest PKI, política de privacidade: os três dados de usuário final | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/privacy-policy |
| Rest PKI, configuração de carimbo de tempo e requisitos RFC 3161 | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/on-premises/configure-timestamping |
| Rest PKI Core, visão geral, SaaS e on premises | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core |
| Rest PKI Core, primeiros passos de integração | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/get-started |
| Rest PKI Core, sessões de assinatura e fluxo com webhook | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/signature-sessions |
| Rest PKI Core, requisitos de certificado `CryptoDevice` e `Cpf` | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/signature-sessions/certificate-requirements |
| Rest PKI Core, webhooks e os três modos de autenticação | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/core/integration/webhooks |
| Rest PKI Core, Swagger público: endpoints, enums e modelos | https://core.pki.rest/swagger/api/swagger.json |
| PKI Express, visão geral e formatos suportados | https://docs.lacunasoftware.com/pt-br/articles/pki-express |
| PKI Express, configuração dos cinco trust services | https://docs.lacunasoftware.com/pt-br/articles/pki-express/config/trust-services |
| PKI SDK, certificados em nuvem | https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/cloud-certificates |
| PKI SDK, BrazilTrustServices: fluxos PWD e OAuth, tipos de sessão | https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/cloud-certificates/brazil-trust-services |
| PKI SDK, assinaturas PAdES e ETSI 102778-x | https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/signatures/pades |
| PKI SDK, políticas ICP-Brasil e o PAdES "em desenvolvimento" | https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/signatures/policies/pki-brazil |
| PKI SDK, mapeadores de política AD-RC v1.0 a v2.1 | https://docs.lacunasoftware.com/pt-br/articles/pki-sdk/signatures/policies/mappers |
| Signer, visão geral e instância por cliente | https://docs.lacunasoftware.com/pt-br/articles/signer |
| Signer, guia de integração: fluxo, ordem, lembrete, validação, webhook | https://docs.lacunasoftware.com/pt-br/articles/signer/integration-guide |
| Signer, assinatura embutida com `LacunaSignerWidget` | https://docs.lacunasoftware.com/pt-br/articles/signer/embedded-signature |
| Signer, Swagger público: os nove `WebhookTypes` | https://www.dropsigner.com/swagger/api/swagger.json |
| Amplia, plataforma de Autoridade Certificadora | https://docs.lacunasoftware.com/pt-br/articles/amplia |
| Lacuna PSC, DOC-ICP-17.01 e OAuth 2.0 | https://docs.lacunasoftware.com/pt-br/articles/psc |
| Lacuna TSA, RFC 3161 | https://docs.lacunasoftware.com/pt-br/articles/tsa |

### Preço

| Assunto | URL |
|---|---|
| Página de preços, renderizada por JavaScript | https://www.lacunasoftware.com/pt-br/pricing/ |
| Textos de preço servidos à página, sem autenticação | https://www.lacunasoftware.com/assets/i18n/pt.json |
| Lógica do simulador, com as faixas de transação e de carimbo | https://www.lacunasoftware.com/main-VBIYTGQZ.js |
| Portal do Rest PKI em nuvem, com link para a página de preços | https://pki.rest/ |

### Instalação do componente

| Assunto | URL |
|---|---|
| Página única de instalação do Web PKI, com detecção de navegador | https://get.webpkiplugin.com/ |
