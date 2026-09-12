# Estudo de Assinatura Digital: Tipos de Certificado e Fornecedores

**Frente 1** · 12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 3) e `plano-do-projeto.md` (rev. 2)

---

## O que este documento responde

Diferença prática entre A1, A3 em mídia física e A3 em nuvem; o que cada tipo exige do navegador em 2026; quais permitem assinatura dentro da nossa tela; o que a lei realmente exige da CPR eletrônica; comparativo dos seis fornecedores candidatos pelos oito critérios de `plano-do-projeto.md`; e os quatro provedores de certificado em nuvem. A recomendação sai em duas trilhas, porque a pergunta 1 de `entendimento-do-projeto.md` continua aberta.

## O que ele não responde, e por quê

**Preço real.** Três dos seis fornecedores publicam tabela (ZapSign, Clicksign, D4Sign). Os outros três (BRy, Lacuna, Certisign) não publicam nada: BRy exige cadastro em `cloud.bry.com.br` para ver a própria documentação, Lacuna licencia o Web PKI por domínio sem tabela pública, e o portal de desenvolvedores da Certisign (`desenvolvedor.portaldeassinaturas.com.br`) é um Azure API Management com login obrigatório. Onde não há fonte, este documento escreve "não publicado, exige contato comercial". Nenhum preço foi estimado.

**Fidelidade do sandbox.** Todos os que têm sandbox descrevem que ele existe. Nenhum documenta se o ambiente de teste reproduz o fluxo de certificado digital, que é justamente a parte que precisa ser testada. Só se descobre usando.

**A documentação técnica da Valid (VIDaaS).** O portal `developers.integraicp.com.br/api-reference/v3/` devolve 403 sem credencial, e a própria página da Valid diz que a chave de acesso ("canal") só sai por solicitação à equipe comercial (https://validcertificadora.com.br/pages/psc-integracao-via-api, acesso 12/09/2026). O que está aqui sobre VIDaaS vem da página comercial da Valid e da configuração pré-pronta da Lacuna, não do manual.

**Se cada fornecedor aceita certificado de PJ.** A Clicksign é explícita que só aceita e-CPF. Os outros não dizem. Para CPR emitida por cooperativa isso importa.

**Qual fornecedor a B3 ou o escritório sócio já usa.** Nenhuma fonte pública. Pergunta para o cliente.

---

## 1. Os três tipos de certificado

| | **A1** | **A3 em token ou cartão** | **A3 em nuvem** |
|---|---|---|---|
| Onde mora a chave privada | Arquivo `.pfx`/`.p12` no disco ou no repositório do sistema operacional | Chip do token USB ou smart card | HSM de um Prestador de Serviço de Confiança (PSC), regulado pelo DOC-ICP-17 |
| Exportável | Sim. É um arquivo, copia-se | Não. Sai do chip apenas a assinatura | Não. Nunca sai do HSM |
| Validade típica | 1 ano | Até 5 anos | Até 5 anos |
| O que o signatário faz | Informa a senha do arquivo | Pluga o dispositivo e digita o PIN | Autoriza no celular (app, biometria ou push) |
| O que ele precisa ter | O arquivo em cada máquina que usar | O token, o driver instalado e a máquina certa | Um celular |
| Onde a assinatura acontece | Navegador do usuário, ou servidor se ele enviar o arquivo | Obrigatoriamente no dispositivo do usuário | Servidor do PSC |
| Para quem integra | Simples se o arquivo puder subir para o servidor. Caro se não puder | O caso difícil. Exige componente local | API REST com OAuth 2.0. O caso fácil |
| Fluxo possível | Embutido ou servidor | Embutido com componente local, ou fora da nossa tela | Embutido com redirect curto, ou push sem redirect nenhum |
| Status regulatório | **Em extinção.** Res. CG ICP-Brasil 211/2024, art. 3º | Vigente | Vigente |

### O A1 está sendo extinto

A Resolução CG ICP-Brasil nº 211, de 31/10/2024, art. 3º, extingue os certificados de assinatura dos tipos **A1 e A2** e os de sigilo S1 a S4. A3 e A4 permanecem. No lugar entram quatro tipos novos (art. 2º): SE-S e SE-H (selo eletrônico, software e hardware) e AE-S e AE-H (aplicações específicas, software e hardware). Fonte: https://repositorio.iti.gov.br/resolucoes/Resolucao211_pauta_modernizante.htm, acesso 12/09/2026.

Selo eletrônico e aplicações específicas são certificados de **pessoa jurídica e de sistema**, não substitutos do e-CPF de assinatura. Quem assina como pessoa física em 2027 usa A3, em mídia ou em nuvem.

Consequência de projeto: **não construir nada apoiado em A1 como cenário principal.** Se hoje parte dos membros usa A1, essa parte migra para A3 dentro do horizonte do contrato, e migra na direção da nuvem, que é a opção barata.

As datas exatas de corte circulam em resumos de terceiros (fim de emissão na cadeia V10 em 31/12/2026, uso admitido de A1 até 02/03/2029) e **não foram confirmadas no texto oficial** que consegui ler. Tratar como indício, não como prazo. Ver "O que não consegui confirmar".

---

## 2. O que cada tipo exige do navegador

### O applet Java morreu. O que ocupou o lugar

Chrome removeu o NPAPI em 2015 e a Oracle depreciou o plugin do navegador na sequência. O acesso a smart card por página web passou a ser feito por **extensão de navegador conversando com um executável local por native messaging**. A documentação da Lacuna descreve o próprio produto exatamente assim: o Web PKI é "uma alternativa ao uso de applets Java para acesso a smartcards em páginas web" (https://docs.lacunasoftware.com/pt-br/articles/pki-guide/index.html, acesso 12/09/2026).

O motivo técnico está escrito na documentação de assinaturas web da Lacuna: a operação precisa acontecer no frontend porque a chave privada de um certificado A3 está em dispositivo criptográfico que **nunca permite exportação**. O servidor manda o hash, o dispositivo devolve a assinatura. Não existe atalho.

**Web PKI (Lacuna)** é o componente que o mercado brasileiro padronizou. Dados oficiais (https://docs.lacunasoftware.com/pt-br/articles/web-pki/browser-support.html e `.../web-pki/get-started.html`, acesso 12/09/2026):

| Item | Valor |
|---|---|
| Navegadores | Chrome 44+, Firefox 50+, Edge 42+, IE9+ |
| Sistemas | Windows 7 SP2+, Linux (Debian, RedHat, Slackware), macOS 10.12+ |
| Como a página usa | Biblioteca JS `lacuna-web-pki.js` (CDN ou pacote npm `web-pki`), classe `LacunaWebPKI`, métodos `listCertificates()`, `readCertificate()`, `signData()`, `signHash()` |
| Licença | Por domínio. Gratuito em `localhost`, pago em produção |

A licença por domínio é o detalhe que some nas demos: usar Web PKI dentro da Clicksign ou da D4Sign é licença deles. Usar no nosso domínio é licença nossa.

### A tabela do que o usuário instala

| Tipo | Extensão de navegador | Componente local | App no celular | Driver |
|---|---|---|---|---|
| A1 no navegador do usuário | Sim (Web PKI ou equivalente) | Sim, o host nativo do Web PKI | Não | Não |
| A1 enviado ao servidor | Não | Não | Não | Não |
| A3 token ou cartão | Sim, obrigatório | Sim, obrigatório | Não | Sim, do fabricante do token |
| A3 em nuvem | **Nada** | **Nada** | Sim, o app do PSC | Não |

A3 em nuvem é o único tipo que não pede nada do navegador. É a diferença que decide o escopo da Fase 2.

### Onde a assinatura acontece, por tipo

| Tipo | Dá para assinar dentro da nossa tela? | O que acontece de fato |
|---|---|---|
| A1 | Sim | Ou o usuário sobe o `.pfx` e o backend assina, ou o Web PKI assina no navegador. Nenhum redirect |
| A3 token ou cartão | Sim, com componente local | A página chama o Web PKI, o usuário digita o PIN em um diálogo do componente, a página recebe a assinatura. A tela é nossa, o componente é de terceiro |
| A3 em nuvem, fluxo authorization code | Parcial | Redirect para o ambiente do PSC, o usuário autentica lá, volta com o código. Saída curta e visível |
| A3 em nuvem, fluxo push | Sim, sem redirect nenhum | Nossa tela dispara a requisição, o celular do usuário toca, ele aprova no app, nosso backend recebe o callback. O navegador nunca sai da página |

**O fluxo push do certificado em nuvem é o único que entrega a promessa de "assinar sem sair da plataforma" sem instalar nada.** Está documentado no Bird ID (`POST /async-signature` com lista de hashes, callback e token de sessão) e no NeoID (sessão de assinatura com validade contratada pelo titular).

---

## 3. Impacto jurídico: CPR e registro na B3

### Os quatro dispositivos

| Norma | O que estabelece | Efeito para nós |
|---|---|---|
| **MP 2.200-2/2001, art. 10, § 1º** | Documentos produzidos com certificação da ICP-Brasil "presumem-se verdadeiros em relação aos signatários" | Assinatura qualificada inverte o ônus da prova. Quem nega tem que provar |
| **MP 2.200-2/2001, art. 10, § 2º** | Não obsta outro meio de comprovação de autoria e integridade, inclusive certificado fora da ICP-Brasil, "desde que admitido pelas partes como válido ou aceito pela pessoa a quem for oposto o documento" | Assinatura não-ICP vale, e depende de aceitação. Em contrato entre membros de clube fechado com termo de adesão, isso é contratável |
| **Lei 14.063/2020, art. 4º** | Três níveis: I simples, II avançada (certificado não emitido pela ICP-Brasil ou outro meio, com vínculo unívoco, controle exclusivo e detecção de alteração), III **qualificada, a realizada com base em certificado emitido pelo ICP-Brasil**. O § 1º diz que a qualificada tem o nível mais elevado de confiabilidade | Define o vocabulário. "ICP-Brasil" e "qualificada" são a mesma coisa |
| **Lei 8.929/1994, art. 3º, VIII** (redação da Lei 13.986/2020) | Requisito da CPR: "Nome, qualificação e assinatura do emitente e dos garantidores, que poderá ser feita de forma eletrônica" | A CPR eletrônica é expressamente autorizada |
| **Lei 8.929/1994, art. 3º, § 4º** (redação da Lei 14.421/2022, originada da MP 1.104/2022) | As partes definem a forma e o nível de segurança da assinatura para fins de validade, eficácia e executividade. **I: na CPR e no documento apartado de descrição de garantias, admite-se assinatura simples, avançada ou qualificada. II: no registro e averbação de garantia real sobre móvel e imóvel, admite-se avançada ou qualificada** | O dispositivo que responde a pergunta |
| **Lei 8.929/1994, art. 12** (redação da Lei 14.421/2022) | Registro ou depósito em entidade autorizada pelo Banco Central, em até 30 dias úteis para CPR emitida a partir de 11/08/2022 | O prazo que a máquina de estados precisa respeitar. Hoje não está em `maquina-de-estados.md` |

### A CPR eletrônica exige assinatura qualificada? Não

A resposta direta, com o artigo: **Lei 8.929/1994, art. 3º, § 4º, I.** A CPR admite assinatura eletrônica **simples, avançada ou qualificada**. O piso legal é a assinatura simples.

Assinatura qualificada só vira exigível em um caso, e por outro inciso: **art. 3º, § 4º, II**, no registro e na averbação de garantia real sobre bem móvel ou imóvel, onde o mínimo sobe para avançada. Mesmo ali a qualificada não é obrigatória, é uma das duas opções.

Duas leituras práticas disso:

1. **Exigir ICP-Brasil é decisão do cliente, não imposição da lei.** `entendimento-do-projeto.md` registra ICP-Brasil como "requisito confirmado". Continua sendo um requisito válido, e a justificativa correta é a presunção de veracidade do art. 10, § 1º da MP 2.200-2 e a executividade do título sem discussão, não "a lei manda".
2. **Se as CPRs do clube tiverem garantia real (hipoteca, penhor, alienação fiduciária), o § 4º, II passa a valer.** O layout da B3 tem campo Tipo de Garantia com dez valores, seis deles reais. Esse é o gatilho que torna a escolha de nível de assinatura uma regra de negócio por registro, não uma configuração global. Ver "Perguntas para o cliente".

### O que a B3 exige

Nada publicado sobre o tipo de certificado do signatário.

A B3 registra **dados estruturados**, não o PDF. O layout de CPR 2.0 tem um único campo sobre o assunto, `Emissão Eletrônica/Digital`, texto de 1 caractere, `S` ou `N` (ver `estudo-api-b3.md`, seção 2). Não há campo para hash do documento, para certificado do signatário, nem para manifesto de assinatura.

Isso tem três consequências:

- **A B3 nunca vê a assinatura.** Ela não valida, não carimba, não recusa por causa dela. Um erro de assinatura não gera `FALHA_B3`.
- **O certificado que a B3 verifica é outro.** O mTLS da API é a credencial da instituição, do escritório sócio. Não tem relação com o certificado do produtor.
- **A responsabilidade pela veracidade fica com o Agente de Registro**, conforme o Manual de Normas de CDA, WA e CPR. Quem responde se a assinatura for contestada é o escritório sócio, não a B3. Isso reforça o argumento pela assinatura qualificada, por motivo de risco e não de norma.

---

## 4. Fornecedores

Seis candidatos de `plano-do-projeto.md` mais um sétimo que apareceu na pesquisa. Os oito critérios do plano estão distribuídos em duas tabelas, mesmas linhas e mesmas colunas para todos.

Uma distinção que muda a leitura: **ZapSign, Clicksign e D4Sign são plataformas de assinatura** (nós mandamos o documento, eles conduzem o signatário). **BRy e Lacuna são fornecedores de componente** (nós conduzimos o signatário, eles fornecem a criptografia). Certisign é os dois, com documentação fechada.

### Tabela A: capacidade técnica

| Fornecedor | ICP-Brasil qualificada | Certificado em nuvem via API | Embutida ou redirect | Webhook |
|---|---|---|---|---|
| **ZapSign** | Sim. É **AC credenciada** à ICP-Brasil e emite certificado próprio | Blog do fornecedor cita BirdID, RemoteID, VIDaaS e SafeID. **Não consta na documentação técnica** | **Embutida.** Widget iframe `app.zapsign.com.br/verificar/{token}`, com `window.onmessage` para `loaded`, `signed` e arquivo pronto. Exige `allow="camera"` se houver biometria | Sim. Eventos, logs de entrega e ambiente de teste de webhook documentados |
| **Clicksign** | Sim. ICP-Brasil é tipo de requisito de autenticação de signatário | **Sim, seis provedores nominais**: BirdID, SafeID, VIDaaS, DS Cloud, SerproID/NeoID, SyngularID. Busca pelo CPF e **redirect para o ambiente do provedor** | **Mista.** Widget Embedded (`embedded.min-2.1.0.js`, eventos `loaded`, `signed`, `resized`) assina na nossa página, mas certificado em nuvem sai para o provedor e certificado local exige Web PKI | Sim. POST HTTP para URL cadastrada, eventos `close` e `document_closed`, página de boas práticas |
| **D4Sign** | Sim. Endpoints para definir e listar o certificado ICP-Brasil por signatário | Não mencionado na documentação de ICP-Brasil | **Embutida.** EMBED cria iframe por JS apontando para `secure.d4sign.com.br/embed/viewblob`. **Assinatura com certificado só funciona em Windows** | Sim, POSTback, opcional |
| **BRy** | Sim. CAdES, XAdES e PAdES com política de assinatura e validação de longo prazo | Sim. Header `kms_type` com `BRYKMS`, `GOVBR` e `DINAMO`. GOVBR por OAuth 2.0; BRYKMS e Dinamo em uma etapa, com `uuid_cert` e PIN em `kms_data` | **Componente.** Não há widget iframe documentado publicamente. A UI é nossa | Não documentado publicamente |
| **Lacuna** | Sim. Rest PKI, PKI SDK e PKI Express, com carimbo do tempo | Sim. Cinco serviços pré-configurados no PKI Express: **BirdID, NeoID, RemoteID, SafeID, VIDaaS**, configurados por `clientId` e `clientSecret` | **Totalmente embutida.** Web PKI no navegador para A1 e A3 local, trust services para nuvem. Nenhuma tela de terceiro | Não se aplica. O fluxo é nosso, a assinatura fecha síncrona no nosso backend |
| **Certisign** | Sim. AC desde a origem da ICP-Brasil. RemoteID é o certificado em nuvem | Sim, RemoteID. Para aplicações sem integração em nuvem exige instalar o **DesktopID** na máquina | Portal de Assinaturas com portal de desenvolvedor. **Documentação atrás de login**, não verificável | Não verificável |
| **Assinei (Aliare)** | Sim, segundo o fornecedor. Produto vertical de CPR, com registro integrado | Não publicado | Produto pronto, não plataforma de integração. **Concorrente, não fornecedor** | Não publicado |

### Tabela B: operação e comercial

| Fornecedor | Sandbox | Quem guarda o documento | Preço público | Manifesto e trilha |
|---|---|---|---|---|
| **ZapSign** | Sim, `sandbox.app.zapsign.com.br`, com token próprio e **sem validade jurídica** | ZapSign. Existem endpoints de cancelar e excluir documento | **Sim.** Individual grátis, 3 docs/mês. Profissional a partir de R$ 29,90/mês. Team a partir de R$ 49,90/mês. Enterprise a partir de R$ 500/mês. Assinatura com certificado digital **R$ 0,50 por assinatura**. **API e webhook só nos planos Team e Enterprise** | Documento de autenticidade com registro de eventos. Detalhe do manifesto não verificado |
| **Clicksign** | Sim, e **habilitado por padrão, sem contrato**. Widget em produção exige acionar a Clicksign | Clicksign | **Sim, com ressalva.** Start, Plus e Automação com limites de 200, 350 e 500 docs/mês. A página mistura preço promocional de primeira mensalidade com preço cheio, e o excedente por documento aparece como "até R$ 3,00 / R$ 4,90 / R$ 6,90". Avançado sob medida. **Confirmar com o comercial** | Documento assinado leva o certificado ICP-Brasil da Clicksign. Detalhe não verificado |
| **D4Sign** | Sim, `sandbox.d4sign.com.br`. **Ativação da API exige e-mail ao suporte** | D4Sign | **Parcial.** Starter R$ 39,90/mês com 20 documentos. Advanced R$ 59,90/mês. ICP-Brasil sem custo adicional. **API Premium "sob consulta"**, que é justamente o que precisamos | Não verificado |
| **BRy** | Sim. Cadastro no BRy Cloud dá 10 créditos e um certificado de teste | **Nós.** A API assina e devolve, não hospeda fluxo | **Não publicado, exige contato comercial.** A documentação inteira exige cadastro em `cloud.bry.com.br` | O mais forte do grupo. PAdES/CAdES com política de assinatura e carimbo do tempo para validação de longo prazo |
| **Lacuna** | Web PKI gratuito em `localhost`. Rest PKI com conta de teste | **Nós.** Integralmente | **Não publicado, exige contato comercial.** Web PKI é licença por domínio | Forte. Assinatura padrão ICP-Brasil com carimbo do tempo, no nosso storage |
| **Certisign** | Não verificável | Portal de Assinaturas armazena. Modelo de integração não verificável | **Não publicado, exige contato comercial** | Não verificável |
| **Assinei (Aliare)** | Não publicado | Assinei | **Não publicado** | Não publicado |

### Duas observações de preço

**A opex do dossiê (R$ 295/mês) não cobre o cenário de API.** Na ZapSign, API só existe a partir do plano Team; com 200 documentos o plano Team publicado é R$ 259,90/mês, mais R$ 0,50 por assinatura com certificado. Uma CPR com três partes assinando custa R$ 1,50 de add-on. Cem CPRs por mês com três partes: R$ 259,90 + R$ 150,00. Já estoura.

**O certificado em nuvem tem custo próprio, e ele é de quem assina.** O SafeID Integração publica tabela: 50 assinaturas/mês grátis, 100 por R$ 100,00/mês, 500 por R$ 400,00/mês, 1.000 por R$ 640,00/mês, com excedente de R$ 0,90, R$ 0,64 e R$ 0,48. Se o clube quiser bancar o certificado dos membros, isso é uma segunda linha de opex, não uma variação da primeira.

---

## 5. Certificados em nuvem

Os quatro provedores pedidos, mais o RemoteID da Certisign, que aparece na mesma lista de trust services da Lacuna e é o quinto PSC que o mercado integra. Todos são certificados **A3 em nuvem**, com chave privada em HSM sob o DOC-ICP-17 (criado pela Resolução ITI nº 132/2017).

| | **VIDaaS (Valid)** | **Bird ID (Soluti / VaultID)** | **SafeID (Safeweb)** | **NeoID / SerproID (Serpro)** | **RemoteID (Certisign)** |
|---|---|---|---|---|---|
| Documentação pública | **Não.** Portal `developers.integraicp.com.br` devolve 403 | **Sim**, `docs.vaultid.com.br`, aberta e completa | Portal existe (`pscsafeweb.safewebpss.com.br/Docs/`), renderizado por JS, não legível por fetch | **Sim**, `neoid.estaleiro.serpro.gov.br`, a mais detalhada das cinco | Não localizada |
| Protocolo | OAuth 2.0 com authorization code e redirect URIs cadastradas | OAuth 2.0 em três variantes: authorization code (web), password (desktop), client credentials (aplicação) | Não verificado | **OAuth 2.0 authorization code com PKCE obrigatório** | Não verificado |
| Endpoint de assinatura | Não verificado | `POST /async-signature` com lista de hashes e `GET /async-signature` para o conteúdo assinado | Não verificado | `POST https://serproid.serpro.gov.br/oauth/v0/oauth/signature`, `signature_format` `RAW` (PKCS1) ou **`CMS` (PKCS7, qualificada)** | Não verificado |
| Como o usuário autoriza | App VIDaaS no celular, com biometria | **QR Code ou push no app.** O app mostra a mensagem que a aplicação enviou | App SafeID no celular | Não detalhado na página de token | App, ou **DesktopID instalado** quando a aplicação não integra em nuvem |
| Autorização vale para quantas assinaturas | Não verificado | Token de sessão com validade configurável: **até 7 dias para PF e 30 dias para PJ** | Não verificado | Sessão de assinatura: **PF de 15 minutos a 7 dias, PJ de 1 hora a 30 dias.** Token de assinatura única ou autenticação: **5 minutos** | Não verificado |
| Retorno assíncrono | Não verificado | **Sim, callback HTTP** após a confirmação no app | Não verificado | Não verificado | Não verificado |
| Como se contrata a integração | "Canal" (chave de acesso) liberado pela equipe comercial da Valid | Cadastro de aplicação | Conta no SafeID Integração + certificado SafeID | Cadastro de aplicação, com insumos de homologação publicados | Não verificado |
| Preço da integração | Não publicado | Não publicado | **Publicado.** 50/mês grátis, 100 por R$ 100, 500 por R$ 400, 1.000 por R$ 640 | Não publicado | Não publicado |
| Integrado por | Clicksign, Lacuna, ZapSign (blog) | Clicksign, Lacuna, ZapSign (blog) | Clicksign, Lacuna, ZapSign (blog) | Clicksign, Lacuna, BRy (`kms_type=GOVBR` é gov.br, não NeoID) | Clicksign, Lacuna, ZapSign (blog) |

### O que isso significa para a UX

A sessão de assinatura longa é o achado operacional. Bird ID e NeoID permitem que o titular autorize **uma sessão** de até 7 dias (PF), e dentro dela a aplicação assina sem nova interação. Para uma CPR isso não interessa muito, já que é um documento por vez. Interessa para o caminho 3 da `maquina-de-estados.md`, reassinatura: o produtor pode autorizar uma vez e o documento corrigido ser assinado sem trazer ele de volta.

O contraponto: uma sessão de 7 dias que assina sem interação é exatamente o tipo de poder que precisa de log de auditoria com o mesmo rigor que `arquitetura-seguranca.md` exige para acesso a dado de registro. Se formos por esse caminho, cada assinatura feita dentro de uma sessão precisa gravar qual sessão a autorizou e quando ela foi criada.

---

## 6. Recomendação

Três finalistas. A ordem muda conforme a resposta do cliente.

### Trilha A, se os membros usarem certificado em nuvem

**1º Clicksign.** Único fornecedor que documenta nominalmente **seis** provedores de nuvem (BirdID, SafeID, VIDaaS, DS Cloud, SerproID/NeoID, SyngularID). Sandbox habilitado por padrão sem contrato, o que destrava a Fase 1 no mesmo dia. Widget Embedded com eventos JS. Webhook com página de boas práticas e eventos nomeados. Preço publicado, ainda que confuso.

O custo: certificado em nuvem **sai da nossa tela** para o ambiente do provedor. E a Clicksign só aceita e-CPF, o que exclui assinatura por e-CNPJ de cooperativa.

**2º ZapSign.** Mais barata com folga, é AC credenciada (emite o certificado do membro que não tiver um, o que resolve um problema de adoção real), e o widget iframe é o mais simples dos três. Sandbox explícito.

O custo: o suporte a certificado em nuvem aparece **em blog, não em documentação técnica**. Isso é exatamente o tipo de afirmação que não se compra sem prova. E API só a partir do plano Team.

**Descartado nesta trilha:** D4Sign, que não menciona certificado em nuvem em nenhuma página de ajuda sobre ICP-Brasil.

### Trilha B, se os membros usarem token ou cartão físico

**1º Lacuna.** É a única opção que mantém A3 físico **dentro da nossa tela em Windows, Linux e macOS**. Web PKI é o padrão de fato do mercado, com biblioteca JS, npm e API documentada. O documento fica no nosso storage, que é o que `arquitetura-seguranca.md` pede. Rest PKI ou PKI Express fecha a assinatura no backend.

O custo: **não existe fluxo pronto.** Convite ao signatário, ordem das assinaturas, reenvio, expiração e manifesto viram código nosso. A Fase 2 estimada em 32 a 40h não cabe nesse desenho.

**2º BRy.** Mesma natureza de componente, com a melhor história de manifesto: PAdES e CAdES com política de assinatura e validação de longo prazo. Cadastro gratuito dá 10 créditos e um certificado de teste, então dá para provar a integração antes de negociar.

O custo: documentação inteira atrás de cadastro, preço não publicado, e nenhum widget embutido documentado.

**Descartado nesta trilha:** D4Sign. Tem o fluxo pronto e o iframe, mas a própria ajuda diz que a assinatura com certificado ICP-Brasil "funciona apenas em computadores com sistemas Windows", e ainda cita cerca de 1 hora para a plataforma reconhecer um token recém-conectado. Produtor rural com Mac ou com pressa não assina. Para um clube de convidados isso é uma trilha de suporte permanente.

### Quem cobre os dois cenários

**Lacuna.** Web PKI resolve A1 e A3 local; os cinco trust services pré-configurados (BirdID, NeoID, RemoteID, SafeID, VIDaaS) resolvem nuvem, com a mesma API e a mesma tela. É o único fornecedor da lista em que a resposta do cliente **não muda a arquitetura**, só muda um branch.

O preço dessa neutralidade é hora de desenvolvimento. Ordem de grandeza, comparando com `plano-do-projeto.md`:

| Caminho | Fase 2 | O que entra |
|---|---|---|
| Plataforma (Clicksign ou ZapSign), só nuvem | 32 a 40h, como previsto | Criar documento, signatários, webhook, reconciliação |
| Plataforma, com token físico | 40 a 50h | O mesmo, mais suporte a um fluxo que sai da nossa tela e uma trilha de erro nova |
| Lacuna, cobrindo os dois | 60 a 80h | Tudo acima, mais orquestração própria: convite, ordem, expiração, manifesto, storage e reenvio |

**Recomendação operacional:** não escolher ainda. Perguntar ao cliente (seção 9) e, em paralelo, **construir a Fase 1 com uma interface de assinatura de uma porta só**: `criarSolicitacao`, `obterStatus`, `receberRetorno`. Todos os três finalistas cabem atrás dela. O mock da Fase 1 implementa essa interface, e a Fase 2 troca a implementação. Isso já é o desenho previsto em `plano-do-projeto.md`; o que este estudo acrescenta é que a interface precisa comportar **dois modos de entrega ao signatário**, embutido e redirecionado, porque essa é a variável que a resposta do cliente controla.

---

## 7. O que não consegui confirmar

Tudo aqui depende de falar com o comercial ou de credencial de acesso.

| # | Item | Com quem | Por que trava |
|---|---|---|---|
| 1 | **Preço real da Clicksign.** A página de planos mistura primeira mensalidade promocional com preço cheio, e o excedente aparece como "até R$ X" | Comercial Clicksign | Sem isso não dá para comparar com a ZapSign |
| 2 | **Preço da API Premium da D4Sign.** Publicado como "sob consulta", e é exatamente o item que usaríamos | Comercial D4Sign | Preço do plano base é irrelevante sem ele |
| 3 | **Preço de BRy, Lacuna e Certisign.** Nada publicado | Comercial de cada um | Metade dos candidatos não tem número |
| 4 | **Mínimo mensal e política de volume baixo.** Nenhum dos seis publica | Comercial | O clube começa com dezenas de CPRs/mês, não milhares. Quem cobra mínimo alto sai da lista |
| 5 | **Fidelidade do sandbox.** Nenhum documenta se o ambiente de teste reproduz o fluxo de certificado digital de verdade | Suporte técnico de cada um | Sandbox que não testa certificado não serve para a Fase 1 |
| 6 | **Certificado em nuvem na ZapSign.** Só aparece em blog do próprio fornecedor | Suporte ZapSign, pedindo a página de documentação | Se for falso, a ZapSign cai da trilha A |
| 7 | **Certificado ICP-Brasil dentro do widget da ZapSign e da Clicksign.** Nenhuma das duas documentações de widget menciona o assunto | Suporte técnico | É a diferença entre assinatura embutida e promessa quebrada |
| 8 | **Datas de corte do A1.** A extinção está no art. 3º da Res. 211/2024. As datas (31/12/2026, 02/03/2029) vêm de resumos de terceiros | ITI, ou texto integral da Resolução e do DOC-ICP correspondente | Define se A1 entra no MVP como cenário suportado |
| 9 | **Licença do Web PKI: preço e modelo por domínio** | Comercial Lacuna | É custo fixo de produção na trilha B |
| 10 | **Aceite de e-CNPJ.** Só a Clicksign é explícita, e para negar | Comercial de todos | CPR de cooperativa é emitida por PJ |
| 11 | **Documentação da Valid (VIDaaS) e da Certisign** | Comercial de cada um | Duas das quatro nuvens pedidas continuam sendo caixa-preta |

---

## 8. Contradições com os docs existentes

Três. Nenhuma invalida decisão tomada, e as três mudam texto.

### 1. ICP-Brasil não é exigência legal da CPR

**Onde:** `entendimento-do-projeto.md`, tabela "O que mudou da revisão 2", linha ICP-Brasil: "**Confirmado.** É requisito". E `plano-do-projeto.md`, tabela de critérios: "Assinatura qualificada ICP-Brasil / Requisito confirmado".

**O que a lei diz:** Lei 8.929/1994, art. 3º, § 4º, I admite assinatura simples, avançada **ou** qualificada na CPR. A qualificada só vira piso-alternativo no inciso II, para registro e averbação de garantia real, e ainda assim ao lado da avançada.

**Por que importa:** a justificativa muda o que é negociável. Como requisito legal, não se discute. Como escolha de risco (presunção de veracidade da MP 2.200-2, art. 10, § 1º, e responsabilidade do Agente de Registro perante a B3), ela se sustenta melhor, e abre uma alternativa concreta de redução de atrito: assinatura avançada via gov.br para membros sem certificado, com qualificada obrigatória quando houver garantia real.

**Correção sugerida na rev. 4:** trocar "É requisito" por "É requisito do cliente, não da lei. A Lei 8.929/1994, art. 3º, § 4º admite simples, avançada ou qualificada. Qualificada é escolha de risco, e passa a ser exigível na prática quando houver garantia real (inciso II)".

### 2. A promessa de "assinar sem sair da plataforma" não depende só do tipo de certificado

**Onde:** `entendimento-do-projeto.md`, pergunta 1: "A1 ou A3 em nuvem: assinatura por API com autorização do usuário. Dá para manter quase tudo dentro da nossa tela".

**O que muda:** certificado em nuvem **com o fornecedor errado também sai da tela**. A Clicksign documenta que o signatário "é direcionado para o ambiente do provedor". O que mantém a assinatura embutida é o fluxo push (Bird ID, NeoID) ou integração direta com o PSC, não o tipo de certificado em si.

**Correção sugerida:** a linha da tabela vira "A3 em nuvem: dá para manter dentro da nossa tela **se o fornecedor usar fluxo push**. Com authorization code, há redirect curto para o provedor".

### 3. O prazo de 30 dias úteis do art. 12 não está na máquina de estados

**Onde:** `maquina-de-estados.md` não menciona prazo em nenhum estado. `plano-do-projeto.md` não cita o art. 12.

**O que muda:** a Lei 8.929/1994, art. 12, com redação da Lei 14.421/2022, dá **30 dias úteis** entre emissão e registro para CPR emitida a partir de 11/08/2022. Um registro parado em `AGUARDANDO_ASSINATURAS` ou em `EM_CORRECAO` consome esse prazo. A fila de pendências do backoffice precisa ordenar por prazo restante, não por data de entrada.

**Correção sugerida:** acrescentar em `maquina-de-estados.md` um relógio de prazo legal por registro, com alerta antes do vencimento, e no `regras-de-negocio.md` (Frente 4) a regra de expiração. Não é contradição com o que está escrito, é buraco.

---

## 9. Perguntas para o cliente

Em ordem de impacto. As três primeiras mudam a arquitetura.

| # | Pergunta | O que muda |
|---|---|---|
| 1 | **Que certificado os membros já têm hoje: A1, A3 em token, A3 em nuvem, ou nenhum?** Se possível, com proporção | Define a trilha inteira. Sem isso, nenhum contrato de fornecedor deveria ser assinado |
| 2 | **Quantos membros usam Mac ou Linux?** | Se a resposta for "alguns" e o certificado for token, a D4Sign morre e a conta da Fase 2 sobe |
| 3 | **As CPRs do clube terão garantia real** (hipoteca, penhor, alienação fiduciária, cessão fiduciária)? | Liga o art. 3º, § 4º, II. Nível de assinatura vira regra por registro. Amarra com o campo Tipo de Garantia do layout da B3 |
| 4 | **Quem emite CPR: pessoa física ou também cooperativa (PJ)?** | Clicksign só aceita e-CPF. Se houver PJ, ela cai ou vira parcial |
| 5 | **O clube banca o certificado de quem não tem?** | ZapSign é AC e emite. É a favor dela. E vira segunda linha de opex, na ordem de R$ 100 a R$ 640/mês pelas tabelas públicas de SafeID |
| 6 | **Aceitamos assinatura avançada (gov.br) para quem não tiver ICP-Brasil?** | A lei permite na CPR sem garantia real. Reduz atrito de adoção com custo zero de certificado |
| 7 | **O comprador que não é membro assina como convidado externo?** | Já é a pergunta 2 de `entendimento-do-projeto.md`. Agora tem consequência técnica: convidado sem certificado inviabiliza qualificada para todas as partes |
| 8 | **Qual o volume esperado de CPRs por mês e de partes por CPR?** | É a variável que decide entre plataforma e componente. Abaixo de 50 CPRs/mês, plataforma. Acima de 500, componente com certificado em nuvem fica mais barato |
| 9 | **O escritório sócio ou a B3 já têm fornecedor de assinatura preferido?** | Pode encurtar a lista para um |
| 10 | **Exigimos que a assinatura seja rastreável a um único dispositivo autorizado por vez?** | Define se aceitamos sessão de assinatura longa (até 7 dias no Bird ID e no NeoID) ou se cada assinatura pede autorização nova |

---

## Anexo: fontes, com data de acesso

Todas acessadas em 12/09/2026.

### Normas

| Fonte | URL |
|---|---|
| Lei 14.063/2020, art. 4º (tipos de assinatura) | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm |
| Lei 14.063/2020, art. 4º, texto consultado via | https://modeloinicial.com.br/lei/L-14063-2020/lei-14063/art-4 |
| MP 2.200-2/2001, art. 10, §§ 1º e 2º | https://modeloinicial.com.br/lei/MPV-2200-2-2001/medida-provisoria-2200-2/art-10 |
| Lei 8.929/1994 atualizada, art. 3º (incisos e §§) e art. 12 | https://www.legisweb.com.br/legislacao/?id=84206 |
| Lei 8.929/1994, art. 3º, § 4º (redação da Lei 14.421/2022, origem MP 1.104/2022) | https://www.legjur.com/legislacao/art/lei_00089291994-3 |
| Lei 8.929/1994, texto normativo atualizado (Câmara) | https://www2.camara.leg.br/legin/fed/lei/1994/lei-8929-22-agosto-1994-349613-normaatualizada-pl.pdf |
| Resolução CG ICP-Brasil nº 211, de 31/10/2024 (extinção de A1, A2, S1 a S4; criação de SE-S, SE-H, AE-S, AE-H) | https://repositorio.iti.gov.br/resolucoes/Resolucao211_pauta_modernizante.htm |
| Resolução ITI nº 132/2017, que cria o DOC-ICP-17 (Prestadores de Serviço de Confiança) | https://www.gov.br/iti/pt-br/central-de-conteudo/resolucao-132-cria-o-doc-icp-17assdig-pdf |
| DOC-ICP-17.01, procedimentos operacionais mínimos para PSC | https://www.gov.br/iti/pt-br/assuntos/legislacao/documentos-principais/DOCICP17.01verso2.3PROCEDIMENTOSOPERACIONAISMNIMOSPARAOSPRESTADORESDESERVIODECONFIANADAICPBRASIL.pdf |
| DOC-ICP-15, assinaturas digitais na ICP-Brasil | https://www.gov.br/iti/pt-br/central-de-conteudo/doc-icp-15-assinaturas-digitais-na-icp-brasil-pdf |

### Componentes de navegador

| Fonte | URL |
|---|---|
| Lacuna, soluções de certificação digital (Web PKI como alternativa a applet Java) | https://docs.lacunasoftware.com/pt-br/articles/pki-guide/index.html |
| Lacuna Web PKI, primeiros passos (JS, npm, licença por domínio, localhost grátis) | https://docs.lacunasoftware.com/pt-br/articles/web-pki/get-started.html |
| Lacuna Web PKI, suporte de navegadores e sistemas | https://docs.lacunasoftware.com/pt-br/articles/web-pki/browser-support.html |
| Lacuna PKI Express, trust services (BirdID, NeoID, RemoteID, SafeID, VIDaaS) | https://docs.lacunasoftware.com/pt-br/articles/pki-express/config/trust-services.html |
| Lacuna Rest PKI | https://docs.lacunasoftware.com/pt-br/articles/rest-pki/index.html |

### Fornecedores

| Fonte | URL |
|---|---|
| ZapSign, conformidade ICP-Brasil e condição de AC credenciada | https://clients.zapsign.com.br/help/a-zapsign-est%C3%A1-em-conformidade-com-o-icp-brasil |
| ZapSign, autenticação por certificado digital (A1 e A3, e-CPF e e-CNPJ) | https://clients.zapsign.com.br/help/como-assinar-com-certificado-digital |
| ZapSign, widget iframe | https://docs.zapsign.com.br/widget/como-funciona |
| ZapSign, ambientes e sandbox | https://docs.zapsign.com.br/ambiente-de-testes |
| ZapSign, índice completo da documentação | https://docs.zapsign.com.br/llms.txt |
| ZapSign, preços | https://zapsign.com.br/precos |
| ZapSign, blog sobre certificados em nuvem (BirdID, RemoteID, VIDaaS, SafeID). **Blog, não documentação** | https://blog.zapsign.com.br/qual-tipo-de-certificado-digital-em-nuvem/ |
| Clicksign, certificados aceitos (A1, A3, e-CPF; seis provedores de nuvem) | https://ajuda.clicksign.com/article/935-certificados-digitais-aceitos-pela-clicksign |
| Clicksign, certificado digital em nuvem (redirect ao provedor) | https://ajuda.clicksign.com/article/973-certificado-digital-em-nuvem |
| Clicksign, assinando com certificado digital (exige Web PKI) | https://ajuda.clicksign.com/article/659-assinando-com-certificado-digital |
| Clicksign, portal de desenvolvedores | https://developers.clicksign.com/docs |
| Clicksign, índice completo da documentação | https://developers.clicksign.com/llms.txt |
| Clicksign, tipos de requisito de autenticação | https://developers.clicksign.com/docs/tipos-de-requisitos-de-autenticacao |
| Clicksign, introdução ao Widget Embedded (sandbox por padrão) | https://developers.clicksign.com/docs/introducao-ao-widget-embedded |
| Clicksign, implementando o Widget Embedded (biblioteca JS, eventos) | https://developers.clicksign.com/docs/implementando-o-widget-embedded |
| Clicksign, planos | https://www.clicksign.com/planos |
| D4Sign, assinando com certificado ICP-Brasil (Web PKI, somente Windows) | https://ajuda.d4sign.com.br/assinando-documento-com-certificado-digital-icp-brasil |
| D4Sign, definir certificado ICP-Brasil por signatário via API | https://ajuda.d4sign.com.br/definir-certificado-digital-icp-brasil-para-signat%C3%A1rio-api |
| D4Sign, endpoints de certificado digital | https://docapi.d4sign.com.br/docs/endpoints-4 |
| D4Sign, instalação do EMBED (iframe) | https://docapi.d4sign.com.br/docs/instala%C3%A7%C3%A3o |
| D4Sign, introdução à API (sandbox e ativação por e-mail) | https://ajuda.d4sign.com.br/introdu%C3%A7%C3%A3o-%C3%A0-api-d4sign-leia-antes-de-come%C3%A7ar |
| D4Sign, planos e preços | https://d4sign.com.br/planos-e-precos |
| BRy, acesso à documentação (exige cadastro) | https://atendimento.bry.com.br/kb/pt-br/article/222675/acesso-a-documentacao |
| BRy, assinatura com certificado na nuvem (`kms_type`: BRYKMS, GOVBR, DINAMO) | https://bry-developer.readme.io/reference/assinatura-com-certificado-na-nuvem |
| BRy Cloud | https://cloud.bry.com.br/ |
| Certisign, RemoteID e DesktopID | https://certisign.com.br/wp-content/uploads/2025/01/Como-utilizar-o-certificado-A3-nuvem-RemoteID.pdf |
| Certisign, soluções de assinatura e portal de desenvolvedor | https://assinaturas.certisign.com.br/Home/Solucao |
| Assinei (Aliare), CPR | https://assinei.digital/cpr/ |

### Provedores de certificado em nuvem

| Fonte | URL |
|---|---|
| Valid, integração PSC via API (canal liberado pelo comercial) | https://validcertificadora.com.br/pages/psc-integracao-via-api |
| Valid, VIDaaS | https://validcertificadora.com.br/pages/certificado-em-nuvem |
| Bird ID / VaultID, índice da documentação | https://docs.vaultid.com.br/workspace/llms.txt |
| Bird ID, assinatura via push (`/async-signature`, callback, sessão de 7 e 30 dias) | https://docs.vaultid.com.br/workspace/cloud/api/uso-de-certificado/assinatura-via-push |
| Bird ID, OAuth2 authorization code em sistemas web | https://docs.vaultid.com.br/workspace/cloud/api/autenticacao-de-usuarios/autenticacao-em-sistemas-web |
| Bird ID, QR Code e push | https://docs.vaultid.com.br/workspace/cloud/api/autenticacao-de-usuarios/qr-code-e-push |
| Safeweb, SafeID Integração (preços publicados) | https://www.safeweb.com.br/produtos/safeidintegracao |
| Safeweb, documentação PSC | https://pscsafeweb.safewebpss.com.br/Docs/ |
| Serpro, NeoID/SerproID, token de acesso (OAuth 2.0 com PKCE, validades de sessão) | https://neoid.estaleiro.serpro.gov.br/documentacao/autorizacao/2-token-acesso/ |
| Serpro, NeoID, assinatura digital (`signature_format` RAW e CMS) | https://neoid.estaleiro.serpro.gov.br/manual-integracao/utilizacao-certificado/assinatura-digital/ |
| Serpro, insumos de homologação | https://serproid.serpro.gov.br/manual-integracao/suporte/insumos-homologacao/ |

### B3

| Fonte | URL |
|---|---|
| B3, novo sistema de registro da CPR (tela, arquivo, API) | https://clientes.b3.com.br/w/novo-sistema-de-registro-da-cedula-do-produto-rural-cpr- |
| Layout em Implementação CPR 2.0 (campo `Emissão Eletrônica/Digital`) | https://www.b3.com.br/data/files/47/F4/77/28/C0526710DDCBB167AC094EA8/Layout%20em%20Implementacao%20-%20CPR%202.0_v4.pdf |
