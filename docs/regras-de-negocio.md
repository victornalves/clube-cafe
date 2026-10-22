# Regras de Negócio — Clube do Café / CRTC

Frente 4 · 12/09/2026, revisão 5 em 01/10/2026 · deriva de `entendimento-do-projeto.md` (rev. 5), `maquina-de-estados.md`, `arquitetura-seguranca.md`, `plano-do-projeto.md` e da reunião de 24/09/2026 (`planejamento/atas-reunioes-wado.md`)

---

## Como ler este documento

Cada regra tem um identificador estável. `RN-07` continua sendo `RN-07` em tarefa, em teste e em conversa com o cliente. Identificador aposentado não é reciclado.

Toda regra tem origem declarada. Três valores, e só três:

| Origem | Significa | O que fazer com ela |
|---|---|---|
| **Doc** | Está escrita em um dos quatro documentos | Implementar |
| **Proposta** | Derivamos por inferência. Ninguém decidiu ainda | Levar à reunião. Só implementar depois do aceite |
| **[PENDENTE-CLIENTE]** | Decisão do cliente, sem resposta até hoje | Bloqueia estimativa ou bloqueia código. Listada na seção 8 |

Regra marcada `Proposta` ou `[PENDENTE-CLIENTE]` que entrar no código sem aceite vira requisito fantasma, e o cliente paga por ela sem ter pedido.

A coluna "Verificação" existe para que uma pessoa consiga dizer, olhando o sistema, se a regra está cumprida. Regra sem verificação não é regra, é intenção.

---

## 1. Proposta de adesão (era "Entrada no clube")

**Revisão 5, reunião de 24/09/2026 com o cliente.** O modelo de entrada mudou inteiro: não existe mais "convite" nem "solicitação" simples. Existe **proposta de adesão**, com 2 recomendantes que também assinam, avaliada por um **comitê de admissão** que provavelmente funciona fora do sistema. Ver `planejamento/atas-reunioes-wado.md`. As regras RN-08, RN-18 a RN-23 e RN-25 a RN-29 da rev. 4 foram **retiradas** por esta revisão: o modelo de recusa corrigível/bloqueada e de limite de reenvio não existe mais. Os identificadores não são reciclados; ficam marcados abaixo como retirados.

### 1.1 O proponente e os 2 recomendantes

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-01 | O clube é fechado. Nenhuma conta de membro passa a existir sem decisão humana registrada e materializada pelo backoffice. Não há autocadastro, não há aprovação automática | Doc | Criar proposta e confirmar que nenhum login funciona antes do aceite materializado |
| RN-02 | Qualquer visitante pode enviar uma **proposta de adesão** pela página pública. A proposta não cria conta, cria pendência numa base própria, separada da base de membros | Cliente, 24/09/2026 | Enviar proposta e confirmar que ela nasce sem credencial, numa tabela distinta da de membros |
| RN-03 | Visitante não enxerga nenhum registro, nenhuma listagem e nenhum dado de membro. Só as páginas públicas e o formulário de proposta | Doc | Tentar URL direta de registro deslogado. Precisa devolver 404 |
| RN-04 | **[PENDENTE-CLIENTE]** Quem é elegível a membro. Proposta: produtor de café (pessoa física ou jurídica) com CPF ou CNPJ regular e propriedade identificada; comprador pessoa jurídica com CNPJ regular e atividade compatível com comercialização de café; corretor pessoa física ou jurídica indicado por uma das pontas | Proposta | Existe checklist escrito de elegibilidade na tela do comitê/backoffice |
| RN-05 | **[PENDENTE-CLIENTE]** Campos reais da proposta. Nome, e-mail e telefone servem ao mockup. Emissão de CPR exige no mínimo CPF/CNPJ e dados da propriedade. É entregável da Fase 0 | Doc (pendência) / Proposta (conteúdo) | Lista de campos assinada pelo cliente antes do início da Fase 1 |
| RN-06 | A validação automática da proposta reprova formato e nunca aprova mérito. Ela barra CPF/CNPJ com dígito verificador inválido, e-mail malformado e telefone fora do padrão brasileiro. Aprovação continua sendo humana, materializada pelo backoffice | Proposta | Enviar CPF com dígito errado. Formulário recusa na hora, sem criar pendência |
| RN-07 | CPF/CNPJ que já pertence a um **membro ativo** não gera nova proposta: o formulário direciona para o login, sem revelar que a conta existe. **Isso vale só para membro ativo**, não para proposta anterior: a base de propostas pode ter o mesmo CPF/CNPJ repetido em mais de um pedido ao longo do tempo (RN-112) | Cliente, 24/09/2026 | Propor adesão com documento de membro ativo. Sistema redireciona ao login |
| ~~RN-08~~ | ~~Situação de solicitação em cinco valores~~. **Retirada.** Substituída por RN-104, que reflete o fluxo de recomendantes e comitê | — | — |
| RN-101 | Toda proposta de adesão indica exatamente **2 recomendantes**, nomeados pelo proponente. Podem ser membros do clube ou pessoas de fora dele (por exemplo, alguém de renome reconhecido no mercado) | Cliente, 24/09/2026 | Formulário recusa proposta com zero, um ou mais de dois recomendantes |
| RN-102 | **[PENDENTE-CLIENTE, 1.27]** Cada recomendante recebe um e-mail e precisa **assinar a recomendação**, pelo mesmo processo de assinatura usado no registro, antes de a proposta avançar. Falta decidir como assina um recomendante que não é membro, já que RN-62 exige que todo signatário de registro seja membro — essa é uma exceção só para a recomendação, ou o recomendante externo precisa virar membro primeiro? | Cliente, 24/09/2026 (parcial) | Proposta não sai de "aguardando assinatura dos recomendantes" sem as duas assinaturas |
| RN-103 | A proposta só entra na fila do comitê de admissão depois de reunir as **3 assinaturas**: proponente e os 2 recomendantes | Cliente, 24/09/2026 | Tentar avançar com 2 de 3 assinaturas. Sistema recusa |
| RN-104 | A situação de uma proposta é uma de: `PREENCHENDO`, `AGUARDANDO_ASSINATURA_RECOMENDANTES`, `EM_FILA_COMITE`, `EM_DILIGENCIA`, `APROVADA`, `RECUSADA`, `EXPIRADA` | Proposta | Enum implementado, com transição registrada no log de eventos |
| RN-112 | O cadastro de propostas vive em uma base separada da base de membros, e o mesmo CPF/CNPJ pode aparecer em mais de uma proposta ao longo do tempo. Só existe conta de membro depois da aprovação (RN-32) | Cliente, 24/09/2026 | Reenviar proposta com CPF já usado em proposta recusada. Sistema aceita |
| RN-113 | A proposta pode receber **anexos**, para apreciação do comitê de admissão | Cliente, 24/09/2026 | Upload de anexo vinculado à proposta, visível na tela do comitê/backoffice |

### 1.2 O comitê de admissão

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-105 | **[PENDENTE-CLIENTE, 1.28/1.30]** O comitê de admissão hoje tem 3 pessoas (Wado e mais 2) e se reúne **uma vez por semana**. Composição configurável; falta decidir se é fixa ou dinâmica, e se há via expressa para caso urgente | Cliente, 24/09/2026 | Parâmetro de configuração, não constante no código |
| RN-106 | **[PENDENTE-CLIENTE, 1.28]** O comitê provavelmente decide **fora do sistema**, na reunião semanal. O backoffice gera um **relatório** (impresso e em tela) com cada proposta pendente para a reunião, e **materializa a decisão** do comitê no sistema depois, em um clique por proposta | Cliente, 24/09/2026 | Relatório exportável/imprimível existe, e toda decisão materializada registra quem no backoffice a lançou e quando |
| RN-107 | O comitê pode registrar um **parecer em texto, opcional**, por proposta. Parecer vazio não bloqueia a decisão | Cliente, 24/09/2026 | Campo de parecer aceita vazio, e decisão segue possível |
| RN-108 | O comitê pode pedir **diligência**: dados ou documentos adicionais ao proponente e/ou aos recomendantes. A proposta vai para `EM_DILIGENCIA` até a resposta, e volta para `EM_FILA_COMITE` quando respondida | Cliente, 24/09/2026 | Pedido de diligência registrado, com os campos solicitados e a resposta anexada |
| RN-109 | Aprovar ou recusar é um clique do backoffice que **materializa** a decisão do comitê — não é o backoffice decidindo o mérito sozinho. A conclusão dispara um e-mail com o resultado | Cliente, 24/09/2026 | Tela de conclusão exige referência à decisão do comitê (ata, data da reunião) antes de liberar o botão |
| RN-12 | Abrir uma proposta para análise grava linha no log de acessos: quem abriu, qual proposta, quando | Doc | Abrir proposta e conferir a linha no log |

### 1.3 Critérios de aprovação e de recusa

**[PENDENTE-CLIENTE]** A tabela inteira abaixo é proposta nossa. Nenhum critério de aceite de membro foi declarado pelo cliente até hoje. Serve de checklist de apoio ao comitê, materializada pelo backoffice.

| ID | Critério de aprovação (proposta) | Verificação |
|---|---|---|
| RN-13 | Documento (CPF ou CNPJ) regular na Receita Federal, conferido antes da reunião do comitê | Campo de conferência preenchido antes de o botão "aprovar" liberar |
| RN-14 | Identidade confere com o documento apresentado | Idem |
| RN-15 | Atividade declarada compatível com produção, corretagem ou compra de café | Idem |
| RN-16 | Propriedade informada é localizável (município e UF no mínimo), para produtor | Idem |
| RN-17 | Os 2 recomendantes assinaram a recomendação (RN-102, RN-103) | Idem |

~~RN-18 a RN-23~~ (tabela de motivos de recusa com desfecho `RECUSADA_CORRIGIVEL`/`RECUSADA_BLOQUEADA`) **retiradas em 01/10/2026.** O cliente não quer bloqueio automático por motivo de recusa (RN-110). A classificação de motivo continua útil como anotação interna do comitê, sem efeito de bloqueio.

### 1.4 O que acontece com a recusa

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-24 | Recusar exige motivo em texto livre, obrigatório, gravado no log de eventos com autor (o comitê, via backoffice) e horário | Proposta | Tentar recusar sem motivo. Botão inerte |
| ~~RN-25~~ a ~~RN-29~~ | ~~Classificação em corrigível/bloqueada, carência, limite de reenvios, bloqueio de CPF/CNPJ~~. **Retiradas, 24/09/2026.** Substituídas por RN-110 | — | — |
| RN-110 | **Não existe bloqueio automático.** Quem teve proposta recusada pode enviar nova proposta a qualquer momento, sem carência e sem limite de tentativas. Cada proposta é avaliada por conta própria pelo comitê | Cliente, 24/09/2026 | Reenviar proposta logo após recusa. Sistema aceita e cria novo registro na fila |
| RN-30 | **[PENDENTE-CLIENTE]** O que o proponente recusado recebe. Proposta: aviso curto de que a proposta não avançou, com canal de contato. O parecer detalhado do comitê fica interno | Proposta | Comparar o texto do e-mail com o motivo gravado no log. Precisam ser diferentes |
| RN-31 | Proposta recusada nunca é apagada. Fica na base com situação, motivo e autor, para consulta do auditor | Doc (log append-only) | Auditor localiza propostas recusadas dos últimos 12 meses |

### 1.5 Depois da aprovação

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-32 | Aprovar cria a conta de membro e dispara convite por e-mail com link de definição de senha. A conta nasce sem senha e sem sessão | Proposta | Conferir que não existe senha padrão na criação |
| RN-33 | **[PENDENTE-CLIENTE]** Validade do link de convite. Proposta: 72 horas, com reenvio pelo backoffice | Proposta | Usar link expirado e confirmar recusa |
| RN-34 | Proposta aprovada cujo convite expira sem uso vai para `EXPIRADA` e volta para a fila do backoffice, sem exigir nova proposta do visitante | Proposta | Deixar expirar e conferir o retorno à fila |
| RN-35 | **[PENDENTE-CLIENTE]** Existe suspensão e desligamento de membro. Proposta: sim. Membro suspenso não cria registro e não assina. Registros já em curso seguem até o desfecho, porque contrato assinado não desaparece por decisão administrativa | Proposta | Suspender membro com registro em `AGUARDANDO_ASSINATURAS` e confirmar que o registro continua vivo |
| RN-36 | Membro aprovado enxerga apenas os registros em que é parte. Sem exceção, e a verificação acontece na consulta ao banco, nunca na tela | Doc | Teste automatizado por endpoint: membro A pede registro do membro B e recebe 404 |
| RN-114 | No primeiro acesso, o membro aprovado precisa **assinar os termos do clube** (contrato-mãe). Sem essa assinatura, a conta não cria nem assina registro. Ver seção 1.6 | Cliente, 24/09/2026 | Tentar criar registro sem ter assinado os termos vigentes. Sistema bloqueia e redireciona |

### 1.6 Termos do clube e reassinatura

A ideia do cliente é tratar a assinatura de cada registro como quem já abriu conta numa corretora: o contrato-mãe foi aceito na entrada, e cada operação só referencia essa aceitação, sem repetir cláusulas gerais.

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-134 | O membro assina os **termos do clube** (contrato-mãe) uma vez, no onboarding, cobrindo que toda transação futura "está sujeita às regras da empresa do clube". Os termos são versionados | Cliente, 24/09/2026 | Versão do termo assinado gravada na conta do membro, com data e hash do documento |
| RN-135 | Quando os termos mudam de versão, todo membro precisa **reassinar** antes de criar ou assinar novo registro. Registros já em curso sob a versão anterior não são afetados retroativamente | Cliente, 24/09/2026 | Publicar nova versão dos termos. Membro sem reassinatura tenta criar registro e é redirecionado para assinar a nova versão |
| RN-136 | Cada registro, ao ser gerado para assinatura, declara ao signatário que a operação está sujeita aos termos do clube vigentes, sem reexibir o contrato-mãe inteiro | Cliente, 24/09/2026 | Tela de assinatura do registro traz a frase e um link para o termo vigente, não o texto completo |

Diagrama: `diagramas/01-entrada-no-clube.drawio` (desatualizado nesta revisão — precisa redesenho para incluir recomendantes e comitê).

---

## 2. Papéis e permissões

### 2.1 Os papéis

`visitante` e `membro` estão declarados em `entendimento-do-projeto.md`. Os três papéis de backoffice estão em `arquitetura-seguranca.md`, item 5, como **proposta nossa**. O cliente nunca opinou sobre eles.

| Papel | Escopo | Origem |
|---|---|---|
| `visitante` | Páginas públicas e formulário de solicitação | Doc |
| `membro` | Registros em que é parte | Doc |
| `aprovador` | Fila de propostas de adesão. Sem acesso a termo comercial | Proposta |
| `operador` | Fila de pendências e resolução de falha. Vê o necessário para agir | Proposta |
| `auditor` | Leitura de logs. Não altera nada | Proposta |

**O comitê de admissão não é, até onde se sabe, um papel do sistema (RN-105, RN-106).** Ele decide offline, na reunião semanal; o `aprovador` é quem materializa a decisão. **[PENDENTE-CLIENTE, 1.28]** Se o comitê precisar de conta própria para registrar parecer (RN-107) diretamente, em vez de ditar para o backoffice, isso vira um sexto papel, `comite_admissao`, de escopo mínimo: lê a proposta, escreve parecer, não decide sozinho.

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-37 | **[PENDENTE-CLIENTE]** Três papéis de backoffice ou dois. `plano-do-projeto.md` precifica o corte em cerca de 6 horas, e o custo declarado é que quem aprova cadastro passa a enxergar termos comerciais. A decisão é comercial e é do cliente | Doc (a alavanca) / Pendente (a escolha) | Decisão registrada em ata antes do início da Fase 1 |
| RN-38 | Uma pessoa pode acumular papéis de backoffice. O acúmulo é ato explícito de configuração, registrado no log de eventos, nunca herança automática | Proposta | Conceder segundo papel e conferir a linha de log |
| RN-39 | Papel de backoffice exige MFA. Sem segundo fator não há sessão de backoffice | Doc | Tentar login de operador sem MFA. Precisa falhar |
| RN-40 | Papel de membro e papel de backoffice não coexistem na mesma conta. Quem opera o backoffice não é parte de registro nenhum sob a mesma identidade | Proposta | Tentar conceder `operador` a um membro ativo. Sistema recusa |
| RN-41 | Toda permissão é negada por padrão. Acesso existe quando uma regra concede, nunca quando nenhuma regra proíbe | Proposta | Endpoint novo sem regra de autorização responde 403 no teste |

### 2.2 Matriz, configuração de 3 papéis (proposta do `arquitetura-seguranca.md`)

`S` permitido · `N` negado · `P` parcial, com condição na nota

| Ação | visitante | membro | aprovador | operador | auditor |
|---|:--:|:--:|:--:|:--:|:--:|
| Ver páginas públicas | S | S | S | S | S |
| Enviar solicitação de entrada | S | N | N | N | N |
| Ver fila de solicitações | N | N | S | N | N |
| Aprovar ou recusar solicitação | N | N | S | N | N |
| Ver dados cadastrais do solicitante | N | N | S | P¹ | N |
| Desbloquear documento recusado | N | N | S | N | N |
| Criar registro | N | S | N | N | N |
| Editar registro em rascunho | N | P² | N | N | N |
| Enviar registro para assinatura | N | P² | N | N | N |
| Assinar documento | N | P³ | N | N | N |
| Ver registro em que é parte | N | S | N | N | N |
| Ver qualquer registro, com termo comercial | N | N | N | S | N |
| Baixar PDF de registro próprio | N | S | N | N | N |
| Cancelar registro próprio | N | P⁴ | N | N | N |
| Ver fila de pendências | N | N | N | S | N |
| Ver payload e resposta da B3 | N | N | N | S | N |
| Reenviar à B3 (retry) | N | N | N | S | N |
| Corrigir payload e reenviar | N | N | N | S | N |
| Abrir reassinatura | N | N | N | S | N |
| Escolher a variante (substituição ou aditivo) | N | N | N | P⁵ | N |
| Cancelar registro por falha | N | N | N | S | N |
| Ler log de eventos | N | N | N | P⁶ | S |
| Ler log de acessos | N | N | N | N | S |
| Exportar em lote | N | N | N | P⁷ | N |
| Exportar relatório agregado | N | N | N | N | S |
| Gerir usuários de backoffice | N | N | N | N | N |

Notas:
1. O operador vê o cadastro da parte apenas dentro do registro que está resolvendo, e não tem acesso à fila de solicitações.
2. Só em `RASCUNHO`, e só quem criou o registro. Ver seção 4.
3. Só a parte convocada a assinar naquele registro. Ver RN-58 e RN-59.
4. Ver RN-71 e a lacuna L-02 da seção 7.
5. **[PENDENTE-CLIENTE]** A variante é decidida com o jurídico. Ver seção 5.
6. Operador lê o histórico do registro que está resolvendo. Leitura ampla de log é do auditor.
7. Nada em lote sem justificativa registrada, com limite de volume e de frequência, e aprovação de um segundo administrador acima de um volume a definir.

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-42 | Gerir usuários de backoffice não pertence a nenhum dos três papéis operacionais. **[PENDENTE-CLIENTE]** Quem cria e revoga conta de backoffice. Proposta: um papel `administrador_tecnico` fora do produto, exercido pela VSTech na Fase 1 e transferido depois | Proposta | Tentativa de criar usuário por `operador` recebe 403 |
| RN-43 | Auditor lê e nunca escreve. Nenhum endpoint de escrita aceita sessão de auditor | Doc | Varredura automatizada: todo endpoint de escrita recusa o papel `auditor` |
| RN-44 | Log de eventos e log de acessos são append-only para todo papel, inclusive administrativo | Doc | Tentar DELETE e UPDATE no log com a maior permissão existente. Precisa falhar |

### 2.3 Matriz, configuração de 2 papéis (alavanca de corte do `plano-do-projeto.md`)

O corte funde `aprovador` e `operador` em um papel `administrador`. Economiza cerca de 6 horas. A coluna que muda está marcada.

| Ação | visitante | membro | administrador | auditor | Muda? |
|---|:--:|:--:|:--:|:--:|:--:|
| Ver páginas públicas | S | S | S | S | |
| Enviar solicitação de entrada | S | N | N | N | |
| Ver fila de solicitações | N | N | S | N | |
| Aprovar ou recusar solicitação | N | N | S | N | |
| Ver dados cadastrais do solicitante | N | N | S | N | |
| Desbloquear documento recusado | N | N | S | N | |
| Criar registro | N | S | N | N | |
| Editar registro em rascunho | N | P² | N | N | |
| Enviar registro para assinatura | N | P² | N | N | |
| Assinar documento | N | P³ | N | N | |
| Ver registro em que é parte | N | S | N | N | |
| **Ver qualquer registro, com termo comercial** | N | N | **S** | N | **sim** |
| Baixar PDF de registro próprio | N | S | N | N | |
| Cancelar registro próprio | N | P⁴ | N | N | |
| Ver fila de pendências | N | N | S | N | |
| **Ver payload e resposta da B3** | N | N | **S** | N | **sim** |
| Reenviar à B3 (retry) | N | N | S | N | |
| Corrigir payload e reenviar | N | N | S | N | |
| Abrir reassinatura | N | N | S | N | |
| Escolher a variante | N | N | P⁵ | N | |
| Cancelar registro por falha | N | N | S | N | |
| Ler log de eventos | N | N | P⁶ | S | |
| Ler log de acessos | N | N | N | S | |
| Exportar em lote | N | N | P⁷ | N | |
| Exportar relatório agregado | N | N | N | S | |

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-45 | Na configuração de 2 papéis, quem aprova cadastro passa a enxergar preço, volume e contraparte de qualquer registro. O cliente precisa aceitar esse efeito por escrito, porque ele contraria o princípio declarado em `arquitetura-seguranca.md` item 5 | Doc | Aceite em ata, nominal |
| RN-46 | A separação `auditor` sobrevive aos dois cenários. Quem lê log de acesso nunca é quem opera | Proposta | Matriz implementada mantém a coluna auditor idêntica nos dois cenários |
| RN-47 | O papel é dado de configuração e a matriz é dado, nunca condicional espalhada no código. Sair de 3 para 2 papéis (ou voltar) é mudança de configuração | Proposta | Alternar a configuração em homologação sem alterar código |

Diagrama: `diagramas/05-matriz-papeis.drawio`.

---

## 3. Regras do registro

### 3.1 Partes

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-48 | Um registro tem 2 ou 3 partes. O corretor é a terceira e é opcional | Doc | Formulário barra 1 parte e barra 4 partes |
| RN-49 | Os papéis de parte são três: `produtor` (emitente e vendedor), `comprador` e `corretor` | Proposta | Enum implementado |
| RN-50 | Exatamente um produtor e exatamente um comprador por registro. Zero ou um corretor | Proposta | Tentar dois compradores. Formulário recusa |
| RN-51 | A mesma pessoa ou empresa não ocupa dois papéis no mesmo registro. Produtor e comprador precisam ter CPF/CNPJ diferentes | Proposta | Informar o mesmo CNPJ nas duas pontas. Formulário recusa |
| RN-52 | Qualquer membro que seja parte do negócio pode **criar o registro, envolvendo a outra parte**. Não é exclusividade do corretor nem de quem "começou" a negociação; o corretor cria pelas partes só quando estiver presente no negócio | Cliente, 24/09/2026 | Produtor cria registro informando o comprador (e vice-versa). Os dois fluxos funcionam |
| RN-53 | Quem cria o registro é gravado como autor e não muda. Autoria não é transferível | Proposta | Campo imutável após criação |
| RN-115 | **[PENDENTE-CLIENTE, 1.31]** Uma parte pode exigir **mais de um signatário** (por exemplo, empresa com dois diretores com poderes conjuntos). Falta decidir o máximo de signatários por parte e se todos precisam concluir dentro da mesma janela do envelope (RN-118) | Cliente, 24/09/2026 | Modelo de dados separa "parte" de "signatário": uma parte tem 1..N signatários convocados |

### 3.2 Campos e validações

> **Ajuste rev. 4:** a tabela abaixo foi escrita antes do estudo da B3 e está superada por `estudo-api-b3.md` §2, que lista os ~45 campos do layout de CPR física. Diferenças principais: produto, classe/tipo, safra, unidade, acondicionamento e finalidade são listas fechadas vindas da B3; bebida e peneira não existem no registro, só no documento; corretor não tem campo no registro; faltam situação, produção, imóvel, tipo de garantia, forma de pagamento, indexador e o bloco SCR. A tabela definitiva sai da reunião com o cliente (pendência 1.9).

**[PENDENTE-CLIENTE]** A lista definitiva de campos é entregável da Fase 0 e depende do mapeamento do payload da B3 (frente 3) e da validação do escritório sócio. A tabela abaixo é proposta de partida, construída a partir do que uma CPR física de café exige. Cada campo com validação é trabalho, e o número de campos move a estimativa da Fase 1.

| Bloco | Campo | Obrigatório | Validação proposta |
|---|---|:--:|---|
| Emitente | Nome ou razão social | sim | Texto, 3 a 120 caracteres |
| Emitente | CPF ou CNPJ | sim | Dígito verificador. Precisa bater com o cadastro do membro |
| Emitente | Endereço completo | sim | CEP válido, UF na lista |
| Emitente | Inscrição estadual | não | Formato por UF |
| Propriedade | Nome da fazenda | sim | Texto |
| Propriedade | Município e UF | sim | Lista oficial IBGE |
| Propriedade | Matrícula do imóvel e cartório | **[PENDENTE-CLIENTE]** | Texto. Obrigatoriedade depende do que a B3 exige |
| Propriedade | Número do CAR | **[PENDENTE-CLIENTE]** | Formato do CAR. Idem |
| Produto | Espécie | sim | Arábica ou conilon |
| Produto | Tipo, peneira e bebida | **[PENDENTE-CLIENTE]** | Listas fechadas, a fechar com o cliente |
| Produto | Safra | sim | Ano ou intervalo de safra, nunca passado distante |
| Quantidade | Sacas de 60 kg | sim | Inteiro maior que zero |
| Preço | Valor por saca | sim | Decimal maior que zero, em reais |
| Preço | Valor total | sim | Calculado. Precisa bater com preço por saca vezes quantidade |
| Entrega | Modalidade de liquidação | sim | Lista fechada: **física** (entrega em armazém credenciado), por diferença, antecipada, ou washout. **[PENDENTE-CLIENTE, 1.36/2.21]** Compatibilidade de cada modalidade com CPR física a confirmar com o escritório |
| Entrega | Região e armazém | condicional | Obrigatório só na modalidade física: primeiro escolhe a **região**, depois um **armazém credenciado** daquela região (RN-131, seção 9) |
| Entrega | Local | sim | Município e UF, ou armazém identificado |
| Entrega | Data | sim | Data futura em relação à emissão |
| Cédula | Data de emissão | sim | Data do envio para assinatura, não digitada |
| Cédula | Vencimento | sim | Igual ou posterior à data de entrega |
| Garantia | Tipo e descrição | não | Lista fechada quando preenchida |
| Comprador | Razão social e CNPJ | sim | Dígito verificador |
| Corretor | Nome e CPF/CNPJ | condicional | Obrigatório quando houver corretor |
| Corretor | Percentual de corretagem | condicional | Entre 0 e 100, duas casas |

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-54 | Valor total é calculado pelo sistema e nunca digitado. Divergência entre preço por saca, quantidade e total é impossível por construção | Proposta | Campo somente leitura na tela e recalculado no servidor |
| RN-55 | Data de entrega posterior à data de emissão, e vencimento igual ou posterior à entrega. As três datas são validadas em conjunto no envio para assinatura | Proposta | Informar entrega anterior à emissão. Envio recusado |
| RN-56 | Toda validação roda no servidor. Validação de tela é conveniência e nunca é a barreira | Proposta | Enviar payload inválido direto ao endpoint. Precisa ser recusado |
| RN-57 | Quantidade é sempre em sacas de 60 kg. A unidade aparece na tela junto do campo, em texto | Proposta | Rótulo presente na tela |

### 3.3 Quem assina

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-58 | Produtor e comprador assinam sempre. A assinatura é ICP-Brasil, sem alternativa. **Ajuste rev. 4:** é requisito do cliente, não da lei, que admite outros níveis na CPR (consolidação C-01). Pendência 1.7 pergunta se o cliente aceita assinatura avançada quando não houver garantia real | Doc | Documento com uma assinatura só não avança para `ASSINADO` |
| RN-59 | **[PENDENTE-CLIENTE]** O corretor assina. Proposta: assina como interveniente quando estiver no registro, porque o percentual de corretagem está no documento | Proposta | Fluxo de assinatura convoca três signatários quando houver corretor |
| RN-60 | O registro só sai de `AGUARDANDO_ASSINATURAS` para `ASSINADO` quando todas as assinaturas convocadas estiverem concluídas. Assinatura parcial mantém o estado | Doc | Assinar com uma parte e conferir que o estado não muda |
| RN-61 | Uma parte recusar assinatura leva o registro a `RECUSADO_POR_PARTE` e de lá a `CANCELADO`. Recusa exige motivo | Doc (transição) / Proposta (motivo) | Recusar e conferir os dois estados no log |

### 3.3.1 O envelope de assinatura

**Mudança de modelo em 24/09/2026.** O registro não assina só o contrato: assina um **envelope** com todos os documentos daquela operação de uma vez (contrato a partir do modelo, CPR, e o que mais for necessário). Isso substitui a ideia anterior de lembretes e dias de prazo (RN-89 a 92 revistas abaixo) por uma janela curta e síncrona.

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-116 | O envio para assinatura gera um **envelope único** com todos os documentos do registro (contrato, CPR e demais artefatos exigidos). As partes assinam o envelope inteiro de uma vez, não documento por documento | Cliente, 24/09/2026 | Assinar o envelope grava uma assinatura por signatário cobrindo todos os documentos nele, no mesmo evento |
| RN-117 | Depois que o envelope é aberto para assinatura, **nenhuma parte é convocada a assinar documento adicional** daquele registro. Se faltar algo, o envelope é refeito (reassinatura, seção 5), não complementado | Cliente, 24/09/2026 | Tentar anexar documento a um envelope já em `AGUARDANDO_ASSINATURAS`. Sistema recusa |
| RN-118 | Quem assina **visualiza o conteúdo completo de todos os documentos do envelope antes de confirmar**. "Envelope" é o nome do agrupamento, não uma assinatura às cegas — ao contrário da ideia de assinatura de contrato futuro cogitada antes, o cliente confirmou que quer exibição integral | Cliente, 24/09/2026 | Tela de assinatura oferece abrir/rolar cada documento do envelope antes de liberar o botão de confirmar |
| RN-119 | A **janela de coleta de assinaturas do envelope é curta e configurável** por variável de ambiente, nunca constante no código. Valor inicial: **15 minutos**. A lógica: quem está negociando já está em contato síncrono (chat, vídeo ou presencial), diferente de um contrato comum enviado para assinar depois | Cliente, 01/10/2026 | Alterar a variável em homologação sem deploy. Envelope de teste expira no tempo configurado |
| RN-120 | **[PENDENTE-CLIENTE]** O que acontece quando a janela do envelope expira sem todas as assinaturas. Proposta: segue o princípio de RN-91 — nada cancela sozinho. O registro sai do fluxo síncrono, avisa autor e partes, e vira pendência para reabrir uma nova janela ou cancelar manualmente | Proposta | Deixar expirar um envelope de teste. Registro não vai para `CANCELADO` sem ação humana |
| RN-121 | O clube pode oferecer uma **Mesa de Negociação** (videochamada whitelabel, serviço de terceiro) que o autor do registro ativa logo na criação, antes de preencher objeto e valor — não só perto da assinatura. É opcional em qualquer etapa e nunca é condição para avançar | Cliente, 24/09/2026; UX revista 01/10 | Criar um registro sem nunca ativar a Mesa, do início ao registro na B3. Fluxo completo funciona |
| RN-122 | A **Mesa de Negociação** (nome de produto definido em 01/10/2026, antes chamada de "sala de negociação por vídeo") facilita a negociação síncrona desde o início do preenchimento até a assinatura. É um recurso opcional, não condição para nenhuma etapa | Cliente, 24/09/2026 | Botão "Iniciar Mesa de Negociação" disponível e opcional logo após a etapa de partes |
| RN-137 | Quando a Mesa está ativa, os campos do formulário em preenchimento (objeto, valor, entrega, revisão) ficam visíveis a todos os participantes da chamada, em tempo real — como uma tela compartilhada | Cliente, 24/09/2026 | Tela de objeto e de revisão têm uma variante "com Mesa", lado a lado com os participantes |
| RN-138 | Com a Mesa ativa, a videochamada permanece aberta **até o envelope ser assinado por todas as partes** — a lógica é de mesa de negociação do começo ao fim, não de sala que fecha antes da assinatura | Cliente, 24/09/2026 | Câmeras seguem ligadas na tela de assinatura (não só na de preenchimento), até o último signatário concluir |
| RN-139 | **[PENDENTE-CLIENTE]** Quem efetivamente edita os campos compartilhados durante a Mesa: qualquer participante, ou só quem está "com a palavra"? Como o sistema resolve edição simultânea? Detalhe que depende do fornecedor de vídeo escolhido (Fase 4) | Pendente | Comportamento definido e testado antes de contratar o fornecedor |

### 3.4 Signatário precisa ser membro do clube

**Decidido pelo cliente em 24/09/2026: Hipótese A.** Todas as partes que assinam são membros. Não há assinatura com parte de fora do clube (pendência 1.4). A tabela fica como registro do que foi pesado.

| | Hipótese A: todo signatário é membro | Hipótese B: signatário externo permitido |
|---|---|---|
| Regra | RN-62 | RN-63 |
| Quem pode ser parte | Só quem já passou pela aprovação do clube | Uma das pontas pode ser convidado externo de um registro específico |
| Cadastro | O criador não consegue montar o registro enquanto a contraparte não for aprovada | Contraparte informada no formulário, sem passar pela fila |
| Identidade | Garantida pela aprovação manual, e o CPF/CNPJ do documento bate com o cadastro | Garantida apenas pelo certificado ICP-Brasil da assinatura |
| Acesso do externo | Não se aplica | Link nominal de acesso único ao documento daquele registro, expirável. Sem conta, sem listagem, sem histórico |
| Efeito no isolamento | Nenhum. O controle da seção 1 do `arquitetura-seguranca.md` cobre tudo | Cria uma segunda porta de acesso ao documento. Precisa de teste de autorização próprio |
| Efeito no cronograma | Menor. Um só fluxo de assinatura | Maior. Dois fluxos, duas telas de assinatura, escopo extra na Fase 1 e na Fase 2 |
| Efeito comercial | Trava negócio com comprador que ainda não entrou no clube | Permite fechar negócio com contraparte de fora do clube |
| Risco | Atrito de adoção | Signatário sem vínculo com o clube, e responsabilidade menos clara perante o escritório sócio |

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-62 | Todo signatário é membro aprovado. O CPF/CNPJ da parte no documento precisa ser igual ao do cadastro aprovado | Cliente, 24/09/2026 | Tentar informar como parte um CPF sem cadastro aprovado. Formulário recusa |
| RN-63 | ~~Hipótese B. Signatário externo assina por convite nominal~~ **Descartada** em 24/09/2026. Não existe signatário externo, nem link de acesso para quem não é membro | Cliente, 24/09/2026 | Não há rota de acesso ao documento sem conta de membro |
| RN-64 | Independente da hipótese, o CPF/CNPJ do certificado usado na assinatura precisa bater com o da parte no documento. Certificado de terceiro não assina no lugar de ninguém | Proposta | Assinar com certificado de CPF diferente. Precisa falhar e gerar alerta |

---

## 4. Edição, cancelamento e imutabilidade

O corte é a primeira assinatura. Antes dela, o membro manda no conteúdo. Depois dela, o conteúdo está congelado e só o jurídico reabre, por reassinatura.

### 4.1 Estado por estado

| Estado interno | Membro vê | Edita conteúdo? | Cancela? | Quem age | O que está congelado |
|---|---|---|---|---|---|
| `RASCUNHO` | Rascunho | Sim, tudo | Lacuna L-01 | Membro autor | Nada |
| `AGUARDANDO_ASSINATURAS` | Aguardando assinaturas | Não | Lacuna L-02 | Partes assinam | Documento e todos os campos |
| `RECUSADO_POR_PARTE` | Cancelado | Não | Transição automática para `CANCELADO` | Sistema | Tudo |
| `ASSINADO` | Em processamento | Não | Não | Sistema envia | Documento, campos e assinaturas |
| `ENVIANDO_B3` | Em processamento | Não | Não | Sistema | Idem, mais o payload em trânsito |
| `FALHA_B3` | Em processamento | Não | Não. Precisa passar por `EM_CORRECAO` | Alerta dispara | Idem |
| `EM_CORRECAO` | Em processamento | Payload sim, documento não | Sim, com motivo | Operador | Documento e assinaturas |
| `AGUARDANDO_REASSINATURA` | Aguardando assinaturas | Não | Lacuna L-03 | Partes assinam o documento novo | Documento novo |
| `REGISTRADO` | Registrado | Não | Não | Ninguém | Tudo, para sempre |
| `CANCELADO` | Cancelado | Não | Não | Ninguém | Tudo |

### 4.2 As regras

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-65 | Em `RASCUNHO` o autor edita qualquer campo, quantas vezes quiser. Nenhuma outra parte enxerga o rascunho | Doc | Comprador tenta abrir o rascunho do produtor e recebe 404 |
| RN-66 | Enviar para assinatura congela o conteúdo. De `AGUARDANDO_ASSINATURAS` em diante nenhum campo do contrato muda por edição | Doc | Endpoint de edição responde 409 em qualquer estado diferente de `RASCUNHO` |
| RN-67 | O documento é gerado no envio para assinatura, a partir do modelo, e o arquivo gerado não é regravado. Documento novo exige assinatura nova | Doc | Hash do PDF conferido antes e depois da assinatura |
| RN-68 | Corrigir payload altera o envio à B3 e nunca altera o documento assinado. O documento continua válido | Doc | Comparar hash do PDF antes e depois de uma correção de payload. Precisa ser idêntico |
| RN-69 | `REGISTRADO` é terminal. Nenhuma ação de nenhum papel muda um registro registrado. Correção posterior é contrato novo | Doc | Tentar qualquer escrita em registro `REGISTRADO`. Precisa falhar com a maior permissão existente |
| RN-70 | `CANCELADO` é terminal. Cancelado não volta a rascunho e não é reaproveitado | Doc | Idem |
| RN-71 | O autor cancela livremente enquanto nenhuma parte tiver assinado o envelope (lacuna L-02, agora resolvida). Depois da primeira assinatura, cancelar vira pedido ao backoffice | Cliente, 24/09/2026 (confirma a proposta da rev. 4) | Cancelar rascunho ou envelope sem assinatura nenhuma. Ação imediata, sem passar pelo backoffice |
| RN-72 | **Revista, 24/09/2026.** Cancelar um registro em que o negócio simplesmente **não existiu** (nenhuma parte assinou, ou a janela do envelope expirou sem conclusão) **não exige motivo em texto**: "cancelado" já significa isso. Motivo em texto continua obrigatório para cancelar um registro que teve ao menos uma assinatura, ou que passou por `FALHA_B3` — aí alguém decidiu interromper algo que já estava em curso, e isso precisa de justificativa | Cliente, 24/09/2026 | Cancelar rascunho sem assinatura: botão não pede motivo. Cancelar registro com assinatura: motivo obrigatório |
| RN-73 | Toda transição de estado grava registro, estado anterior, estado novo, autor, horário, motivo e, quando houver, o diff | Doc | Log de eventos com os sete campos preenchidos em toda linha |
| RN-74 | Transição sem autor identificado não existe. Ação automática grava o sistema como autor, com o gatilho que a originou | Doc | Nenhuma linha do log com autor nulo |
| RN-75 | Registro cancelado ou recusado nunca é apagado. Arquiva com motivo e continua consultável pelo auditor | Doc | Auditor localiza registros cancelados do período |

Diagramas: `diagramas/02-ciclo-registro-membro.drawio` e `diagramas/03-ciclo-registro-backoffice.drawio`.

---

## 5. Reassinatura: substituição ou aditivo

A tabela do `maquina-de-estados.md` diz o que cada variante é. Falta o critério de decisão operacional, que é o que o operador precisa na tela às 15h de uma terça.

### 5.1 Quando cada uma

| ID | Situação | Variante | Origem | Verificação |
|---|---|---|---|---|
| RN-76 | Erro material no documento, e o contrato ainda não produziu efeito entre as partes. Nada foi entregue, nada foi pago, nada foi dado em garantia | Substituição | Doc | Checklist de efeito na tela, respondido antes de liberar o botão |
| RN-77 | O contrato é válido e as partes querem manter o negócio. O ajuste é pontual: prazo de entrega, local, quantidade dentro do combinado | Aditivo | Doc | Idem |
| RN-78 | Dúvida sobre ter produzido efeito | Consulta ao jurídico antes de escolher | Proposta | Tela oferece "encaminhar ao jurídico" como terceira saída, sem obrigar escolha imediata |

### 5.2 O critério em uma pergunta

O caminho de resolução já é separado por uma pergunta: o dado errado aparece no documento assinado. A escolha da variante é separada por outra:

> **O contrato já produziu efeito entre as partes?**
> Não produziu: substituição. O documento anterior morre.
> Produziu: aditivo. O documento anterior sobrevive e o novo aponta para ele.

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-79 | Na substituição, o documento anterior é cancelado e arquivado com motivo. Ele continua existindo na base e no histórico, e deixa de ter validade | Doc | Documento anterior marcado como cancelado, acessível ao auditor, não acessível como contrato vigente |
| RN-80 | No aditivo, o documento anterior é preservado e o novo documento referencia o anterior por identificador | Doc | Campo de referência preenchido e navegável dos dois lados |
| RN-81 | A reassinatura convoca as mesmas partes do documento original. Trocar de parte é registro novo, nunca reassinatura | Proposta | Tentar alterar CPF/CNPJ de parte dentro de uma reassinatura. Precisa falhar |
| RN-82 | Toda reassinatura grava: documento antes, documento depois, variante escolhida, quem decidiu, justificativa | Doc | Cinco campos preenchidos no log de eventos |
| RN-83 | Uma reassinatura volta o registro para `AGUARDANDO_REASSINATURA`, e o membro volta a ver "aguardando assinaturas", porque a ação é dele | Doc | Tela do membro muda de "em processamento" para "aguardando assinaturas" |

### 5.3 Quem decide

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-84 | O operador abre a reassinatura. A variante é decidida caso a caso com o jurídico | Doc | Campo de decisor preenchido com nome, nunca com o papel genérico |
| RN-85 | **[PENDENTE-CLIENTE]** Quem tem a palavra final na variante. Proposta: o escritório sócio decide, o operador executa. O operador nunca escolhe sozinho entre substituição e aditivo, porque a escolha errada tem efeito jurídico | Proposta | A tela exige identificar quem do jurídico decidiu |
| RN-86 | **[PENDENTE-CLIENTE]** Prazo de resposta do jurídico para a decisão de variante. Sem prazo, o registro fica em `EM_CORRECAO` indefinidamente e o membro fica vendo "em processamento" sem fim | Pendente | SLA acordado e medido no painel |
| RN-87 | **[PENDENTE-CLIENTE]** O membro precisa concordar com a variante antes da reassinatura, ou apenas assina o documento novo. Proposta: comunicação obrigatória com a justificativa em linguagem comum antes da convocação para assinar | Proposta | Aviso enviado e registrado antes da mudança de estado |

Diagrama: `diagramas/04-caminhos-de-resolucao.drawio`.

---

## 6. Prazos

Nenhum prazo está definido nos quatro documentos. `maquina-de-estados.md` declara explicitamente que canal, responsável e prazo de resposta do alerta de falha ficam a definir com o cliente. Os demais nem foram levantados.

Sem prazo, três coisas quebram: a fila cresce sem limite, o membro não sabe o que esperar, e não existe número para medir o backoffice.

| ID | Prazo | Situação | Proposta de partida | Verificação |
|---|---|---|---|---|
| RN-88 | **[PENDENTE-CLIENTE]** Análise de proposta de adesão. **Revisto, 24/09/2026:** como a decisão depende da reunião semanal do comitê, o prazo realista é de até ~7 dias corridos, não os 2–3 dias úteis da rev. 4 | Parcialmente respondido | Contador visível na fila, e relatório de propostas fora do prazo |
| RN-89 | **[PENDENTE-CLIENTE]** Validade do link de convite após aprovação | Nunca discutido | 72 horas, com reenvio pelo backoffice | Link expirado recusa acesso |
| ~~RN-90~~ | ~~Expiração da coleta de assinaturas em dias corridos~~. **Retirada, 24/09/2026.** O modelo de "dias de coleta com lembretes" não existe mais. Substituída por RN-119 (janela do envelope, minutos, configurável) | — | — |
| ~~RN-91~~ | ~~O que acontece no fim do prazo de assinatura~~. **Retirada.** Substituída por RN-120 | — | — |
| ~~RN-92~~ | ~~Lembretes durante a coleta de assinaturas~~. **Retirada.** Uma janela de minutos não comporta lembretes por e-mail; o aviso, se houver, é dentro da própria tela do envelope, em tempo real | — | — |
| RN-93 | **Ajuste rev. 4:** 30 dias úteis entre emissão e registro (Lei 8.929/1994, art. 12, a conferir pelo escritório). Continua pendente **quando a emissão acontece**, no envio ou na última assinatura (pendência 2.8). Texto original: Janela regulatória entre a assinatura e o registro na B3. Existe prazo legal para registrar uma CPR depois de emitida. Confirmar com o escritório sócio, e não presumir. Esse prazo define quanto tempo o backoffice tem para resolver uma falha antes de o problema virar jurídico | Pendente | Prazo escrito, confirmado pelo escritório, e alarme no painel antes do vencimento |
| RN-94 | **[PENDENTE-CLIENTE]** Prazo de resposta ao alerta de `FALHA_B3`. Declarado como pendência no `maquina-de-estados.md`. Proposta: 4 horas úteis para assumir (`EM_CORRECAO`), 2 dias úteis para resolver | Doc (a pendência) / Proposta (o número) | Dois contadores na fila de pendências, um de assunção e um de resolução |
| RN-95 | **[PENDENTE-CLIENTE]** Canal do alerta e responsável nominal. Declarado como pendência no `maquina-de-estados.md`. Sem dono, o alerta vira ruído | Doc (a pendência) | Alerta chega a uma pessoa identificada, e a fila mostra quem assumiu |
| RN-96 | **[PENDENTE-CLIENTE]** Tempo máximo em `EM_CORRECAO` antes de escalonamento | Nunca discutido | 2 dias úteis, depois escalona para o responsável pelo backoffice | Marcação de escalonamento na fila |
| RN-97 | **[PENDENTE-CLIENTE]** Prazo do jurídico para decidir a variante de reassinatura | Nunca discutido | 1 dia útil | Contador próprio |
| RN-98 | **[PENDENTE-CLIENTE]** Prazo de assinatura na reassinatura | Nunca discutido | Igual ao da primeira coleta | Mesmo parâmetro |
| RN-99 | Nenhum prazo é constante no código. Todos são configuração, porque o cliente vai mudar de ideia depois de ver o primeiro mês de operação | Proposta | Alterar cada prazo em homologação sem deploy |
| RN-100 | Todo vencimento de prazo gera linha no log de eventos com o sistema como autor e o gatilho identificado | Doc | Log de vencimentos consultável |

---

## 7. Contradições com os docs existentes

Nenhuma contradição direta entre afirmações dos quatro documentos. O que existe são lacunas na máquina de estados, encontradas ao desenhá-la, e duas divergências de vocabulário. Os diagramas 2, 3 e 4 desenham o que está documentado, sem consertar nada em silêncio.

### 7.1 Lacunas da máquina de estados

| ID | Lacuna | Onde | Efeito prático |
|---|---|---|---|
| L-01 | Não existe transição para descartar um `RASCUNHO`. A camada 2 tem uma única saída de `RASCUNHO`, que é `AGUARDANDO_ASSINATURAS` | `maquina-de-estados.md`, camada 2 | Rascunho abandonado fica na base para sempre, e o membro não tem botão para se livrar dele |
| ~~L-02~~ | ~~Não existe transição de `AGUARDANDO_ASSINATURAS` para `CANCELADO` por decisão do membro~~. **Fechada, 24/09/2026.** RN-71 confirma a transição: o autor cancela livremente enquanto nenhuma parte tiver assinado o envelope | `maquina-de-estados.md`, camada 2 | — |
| L-03 | Não existe saída de `AGUARDANDO_REASSINATURA` que não seja `ENVIANDO_B3`. Se uma parte recusar a reassinatura, o registro não tem para onde ir | `maquina-de-estados.md`, camada 2 | Registro travado, e a fila de pendências não fecha |
| L-04 | O aditivo não tem caminho a partir de `REGISTRADO`. A reassinatura só existe saindo de `EM_CORRECAO`, ou seja, antes do registro na B3. Mas a definição do aditivo fala em "contrato válido, ajuste pontual", que é a situação típica de um contrato já registrado | `maquina-de-estados.md`, seção 3 | A variante mais provável na operação real não tem transição desenhada |
| L-05 | Tensão na própria definição da substituição. Ela pressupõe "contrato ainda não produziu efeito", e a reassinatura só acontece depois de falha na B3, ou seja, com o contrato assinado pelas partes e ainda não registrado. O momento em que o efeito começa precisa vir do jurídico | `maquina-de-estados.md`, seção 3 | Operador sem critério objetivo para escolher a variante |
| L-06 | A camada 1 não tem seta de `EM PROCESSAMENTO` de volta para `AGUARDANDO ASSINATURAS`, e a tabela de mapeamento exige que ela exista: `AGUARDANDO_REASSINATURA` aparece ao membro como "Aguardando assinaturas", vindo de estados que aparecem como "Em processamento" | `maquina-de-estados.md`, camada 1 contra tabela de mapeamento | O diagrama do membro, como está, não representa o único caso em que o estado anda para trás na tela dele |
| L-07 | `FALHA_B3` não tem retry automático. O único caminho é `EM_CORRECAO`, que exige um humano assumir. Timeout de rede passa a consumir pessoa | `maquina-de-estados.md`, camada 2 | Coerente com o human in the loop declarado, e caro em falha transitória. Vale confirmar se é intencional |
| L-08 | `RECUSADO_POR_PARTE` não tem caminho de reparo. A única saída é `CANCELADO`. Uma parte que recusa por causa de um erro de digitação mata o registro, e o trabalho inteiro é refeito do zero | `maquina-de-estados.md`, camada 2 | Atrito alto em erro pequeno |

### 7.2 Divergências de vocabulário

| ID | Divergência | Onde |
|---|---|---|
| L-09 | `entendimento-do-projeto.md` fala em "aprovação manual por admin". `arquitetura-seguranca.md` item 5 diz que um único papel `admin` é grosso demais e propõe três. O primeiro documento usa um termo que o segundo já descartou | Escopo, item 1, contra Controles, item 5 |
| L-10 | Três documentos dão três contagens de papel de backoffice: "papéis separados" (entendimento), três nominais (arquitetura), dois como alavanca de corte (plano). Nenhum dos três foi aceito pelo cliente | Os três |

---

## 8. Decisões pendentes do cliente

Pauta de reunião. Cada item bloqueia código, estimativa ou as duas coisas. Ordenado por quanto trava.

### 8.1 Travam a estimativa da Fase 1

| # | Decisão | Regra | Impacto |
|---|---|---|---|
| 1 | Campos reais do cadastro | RN-05 | Cada campo com validação é trabalho. Entregável da Fase 0 |
| 2 | Campos reais do registro, e quais são obrigatórios | RN-54 e seção 3.2 | Move o bloco de formulário multi-etapa (24h estimadas) |
| 3 | ~~Signatário precisa ser membro. Hipótese A ou B~~ **Decidido: Hipótese A** (24/09/2026) | RN-62, RN-63 | Um só fluxo de assinatura |
| 4 | Três papéis de backoffice ou dois | RN-37, RN-45 | Cerca de 6 horas. O custo do corte é aprovador enxergando termo comercial |
| 5 | Obrigatoriedade de matrícula do imóvel e CAR | Seção 3.2 | Depende do payload da B3, frente 3 |

### 8.2 Travam o fluxo

| # | Decisão | Regra |
|---|---|---|
| 6 | Critérios de elegibilidade a membro | RN-04, RN-13 a RN-17 |
| 7 | ~~Motivos de recusa, e quais bloqueiam em definitivo~~ **Superada.** Não há bloqueio definitivo (RN-110) | — |
| 8 | ~~Recusado pode reenviar. Com carência, com limite, ou sem nenhum dos dois~~ **Decidido, 24/09: sem carência, sem limite** | RN-110 |
| 9 | O que o proponente recusado recebe como resposta | RN-30 |
| 10 | Uma aprovação de proposta basta, ou exige todo o comitê | RN-105, RN-109 |
| 11 | Existe suspensão e desligamento de membro | RN-35 |
| 12 | ~~Quem pode criar registro, e se o corretor cria pelas partes~~ **Decidido, 24/09: qualquer parte membro, corretor opcional** | RN-52 |
| 13 | Corretor assina o documento | RN-59 |
| 14 | ~~Membro pode cancelar registro em coleta de assinaturas~~ **Decidido, 24/09: sim, livremente, antes da primeira assinatura** | RN-71, RN-72 |
| 15 | Quem decide a variante de reassinatura, e se o membro precisa concordar | RN-85, RN-87 |
| 16 | Quem cria e revoga conta de backoffice | RN-42 |
| 33 | Recomendante externo (não membro): como assina a recomendação de adesão | RN-102 |
| 34 | Comitê de admissão precisa de registro formal no sistema, ou só relatório + decisão materializada | RN-105, RN-106 |
| 35 | Máximo de signatários por parte, e se todos cabem na mesma janela do envelope | RN-115 |
| 36 | O que fazer quando a janela do envelope expira sem todas as assinaturas | RN-120 |
| 37 | Compatibilidade de washout e liquidação por diferença/antecipada com CPR física | Seção 3.2, pendência 1.36/2.21 |
| 38 | Critério de credenciamento de armazéns, cadastro de árbitros e fluxo de amostras | Seção 9 |

### 8.3 Travam a operação

| # | Decisão | Regra |
|---|---|---|
| 17 | Canal do alerta de falha na B3 e responsável nominal | RN-95 |
| 18 | Prazo para assumir e para resolver uma falha na B3 | RN-94 |
| 19 | Janela regulatória para registrar a CPR depois de assinada. Confirmar com o escritório sócio | RN-93 |
| 20 | Prazo de análise de proposta de adesão, dado o ritmo semanal do comitê | RN-88 |
| 23 | Tempo máximo em correção antes de escalonar | RN-96 |
| 24 | Prazo do jurídico para decidir a variante | RN-97 |
| 39 | Validação preventiva do payload da B3 antes de liberar o envelope para assinatura (não assinar o que vai falhar) | Pendência 1.35, `maquina-de-estados.md` rev. 3 |

### 8.4 Decisões de desenho, para aprovar junto

| # | Item | Lacuna |
|---|---|---|
| 25 | Transição de descarte de rascunho | L-01 |
| ~~26~~ | ~~Transição de cancelamento pelo membro durante a coleta de assinaturas~~ | **Fechada, L-02.** RN-71 confirma a transição |
| 27 | Saída de `AGUARDANDO_REASSINATURA` quando uma parte recusa | L-03 |
| 28 | Caminho do aditivo a partir de `REGISTRADO` | L-04 |
| 29 | Definição jurídica de "contrato produziu efeito" | L-05 |
| 30 | Seta de retorno na camada do membro, de "em processamento" para "aguardando assinaturas" | L-06 |
| 31 | Retry automático em falha transitória, antes de consumir pessoa | L-07 |
| 32 | Caminho de reparo após recusa de assinatura por erro pequeno | L-08 |

---

## 9. Armazéns, árbitros e amostras (escopo novo, reunião de 24/09/2026)

Nenhuma regra aqui tem origem **Doc**: tudo nasceu da reunião 2 e está sob avaliação, para o mockup mostrar a ideia completa antes de ser precificado em separado (ver `plano-do-projeto.md`, "Novo escopo").

### 9.1 Modalidade de liquidação

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-123 | Todo registro declara uma **modalidade de liquidação**: física (com entrega em armazém), por diferença, antecipada, ou washout (desfaz o contrato). **[PENDENTE-CLIENTE, 1.36/2.21]** Falta confirmar com o escritório se as três últimas cabem numa CPR física | Cliente, 24/09/2026 | Campo obrigatório no formulário de registro, com as quatro opções |
| RN-124 | Armazém e árbitro só se aplicam na modalidade **física**. Nas demais, esses campos não aparecem | Cliente, 24/09/2026 | Trocar a modalidade para "por diferença" e confirmar que o bloco de armazém some do formulário |

### 9.2 Armazéns credenciados

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-125 | Existe um cadastro de **armazéns credenciados**, agrupados por região | Cliente, 24/09/2026 | Listagem de armazéns filtrável por região |
| RN-126 | **[PENDENTE-CLIENTE, 1.37]** Fluxo de credenciamento de armazém: quem solicita, que documentos apresenta, quem aprova, se tem validade e renovação | Pendente | Fluxo desenhado e aprovado antes de codificar |
| RN-127 | No formulário de registro, o local de entrega em modalidade física é escolhido em duas etapas: primeiro a **região**, depois um **armazém credenciado** daquela região | Cliente, 24/09/2026 | Trocar a região e confirmar que a lista de armazéns muda |

### 9.3 Árbitros classificadores

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-128 | Existe um cadastro interno de **árbitros classificadores**, mantido pelo clube | Cliente, 24/09/2026 | Listagem de árbitros no backoffice |
| RN-129 | Um árbitro é **imparcial**: não pode classificar café de um registro em que ele tenha vínculo com o produtor, o comprador ou o corretor envolvidos | Cliente, 24/09/2026 | Tentar designar árbitro com vínculo declarado a uma das partes. Sistema recusa e registra a tentativa |
| RN-130 | **[PENDENTE-CLIENTE, 1.38]** Como o sistema conhece o vínculo de um árbitro com uma empresa, para aplicar RN-129: declaração do próprio árbitro, cadastro de vínculos, ou checagem manual pelo backoffice antes de cada designação | Pendente | Campo de vínculos do árbitro existe e é consultado na designação |

### 9.4 Amostras

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-131 | Existe um **fluxo de amostras**: coleta e aprovação, associado ao registro em liquidação física | Cliente, 24/09/2026 | Registro em modalidade física ganha uma etapa de amostra, com situação própria |
| RN-132 | **[PENDENTE-CLIENTE, 1.39]** Quem coleta a amostra, quem aprova, e o que acontece se for reprovada: o negócio cai, ou existe tolerância de reclassificação (ligando de volta à pergunta de RN-77, "o que muda se a qualidade na entrega for diferente") | Pendente | Fluxo desenhado e aprovado antes de codificar |

### 9.5 Serviço de arbitragem em litígio

| ID | Regra | Origem | Verificação |
|---|---|---|---|
| RN-133 | Em caso de litígio entre as partes, existe um serviço de **arbitragem e classificação do clube** (laudo), mas ele roda **fora da plataforma**. O sistema, no máximo, registra que um litígio foi aberto e referencia o registro, sem workflow próprio no MVP | Cliente, 24/09/2026 | Fora de escopo de código; confirmar que não há fluxo de laudo dentro do sistema |

---

## Diagramas

Um único arquivo, `diagramas/Clube do Café - Diagramas - rev 2.drawio`, com uma página (aba) por diagrama. O PDF anterior está em `diagramas/legado/`.

| Página | O que mostra |
|---|---|
| A1 · Entrada no clube | Proposta de adesão: candidato, 2 proponentes, cartas anexadas pelo candidato, assinatura das 3 partes, comitê, termos |
| A2 · Limites do membro e análise de risco | Definição e ajuste do limite, soma da exposição, aviso urgente à cúpula, agente que libera ou nega |
| B1 · Visão geral do registro | Ponta a ponta, por raia (membro, sistema, backoffice) |
| B2 · Negociação, com e sem Mesa | O novo estado entre rascunho e aguardando assinaturas |
| B3 · Estados do registro (membro) | Camada 1, seis estados |
| B4 · Estados do registro (backoffice) | Camada 2, máquina completa |
| B5 · Resolução de falhas | Os quatro caminhos. Só ganhou uma nota: registro retido por limite ou risco não passa por aqui |
| C1 · Liquidação e entrega | Armazém, amostra, troca de partes, seguro, e o que acontece depois de Registrado |
| C2 · Armazém: dois papéis | Armazém geral (entrega) x armazém membro (negociante), em aberto |
| D1 · Matriz de papéis | Permissões em 2 e 3 papéis, agora com o papel **cúpula** (análise de risco) e as ações novas: proposta, termos, negociação, limite, retenção, armazém, árbitro e amostra |

Abrir arrastando para `app.diagrams.net` ou no VS Code com a extensão Draw.io Integration.
