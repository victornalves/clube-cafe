# Pendências — Lista Única

21/10/2026 · revisão 6 · junta, sem repetição, as perguntas abertas das seis frentes mais o que as reuniões com o Wado abriram (24/09 e 07/10). Ver `planejamento/atas-reunioes-wado.md`, `planejamento/reunião 4.md` e `consolidacao-rev5.md`.

Organizada por **quem responde**, para cada bloco virar uma reunião ou um e-mail. Dentro de cada bloco, o que trava preço vem primeiro.

Legenda da coluna Trava: **P** preço · **A** arquitetura · **F** fluxo · **O** operação

---

## 1. Cliente — reunião de validação

Usar junto com o roteiro de `mockup/README.md`.

**Decidido em 01/10/2026:** o clube usa o termo **"membro"**, nunca "sócio" — na prática não é juridicamente um clube de sócios.

**Decidido em 07/10/2026** (reunião 4, com Gesiel; esclarecido por Victor em 21/10):

- **Toda assinatura usa certificado digital**, token ou arquivo: proposta de adesão, indicação dos recomendantes, termos iniciais, registros. Vale também para o recomendante de fora do clube. Isso encerra a linha da assinatura por e-mail sem certificado (1.25, 1.26, 2.18, 2.19, 3.14, 3.15). Se e-CNPJ também é aceito ainda está em aberto (1.40).
- O nível de exigência de assinatura fica **parametrizável** por uma ou mais flags (1.42). O padrão é certificado em tudo.
- **O corretor preenche, mas não assina pelo produtor.** Ele pode cadastrar a proposta de adesão do produtor e, na negociação, preencher o registro e mediar. O produtor recebe cada pedido de assinatura por e-mail e assina com o próprio certificado. O clube aprova a adesão normalmente.
- O membro assina os termos iniciais **uma vez só**, no primeiro ingresso. Mudança de termos vira **circular de aviso**, pelo sistema e por e-mail.
- **Intermediário (corretor)** passa a ser parte do registro. Se quem está logado é corretor, o papel vem marcado.
- Usar **"limite de negociação na plataforma"**, nunca "crédito".

### Travam preço ou arquitetura

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 1.1 | Que certificado os membros têm hoje: A1, A3 em token, A3 em nuvem, nenhum? Com proporção aproximada | P A | Panorama 1 |
| 1.2 | **Só se a 1.1 responder "token" e a 1.25 responder "não".** Algum membro assina de Mac ou Linux? Aceita usar Chrome ou Firefox, já que a Lacuna não suporta Safari? | P | Panorama 2; Lacuna §2. Com a D4Sign descartada, só muda teste e suporte, não o fornecedor |
| 1.3 | Quem emite CPR: só pessoa física, ou também cooperativa e empresa? | A | Panorama 4. Clicksign só aceita e-CPF |
| 1.4 | ~~A contraparte precisa ser membro aprovado, ou pode assinar como convidada externa?~~ **Respondida pelo cliente em 24/09/2026: todo signatário é membro. Não há assinatura com parte de fora do clube.** Vale a Hipótese A (RN-62) | — | Regras RN-62/63 |
| 1.5 | Volume esperado de CPRs por mês, e quantas partes por CPR | P | Panorama 8 |
| 1.6 | As CPRs terão garantia real (hipoteca, penhor, alienação fiduciária)? | A | Panorama 3. Muda o nível mínimo de assinatura |
| 1.7 | O clube banca certificado para quem não tem? Aceita assinatura avançada gov.br quando não houver garantia real? | P | Panorama 5, 6 |
| 1.8 | **Aceite informado, por escrito.** O fornecedor de assinatura também guarda uma cópia do contrato: administrador do painel dele vê todos os contratos, fora da nossa auditoria; a exclusão de contrato finalizado é manual; a guarda dura enquanto houver conta. Mitigações: poucos logins, logs de auditoria (plano Avançado), cópia própria baixada na hora, responsável nomeado pelo expurgo. De acordo? | A | Consolidação C-10; Clicksign §7. Se "não", sobra só a Lacuna Rest PKI clássica, que recebe apenas o hash |
| 1.9 | Campos reais do cadastro e do registro. Levar o mapa de campos da B3 | P | Regras RN-05, §3.2; B3 §2 |
| 1.10 | Três papéis de backoffice ou dois | P | Regras RN-37 |
| 1.25 | ~~Aceita assinatura por e-mail, sem certificado, para CPR sem garantia real?~~ **Respondida em 07/10/2026: não.** Toda assinatura usa certificado digital | — | `estudo-assinatura-sem-certificado.md` |
| 1.26 | ~~Haverá CPR com garantia real no início? Se sim: e-mail com fator extra, ICP só nesses casos, ou fora do MVP?~~ **Perde o sentido em 07/10/2026:** certificado vale para qualquer CPR, com ou sem garantia real | — | Idem, §4 |
| 1.40 | **Cadastro de empresa.** O membro é sempre uma pessoa (CPF) que pode estar vinculada a uma ou mais empresas (CNPJ), ou existe cadastro direto de CNPJ como membro? Junto com isso: aceitar **e-CNPJ** na assinatura, ou só o e-CPF do representante? Decide quem é a parte do registro, como se comprova o poder de representação (contrato social, procuração) e quais fornecedores de assinatura servem (a Clicksign só aceita e-CPF) | A P | Reunião 4, 07/10; esclarecimento de 21/10. Liga 1.3 e 1.31 |
| 1.42 | **Nível de exigência de assinatura parametrizável.** Quais níveis existem (certificado ICP-Brasil, avançada, e-mail), a que se aplica cada flag (tipo de documento, tipo de parte, valor, garantia real) e quem pode alterar. Padrão definido: certificado em tudo | A | Reunião 4, 07/10; esclarecimento de 21/10 |
| 1.29 | O item **"Seguro"**, citado na reunião 2 e deixado em aberto pelo próprio Wado: é um serviço de seguro por operação, oferecido a comprador/vendedor, ou uma apólice do clube para cobrir prejuízo em caso de falha? Decide se vira módulo de produto ou fica fora | A | Reunião 2, 24/09 |

### Travam fluxo

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 1.11 | Critérios de entrada no clube e motivos de recusa | F | Regras RN-04, RN-13 a 23 |
| 1.12 | Recusado pode pedir de novo? Com carência, com limite? O que ele recebe como resposta? | F | ~~Regras RN-27, 28, 30~~ **Respondida em 24/09: sem bloqueio automático.** Proponente recusado pode propor de novo a qualquer momento; a proposta nasce em base separada, onde o CPF pode se repetir |
| 1.13 | ~~Quem pode criar um registro? O corretor cria pelas partes? O corretor assina?~~ | — | Regras RN-52, RN-59. **Respondida em 24/09 e 07/10:** qualquer parte membro pode preencher envolvendo a outra. O corretor é opcional, entra como parte "intermediário", pode preencher e mediar, e nunca assina pelo produtor |
| 1.14 | O autor pode descartar rascunho, cancelar durante a coleta de assinaturas, e corrigir depois de uma recusa? | F | Regras L-01, L-02, L-08. **Parcial, 24/09:** cancelar não exige motivo registrado nem aprovação, na leitura de Wado ("não quer saber de tentativa que não efetivou") — confirmar se isso vale também para cancelamento já assinado |
| 1.15 | Falha claramente passageira da B3 pode ser reenviada automaticamente, ou toda falha passa por uma pessoa? | F | Consolidação I-03. **Reforçado em 24/09:** Wado tratou falha de registro como "erro grave" e quer prevenção antes do envio, não só correção depois. Ver 1.35 |
| 1.16 | Cancelar ou reassinar contrato de valor alto exige segunda pessoa aprovando? | F | Mockup 10 |
| 1.17 | Membro pode alterar o próprio cadastro sem aprovação? Membro precisa de segundo fator para entrar? | F | Mockup 2, 3 |
| 1.18 | O membro pode ver quem do backoffice abriu o contrato dele? | F | Mockup 16 |
| 1.27 | **Respondida em parte, 07/10: o recomendante externo também assina com certificado digital.** Resta o fluxo: como ele recebe o pedido e se identifica sem ser membro. Pergunta original: um recomendante da proposta de adesão pode ser alguém de fora do clube ("de renome no mercado"). Como essa pessoa assina a recomendação, se ela não é membro e a Hipótese A (RN-62) diz que todo signatário é membro? É uma exceção só para a adesão, com um fluxo de assinatura próprio? | F | Reunião 2, 24/09. Contradiz RN-62/63 se não for tratado como exceção |
| 1.28 | O comitê de admissão precisa de registro formal no sistema (conta, voto individual), ou o backoffice só gera um relatório para a reunião semanal e depois materializa a decisão tomada offline, com um parecer opcional por pedido? | F | Reunião 2, 24/09 e esclarecimento de 01/10 |
| 1.31 | Uma parte do registro (empresa) pode precisar de mais de um signatário. Quantos signatários no máximo por parte? Todos precisam assinar dentro da mesma janela de 5 a 15 minutos do envelope? | F | Reunião 2, 24/09 |
| 1.35 | O que fazer quando o payload de um registro tem alta chance de falhar na B3 (dado fora do domínio, formato inválido). Existe validação prévia aceitável antes de liberar o envelope para assinatura, para nunca assinar um contrato que vai falhar no registro? | F A | Reunião 2, 24/09. Wado chama falha de registro de "erro grave": o contrato assinado não pode ficar sem efeito por erro técnico |
| 1.36 | Washout, liquidação por diferença e mudança de local de entrega: o próprio Wado não tem certeza de como isso se encaixa numa CPR física só de liquidação física. Esclarecer o que são essas modalidades e se cabem no clube | F | Reunião 2, 24/09; esclarecimento de 01/10. Ver 1.41 |
| 1.41 | **Distrato / washout.** Ideia da reunião 4: um registro paralelo, criado já vinculado ao registro ativo que encerra. Tudo o mais está em aberto e depende do cliente e do escritório: nome, valor a pagar e como é calculado, quem pode propor, quem assina, se passa pelo comitê ou pelo backoffice, e o que acontece com a CPR na B3 (baixa, cancelamento, novo registro). **Ainda em discussão pelo time** | F A | Reunião 4, 07/10; esclarecimento de 21/10 |
| 1.43 | Produtor cadastrado por um corretor: até aceitar os termos iniciais com o próprio certificado, ele fica num estado "pendente" e não pode ser selecionado como parte. Confirma? O convite vai por e-mail com prazo de validade? | F | Reunião 4, 07/10. Proposta nossa para o estado |
| 1.44 | Opção "pagamento já adiantado" no registro: é só informativa, ou muda alguma coisa na liquidação, no documento ou no payload da B3? | F | Reunião 4, 07/10 |
| 1.37 | Critério de credenciamento de armazéns: quem aprova, que documentos o armazém apresenta, prazo de validade do credenciamento | F | Reunião 2, 24/09, escopo novo de armazéns |
| 1.38 | Árbitros classificadores: cadastro é interno ao clube? Como o sistema confirma que um árbitro não tem vínculo com nenhuma das empresas envolvidas na negociação, antes de permiti-lo como classificador daquele registro? | F | Idem |
| 1.39 | Fluxo de amostras: quem coleta a amostra, quem aprova, e o que acontece se a amostra for reprovada (negócio cai, ou há tolerância de reclassificação)? | F | Idem |

### Travam operação

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 1.19 | Quem é avisado quando um registro falha, por qual canal, e em quanto tempo precisa assumir e resolver | O | Regras RN-94 a 96 |
| 1.20 | Prazo de análise de cadastro: dois dias úteis (mockup) ou três (regras)? | O | **Superada em parte, 24/09.** A análise passa a depender da reunião semanal do comitê de admissão, então o prazo realista é de até ~7 dias corridos, não 2 ou 3 dias úteis. Confirmar o número com o cliente |
| 1.21 | Validade do convite, prazo de coleta de assinaturas, lembretes | O | **Superada em parte, 24/09.** A coleta de assinaturas do registro passa a ser uma janela curta e síncrona (5–15 minutos, configurável, default 15 min), não mais dias com lembretes. RN-89 a 92 revistas em `regras-de-negocio.md` |
| 1.22 | Por quanto tempo guardar os registros de auditoria | O | Mockup 14 |
| 1.30 | Prazo de reunião do comitê de admissão: sempre semanal, ou existe análise expressa para caso urgente? | O | Reunião 2, 24/09 |

### Identidade visual, só depois do fluxo aprovado

| # | Pergunta | Origem |
|---|---|---|
| 1.23 | O clube tem nome definitivo e material de marca? | UI 1, 4 |
| 1.24 | O backoffice usa a mesma identidade do membro? | UI 2 |

---

## 2. Escritório sócio

Dois e-mails: um técnico, um jurídico. O técnico destrava trabalho imediatamente.

### E-mail técnico

| # | Pedido | Trava | Origem |
|---|---|---|---|
| 2.1 | Pacote de acesso de **certificação** da B3: `.zip` com certificados, `client_id`, `client_secret` e senha do `.p12` | A | B3 §9.1 |
| 2.2 | Documentação técnica da API de CPR (Swagger ou manual do participante) | P | B3 §9.2 |
| 2.3 | Códigos de conta Cetip (8 dígitos, vão no payload de todo registro): registrador, custodiante, favorecido, agente de pagamento. Custodiante e favorecido são sempre o escritório ou mudam a cada CPR? Os códigos de certificação são os mesmos de produção? | A | B3 §9.3. Fixos viram configuração; variáveis viram campo do formulário |
| 2.4 | Arquivos de domínio vigentes (`Cestas_Produtos`, `Cadastro_Curvas_Moedas_Feeder_Dominios`), ou confirmação de que a API expõe isso por endpoint | P | B3 §9.4. Maior incerteza única da Fase 3, ~8h |
| 2.5 | Contato do RM na B3 e acesso ao SAT | O | B3 §9.8 |
| 2.6 | Quem recebe o aviso de vencimento do certificado da B3 | O | B3 §7 |

### E-mail jurídico

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 2.7 | ~~Conferir no texto consolidado da Lei 8.929/1994: art. 3º, § 4º, I e II, e art. 12~~ **Texto conferido em 12/09 na versão consolidada da Câmara.** Resta ao escritório validar a interpretação | — | `estudo-assinatura-sem-certificado.md` §1 |
| 2.8 | Qual é a data de emissão da CPR na plataforma: envio para assinatura ou última assinatura? | A | Consolidação I-02. Define quando os 30 dias úteis começam |
| 2.9 | As CPRs do clube entram no SCR? | P | B3 §9.5. Liga sete campos obrigatórios |
| 2.10 | O escritório atua como Agente de Registro? Conta própria, de cliente 1 ou de cliente 2? | F | B3 §9.6 |
| 2.11 | Acordo escrito de uso da credencial: responsabilidade, rotação, revogação | — | B3 §9.7 |
| 2.12 | ~~Corretor fica só no documento, sem campo no registro. Confirma?~~ **Revista em 07/10:** o corretor passa a ser parte "intermediário" no registro do clube. Pergunta nova: ele vai para o payload da B3 ou só para o contrato? | F | B3 §2; reunião 4 |
| 2.13 | Critério de "o contrato já produziu efeito", quem decide entre substituição e aditivo, e em quanto tempo | F | Regras L-05, RN-85, RN-97 |
| 2.14 | PAdES ou CAdES destacado? Carimbo do tempo é obrigatório? | P | Lacuna §8, Clicksign §8 |
| 2.15 | Tarifa da B3 por registro de CPR: valor e quem paga | P | Consolidação I-05 |
| 2.16 | LGPD: base legal, retenção, encarregado, e o que fazer com pedido de exclusão de dado que está em CPR registrada | A | Arquitetura, seção LGPD |
| 2.17 | O escritório ou a B3 já usam algum fornecedor de assinatura? | A | Panorama 9 |
| 2.18 | ~~Superada em 07/10: toda assinatura usa certificado.~~ Como Agente de Registro, aceita registrar CPR assinada por e-mail? Que cláusula de forma de assinatura vai no termo de adesão e na CPR? | A | `estudo-assinatura-sem-certificado.md` |
| 2.19 | ~~Superada em 07/10.~~ E-mail mais login com segundo fator na plataforma enquadra como assinatura avançada? | A | Idem, §3.1 |
| 2.20 | Pix ou biometria facial da Clicksign atendem o art. 3º, § 4º, II para garantia real? | A | Idem, §4 |
| 2.21 | A CPR é física e a liquidação sempre física nos casos até agora descritos. Washout e liquidação por diferença/antecipada aparecem citados pelo cliente como modalidades possíveis. São compatíveis com CPR física, ou pressupõem outro instrumento? | F | Reunião 2, 24/09; ver pendência 1.36 |
| 2.22 | O envelope de assinatura reúne CPR, contrato e eventuais outros documentos numa única sessão de assinatura, com janela curta (minutos). Isso é juridicamente equivalente a assinar cada documento separadamente, para efeito de validade da CPR e do contrato? | A | Reunião 2, 24/09 |
| 2.23 | O termo de adesão do clube (contrato-mãe) é reassinado sempre que a versão mudar. Isso precisa de alguma formalidade adicional (aviso prévio, prazo de carência), ou a reassinatura simples basta? | A | Reunião 2, 24/09 |
| 2.25 | Membro como pessoa física vinculada a empresas, ou cadastro direto de CNPJ? Para assinar pela empresa, basta o e-CPF do representante com poderes comprovados, ou é preciso e-CNPJ? Que documento comprova o poder no cadastro | A | Reunião 4, 07/10; ver 1.40 |
| 2.26 | Distrato / washout como registro paralelo vinculado ao original: que forma jurídica tem, como se calcula o valor e o que se faz com a CPR registrada na B3 | F A | Reunião 4, 07/10; ver 1.41 |
| 2.27 | Termo de aceite para gravar, ou não, a reunião na mesa de negociação: texto, base legal (LGPD) e por quanto tempo guardar a gravação | A | Reunião 4, 07/10 |
| 2.24 | Recomendante de uma proposta de adesão que não é membro do clube: que natureza tem a assinatura dele (declaração, carta de recomendação, outra), e isso expõe o clube a algum risco se a recomendação for falsa ou interessada? | F | Reunião 2, 24/09; ver pendência 1.27 |

---

## 3. Clicksign

Só vale enviar enquanto a Clicksign for finalista. Nenhum dos dois exige conta criada.

### Suporte técnico

| # | Pergunta | Origem |
|---|---|---|
| 3.1 | Política de reentrega de webhook: tentativas, intervalo, reenvio manual | Clicksign §12.1 |
| 3.2 | Certificado ICP-Brasil funciona dentro do Widget Embedded? | §12.2 |
| 3.3 | São três provedores de nuvem ou seis? Por escrito | §12.3 |
| 3.4 | O sandbox aceita assinatura com certificado ICP real? | §12.4 |
| 3.5 | Perfil PAdES entregue e política de assinatura aplicada | §12.7 |
| 3.6 | O campo `role` aceita os ~60 papéis ou só os 3 do enum? | §12.8 |
| 3.7 | Existe endpoint REST com as URLs de download do assinado? | §12.10 |
| 3.8 | Polling de envelope é permitido? | §12.11 |
| 3.9 | Existe evento de falha de autenticação por certificado? | §12.13 |
| 3.14 | Como funciona a autenticação da `embedded_signature`, e o que aparece no log do documento? | `estudo-assinatura-sem-certificado.md` |
| 3.15 | Quais combinações de autenticação a Clicksign declara como avançada? | Idem |

### Comercial

| # | Pergunta | Origem |
|---|---|---|
| 3.10 | Preço do plano Avançado para 100 documentos/mês | §12.5 |
| 3.11 | Preço do carimbo do tempo, e se pode ser add-on do Start | §12.5, 12.6 |
| 3.12 | Representante legal com e-CPF resolve CPR emitida por PJ? | §12.9 |
| 3.13 | Prazo e custo para liberar o Widget Embedded em produção | §12.12 |

---

## 4. Lacuna

### Comercial

| # | Pergunta | Origem |
|---|---|---|
| 4.1 | O que conta como uma "transação": uma assinatura, ou preparar e completar contam duas? | Lacuna §12.1. Única variável que estoura a opex |
| 4.2 | A isenção de licença do Web PKI vale para o Rest PKI **Core**? | §12.2 |
| 4.3 | O Rest PKI Core SaaS usa a tabela de preço publicada? | §12.4 |
| 4.4 | Preço do PKI Express | §12.3 |

### Suporte ao desenvolvedor

| # | Pergunta | Origem |
|---|---|---|
| 4.5 | O `POST /api/signature` do Core aceita assinar só com o hash, sem enviar o PDF? | Consolidação I-01. Decide o argumento de segurança |
| 4.6 | Existe reentrega de webhook? | §12.5 |
| 4.7 | Valor padrão de `availableUntil` | §12.6 |
| 4.8 | Suporte a Safari em 2026 | §12.8 |
| 4.9 | Situação da política PAdES ICP-Brasil | §12.9 |

---

## O que fecha a proposta

**Mudança de estratégia em 01/10/2026:** antes de fechar preço, o mockup vai crescer para cobrir **tudo** o que a reunião 2 trouxe — inclusive o que ainda não está validado (armazéns, árbitros, amostras, vídeo). O cliente vê a ideia completa, depois cada bloco é estimado e precificado em separado, e ele compõe o MVP dele conforme o orçamento. A lista abaixo continua valendo para fechar o **núcleo** (adesão, registro, assinatura, B3); os blocos novos (seção "Novo escopo" em `plano-do-projeto.md`) são cotados à parte.

Nem tudo acima precisa estar respondido. Para emitir proposta de escopo fechado do **núcleo**, bastam:

- Cliente: ~~1.4~~, 1.9, 1.10, 1.14, 1.15, ~~1.25~~, 1.27, 1.28, 1.31, 1.35, 1.40, 1.42, 1.43
- Escritório: 2.8, 2.9, 2.12, ~~2.18~~, 2.21, 2.22, 2.25

Para fechar **Fases 2 e 3** com número, somam-se:

- Cliente: 1.1, 1.3, 1.5, 1.6, 1.8
- Escritório: 2.1, 2.2, 2.4, 2.14
- Fornecedor escolhido: o bloco dele inteiro

Para cotar os **blocos novos** (armazéns, árbitros, amostras, vídeo, seguro):

- Cliente: 1.29, 1.36, 1.37, 1.38, 1.39, 1.41
- Escritório: 2.26, 2.27
