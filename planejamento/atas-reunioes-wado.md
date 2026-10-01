# Atas — Reuniões com Wado Aranha

Versão limpa das notas brutas em `reunião 2 - CLUBE DO CAFÉ - Com Wado Aranha.md`. Mantém o conteúdo, organiza por tema, remove repetição e marca o que já foi superado. Cada item relevante aponta para onde foi aplicado nos documentos principais.

---

## Acordo comercial

- **R$ 300/hora**, não os R$ 350 da proposta inicial.
- Horas fechadas no dia 30, pagamento no dia 5 do mês seguinte.
- Sem descritivo de horas por enquanto: envio no final do mês.
- No futuro, a ideia é migrar para um projeto de escopo fechado.

---

## Reunião 1 — 10 de setembro de 2026, 14h30

Presentes: Gesiel Barros ([souzabarquette.adv.br](http://souzabarquette.adv.br)), Oswaldo Aranha Neto (Wado), Victor. Vinicius não compareceu.

### Escopo original

1. **Registro do contrato.** Precisa ter validade jurídica: certificado digital (modelo DocuSign) ou assinatura com duas testemunhas. Pode integrar com um fornecedor de assinatura digital.
2. **CPR.** Precisa ser depositada ou registrada em uma entidade do Banco Central (B3, CRDC, outra). Funciona como uma conta bancária por participante. O escritório já tem conta na B3 e pode oferecê-la ao clube. O sistema de registro é o "Novo Mercado" da B3. Hoje o processo é manual.
   - O clube emite a CPR e envia as informações à B3; o formato do payload é definido por quem envia (o clube).
   - Existem outras CPRs além de café ("não produtos", outros papéis), mas isso está fora de escopo.
   - **O corretor preenche** o registro. Comprador e vendedor apenas assinam. *(Nota: a reunião 2 revisou este ponto — ver "Quem preenche".)*

### Entrada no clube (versão original, superada)

- Primeiro cadastro, depois análise para aprovação ou recusa.
- A pessoa aprovada pode assumir diferentes papéis — a validar.
- Transação sem corretor é possível; o sistema deve incentivar o uso de corretor, sem exigir.
- O registro é só entre sócios do clube. Ninguém pode estar de fora. *(Reafirmado na reunião 2, ver RN-62.)*
- A avaliar: como funciona o preenchimento de quem compra e quem vende, e vice-versa.

### Lado jurídico

- Em definição o modelo de cobrança do escritório. Vai demorar mais.

### Tarefas definidas

- Planejamento da arquitetura.
- Falar com Gesiel sobre B3: autenticação, cadastro e sandbox.
- Pesquisar plataformas de assinatura digital.

---

## Reunião 2 — 24 de setembro de 2026, 15h30

Presentes: Victor, Wado.

### Correção do time jurídico

O escritório havia analisado o tipo errado de CPR e de contrato, cobrindo operações de barter. **Não é esse o caso.**

- O clube trabalha com **CPR financeira**: um contrato financeiro apenas, fora do escopo do clube.
- O escopo do clube é **CPR física**.
- Isso não atrapalha o projeto — os documentos já partiam de CPR física.
- **Pendência:** o item **Seguro** ficou em aberto. Wado não sabe dizer se é um serviço de seguro oferecido por operação, ou uma apólice do próprio clube para cobrir prejuízo em caso de problema. Fica pendente.

### Nome do clube

**Não usar "sócio"**, porque na prática o clube não é, juridicamente, um clube de sócios. Usar **"membro"**. *(Decidido em 01/10/2026, quando perguntado.)*

### Entrada no clube — proposta de adesão

Muda o modelo inteiro de entrada.

- O termo não é "convite". É **"proposta de adesão"**.
- O **proponente** preenche um formulário explicando quem é.
- No formulário, o proponente indica **2 recomendantes** — pessoas que recomendam sua entrada. Podem ser membros do clube ou não (por exemplo, alguém de renome no mercado, fora do clube).
  - **Pendência:** se um recomendante é externo ao clube, como ele assina a recomendação? É um ponto a resolver com o Wado — a decisão de 24/09 de que "todo signatário é membro" vale para o *registro*; a adesão tem essa exceção a esclarecer.
- Os 2 recomendantes **também assinam** a proposta, pelo mesmo processo de assinatura usado no registro (tipo DocuSign). Eles recebem um e-mail para confirmar a aprovação e assinar.
- Com as 3 assinaturas (proponente + 2 recomendantes), a proposta entra na fila de avaliação do **comitê de admissão**.

### Comitê de admissão

- Hoje tem 3 pessoas: Wado e mais 2. **Configurável** — ainda não decidido se será fixo ou dinâmico.
- Se reúne **uma vez por semana**.
- **Funciona offline, na prática.** O comitê provavelmente não vai operar dentro do sistema. Em vez disso:
  - O **backoffice gera um relatório** (impresso e em tela) com cada pedido de entrada, para a reunião semanal.
  - O comitê decide **fora do sistema**.
  - O comitê pode registrar um **parecer, opcional**, por pedido.
  - O **backoffice materializa a decisão** do comitê no sistema depois da reunião.
  - **Em aberto:** se o comitê precisa de registro formal no sistema (contas, votos) ou se tudo fica só no relatório e na decisão materializada pelo backoffice. Por ora, a segunda opção.

### Processo de avaliação ("onboard" da proposta)

- Pode haver **anexos** na proposta, para apreciação do comitê.
- O comitê pode fazer **pedidos adicionais de dados** durante a análise — ao proponente e aos recomendantes. Não é o caso mais provável, mas precisa existir.
- **Conclusão em um clique**, feito pelo backoffice, aprovando ou não o processo. Dispara um e-mail com o resultado.

### Sem bloqueio automático

- O sistema **não bloqueia automaticamente** uma pessoa que já teve proposta recusada.
- Um proponente pode fazer **nova proposta**, mesmo tendo sido recusado antes.
- O pedido de proposta **não cria usuário**. Fica em uma **base separada**, onde o mesmo CPF pode se repetir em propostas diferentes.
- **Porém**, se já existir um **usuário ativo** com aquele CPF/CNPJ, não pode duplicar — o sistema direciona para o login.

### Onboarding do membro aprovado

- É preciso **explicar como o clube funciona** para quem entra.
- Toda transação no sistema está sob o **contrato padrão do clube**: "Esta transação está sujeita às regras da empresa X (clube)".
- O membro provavelmente precisa **assinar os termos do clube** logo no início do onboarding.
- Se os termos forem **atualizados**, os membros precisam **reassinar**.

### Registro (contrato + CPR)

- Além da CPR, também existe **contrato** e possivelmente outros documentos.
- **Formulário enxuto**, só o essencial:
  - Comprador + vendedor (talvez o corretor).
  - Quantidade.
  - Preço.
  - Prazo de entrega.
  - Ponto/condição de entrega (talvez).
- **Não existe negociação de cláusulas.** É sempre um modelo (template) fixo. A "qualidade", por exemplo, já é fixa no contrato.
- **Quem preenche:** qualquer uma das partes, desde que seja membro, pode preencher envolvendo a outra parte. Corretor pode ou não estar envolvido. *(Revê o que a reunião 1 havia dito sobre "o corretor preenche".)*

### Envelope de assinatura

- O tempo de espera por assinatura precisa ser **curto**: algo entre **5 e 10 minutos**. *(Fixado em 01/10 como variável configurável, começando em 15 minutos — ver abaixo.)*
- A assinatura **não é só do contrato**: pode haver outros documentos (CPR, outros artefatos).
- **Todos os documentos entram em um único envelope**, assinado de uma vez. Quem assina não pode ser chamado para assinar mais nada depois daquele envelope.
- Quem assina precisa **ver tudo antes de assinar** — não é assinatura "às cegas". O "envelope" junta os documentos, não esconde o conteúdo.
- Depois de assinado, **gerar cópia dos documentos para todos os envolvidos**.
- **A avaliar:** partes que precisam de mais de uma assinatura (ex.: empresas com dois signatários/diretores).

### Estados do negócio

- **Cancelado** significa que o negócio não existiu. Não precisa de motivo registrado.
- **Rascunho** talvez nem seja necessário como está hoje — pode virar um "modelo de negociação", com visual amigável mostrando o preenchimento e a forma de negociação, antes de virar registro de verdade.

### Ideia nova: negociação por vídeo

- Adicionar uma sala de **chat/vídeo** (tipo Google Meet) dentro da aplicação, usando uma ferramenta **white-label** (ex.: Whereby), para facilitar a negociação entre as partes.
- Pode virar um **serviço adicional pago** do clube.
- A ideia: as partes negociam e podem até **assinar dentro da própria sala de vídeo**, como se estivessem frente a frente.
- **Motivo da janela curta (5–15 min):** quem está negociando já está, de alguma forma, em contato síncrono — por chamada ou presencialmente. É diferente de um contrato regular enviado para assinar depois.

### Registro no backoffice — falha é risco grave

- **Cancelamento:** não é necessário registrar o motivo. Wado não quer saber de tentativas de registro que não deram certo.
- **Falhar o registro na B3 é um erro grave.** As partes já assumiram o contrato; ele não pode ficar sem efeito por causa de um erro técnico ou da B3.
- O estado **EM_CORREÇÃO é muito danoso** para o clube. Precisa ser muito bem avaliado — investigar melhor como a B3 se comporta.
- **Tarefa:** mapear tudo o que pode dar errado no registro, e já deixar a solução de cada caso mapeada com antecedência.

### Novo escopo: armazéns

- **Local de entrega** da negociação.
- Só existe na **liquidação física** — não em liquidação por diferença, antecipada, ou **washout** (desfaz o contrato).
- Precisa de um **registro interno de árbitros**, para classificar o café.
  - **Árbitro imparcial:** não pode trabalhar para nenhuma empresa envolvida na negociação.
- **Armazéns credenciados**, com fluxo próprio de credenciamento.
- **Fluxo de amostras**, com aprovação de amostras.
- No cadastro do registro, em "local de entrega": escolher **região** e depois um **armazém cadastrado** daquela região.

### Mudanças de registro já feito

Ainda sem resposta, levar ao Wado:

- O que acontece se a qualidade mudar na entrega? Só renegocia o preço?
- É possível alterar um registro já feito, ou só cancelar e refazer? Existe aditivo?
- Como lidar com washout, mudança de local de entrega, e aditivos em geral?
- **Nota de 01/10:** o próprio Wado disse não entender bem esse ponto ainda — washout e liquidação são "possíveis conclusões precipitadas de CPRs físicas". Perguntar com mais calma.

### Serviço do clube fora da plataforma

- **Arbitragem e classificação.** Em caso de litígio, os membros podem escalar para um time do clube fazer uma avaliação formal (laudo). Esse serviço roda **fora da plataforma**.

### Sobre a assinatura do contrato

- **Não é preciso mostrar o contrato inteiro preenchido** a cada operação.
- O modelo é mais parecido com assinar uma ordem de compra de ação em uma corretora: o contrato-mãe já foi aceito quando a pessoa abriu conta no clube.
- No **onboard**, o usuário provavelmente assina os termos completos logo de início. Se os termos mudarem, reassina.

---

## Esclarecimentos de 01/10/2026 (por mensagem, não reunião)

Respostas de Victor às ambiguidades levantadas após a leitura da reunião 2. Aguardando confirmação do Wado em pontos específicos.

| Tema | Esclarecimento | Ainda em aberto |
|---|---|---|
| Recomendante externo | Resolver com o Wado se um recomendante de fora do clube pode assinar a indicação sem ser membro | **Sim, perguntar ao Wado** |
| Parecer do comitê | Opcional. O comitê provavelmente trabalha offline; o backoffice gera relatório (impresso e em tela) para a reunião semanal, e materializa a decisão no sistema depois | — |
| Registro do comitê no sistema | Configurável quanto ao tamanho/composição, mas ainda não se sabe se o comitê precisa de conta própria no sistema. Por ora: relatório do backoffice → decisão offline → backoffice materializa | **Sim, decidir depois** |
| Envelope de documentos | Quem assina vê tudo antes de assinar. "Envelope" significa que todos os documentos incluídos são assinados juntos, sem pedir assinatura de novos documentos depois | — |
| Janela de assinatura | Configurável por variável de ambiente. Começar em **15 minutos**. Ideia: quem negocia já está em contato síncrono (chat, vídeo ou presencial) | — |
| Contrato x CPR | Os dois. O envelope inclui o contrato baseado em modelo, a CPR, e o que mais for necessário | — |
| Washout / liquidação | Wado não tem certeza — podem ser "conclusões precipitadas" de CPRs físicas. **Perguntar ao Wado** | **Sim** |
| Quem preenche o registro | Flexível: qualquer parte que seja membro pode preencher envolvendo a outra. Corretor é opcional | — |
| Origem dos ~45 campos da B3 | Hipótese: boa parte vem do cadastro já capturado no onboarding das partes, e boa parte dos dados de produto já vem fixa nos modelos/termos de uso (nem todo produto, nem toda qualidade são aceitos) | A confirmar quando o formulário de cadastro for fechado |
| Seguro | Não se sabe a que se refere — serviço por operação ou apólice do clube. Fica em aberto | **Sim** |
| Nome do clube/membro | Usar **"membro"** por enquanto | — |
| Prazo de registro na B3 | Objetivo do Wado: registrar em **poucos minutos**. Não registrar é falha grave | — |

### Estratégia de escopo definida em 01/10/2026

Victor optou por ampliar o escopo **do mockup** para cobrir tudo o que o Wado descreveu — inclusive os itens ainda em validação (armazéns, árbitros, amostras, vídeo) — para testar a ideia completa antes de discutir orçamento. Depois disso, cada módulo será estimado e precificado separadamente, e o Wado compõe o MVP dele conforme o orçamento disponível.

---

## Rastreamento — o que mudou em cada documento

| Tema da reunião 2 | Aplicado em |
|---|---|
| CPR física, não financeira | `entendimento-do-projeto.md`, confirmação de escopo |
| Não usar "sócio" | Todos os documentos, termo "membro" |
| Proposta de adesão, recomendantes, comitê | `regras-de-negocio.md` §1, `maquina-de-estados.md`, mockup telas 02, 02c, 12, 12b, 12c, 13 |
| Onboarding e termos versionados | `regras-de-negocio.md` nova seção, mockup tela 03b |
| Envelope de assinatura, múltiplos documentos | `regras-de-negocio.md` §3, `maquina-de-estados.md`, mockup telas 08, 09 |
| Janela de assinatura configurável, 15 min | `regras-de-negocio.md` RN-90/91, `maquina-de-estados.md` |
| Negociação por vídeo (Whereby) | `plano-do-projeto.md` escopo novo, mockup tela 09-video |
| Falha na B3 é erro grave, prevenção antes do envio | `maquina-de-estados.md` rev. 3 |
| Armazéns, árbitros, amostras | `regras-de-negocio.md` nova seção 9, `plano-do-projeto.md`, mockup telas 18–20 |
| Cancelamento sem motivo obrigatório | `regras-de-negocio.md` RN-72 revista |
| Quem preenche o registro | `regras-de-negocio.md` RN-52 revista |
| Estratégia de mockup amplo, preço modular | `plano-do-projeto.md`, `entendimento-do-projeto.md` |

Pendências novas geradas por esta reunião estão listadas em `docs/pendencias.md`, seção 1 (cliente) e seção 2 (escritório).
