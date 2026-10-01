# Clube do Café / CRTC — Entendimento do Projeto

**Revisão 5** · 01/10/2026
Fontes: `planejamento/Dossie_Contexto_CRTC.pdf`, kickoffs de setembro, as seis frentes de estudo, e a reunião de validação de 24/09/2026 com o cliente (`planejamento/atas-reunioes-wado.md`). O porquê de cada mudança está em `consolidacao-rev5.md`.

**Termo:** o clube usa "membro", nunca "sócio" — decidido pelo cliente em 01/10/2026.

---

## O que mudou da revisão 4

A reunião de 24/09/2026 trouxe mais mudança de modelo do que qualquer rodada anterior. Resumo; detalhe em `consolidacao-rev5.md`.

| Tema | Rev. 4 | Rev. 5 |
|---|---|---|
| Entrada no clube | Solicitação simples, aprovação de um `aprovador` | **Proposta de adesão**: proponente + 2 recomendantes assinam, avaliada por um **comitê de admissão** que se reúne semanalmente, provavelmente fora do sistema |
| Bloqueio de recusado | Recusa corrigível/bloqueada, com carência e limite de reenvio | **Sem bloqueio automático.** Proponente recusado pode propor de novo a qualquer momento |
| Assinatura do registro | Um documento, dias de coleta, lembretes | **Envelope único** (contrato + CPR + outros), janela curta e configurável, 15 minutos de partida |
| Onboarding | Não existia | Membro assina os **termos do clube** (contrato-mãe) na entrada, e reassina quando a versão mudar |
| Falha no registro na B3 | Corrigir depois, com `EM_CORRECAO` e quatro caminhos | Mesmos quatro caminhos, mas com uma **pré-validação antes da assinatura**, porque o cliente trata falha de registro como "erro grave" |
| Escopo | Cadastro, registro, assinatura, B3, backoffice | Mesmo núcleo, mais **armazéns credenciados, árbitros classificadores, fluxo de amostras e negociação por vídeo**, para validar no mockup antes de precificar |
| Estratégia de validação | Mockup do fluxo essencial, para aprovar antes de orçar | Mockup **ampliado para cobrir tudo**, inclusive o que ainda não está maduro, para o cliente ver a ideia inteira; cada bloco é precificado depois, em separado |

---

## Em uma frase

Um clube fechado onde membros aprovados propõem adesão com recomendação de pares, criam e assinam em envelope único contratos de café validados preventivamente, registram na B3 dentro do prazo legal, com um time de backoffice acompanhando e resolvendo o que falhar.

---

## Escopo

### Dentro — núcleo

1. **Proposta de adesão.** Proponente + 2 recomendantes assinam; comitê de admissão avalia (possivelmente fora do sistema); backoffice materializa a decisão.
2. **Onboarding com termos do clube.** Assinatura do contrato-mãe, versionado, com reassinatura obrigatória quando a versão mudar.
3. **Criação de registro.** Qualquer parte membro pode preencher envolvendo a outra; corretor opcional.
4. **Geração do envelope** (contrato a partir de modelo, CPR e demais documentos) com pré-validação contra os domínios/formatos da B3 antes de abrir para assinatura.
5. **Assinatura em envelope único**, janela curta e configurável.
6. **Registro na B3**, sob a conta do escritório sócio, com reconciliação por consulta.
7. **Área do membro.** Conta, listagem, detalhe.
8. **Painel de backoffice.** Fila de propostas (com relatório para o comitê), fila de pendências ordenada por prazo legal, resolução de falhas, auditoria.

### Dentro — escopo novo, para validar no mockup antes de precificar

9. **Modalidade de liquidação** no registro: física (com armazém), por diferença, antecipada, washout — compatibilidade com CPR física ainda a confirmar com o escritório.
10. **Armazéns credenciados**, por região, com fluxo de credenciamento.
11. **Árbitros classificadores**, com checagem de imparcialidade (sem vínculo com as partes do registro).
12. **Fluxo de amostras**, coleta e aprovação.
13. **Mesa de Negociação** (videochamada white-label, tipo Whereby), recurso opcional desde a criação do registro até a assinatura — nome de produto definido em 01/10/2026.

Cada item 9–13 vira um módulo cotado em separado; o cliente compõe o MVP dele conforme o orçamento (ver `plano-do-projeto.md`).

### Fora

- Negociação e formação de preço.
- Liquidação financeira.
- Ser registradora.
- Marketing e aquisição.
- **Aditamento de CPR já registrada.** É outra operação na B3, sem estimativa. Proposta para fase futura.
- **Registro no SCR**, se o escritório confirmar que não se aplica.
- **Arbitragem de litígio (laudo).** Roda fora da plataforma, como serviço do clube.
- **Seguro.** Natureza ainda não definida pelo cliente (por operação ou apólice do clube) — fica fora até ser esclarecido.

---

## A decisão de produto mais importante

**O membro vê cinco estados. O backoffice vê a máquina inteira.**

Depois de enviar, o membro vê **Em processamento** até **Registrado**. Entre um e outro, tudo é trabalho do backoffice, com alerta, dono e prazo.

A rev. 4 acrescentou um segundo relógio a essa decisão: o prazo legal. A rev. 5 acrescenta uma terceira ideia: **prevenir é melhor que corrigir**. O cliente chama falha de registro de "erro grave" — o contrato já foi assinado e não pode ficar sem efeito por um problema técnico nosso. Por isso entra uma pré-validação do payload antes de abrir a janela de assinatura, para que o erro mais comum (dado fora do domínio da B3) nunca chegue a um documento assinado.

Detalhamento em `maquina-de-estados.md` (rev. 3).

---

## Arquitetura

Tudo que é crítico é terceirizado. Sobra para nós o cadastro, o formulário, o documento, **o controle de estado**, **o relógio do prazo** e **a proteção dos dados**.

| Peça | Decisão |
|---|---|
| Banco | Relacional comum |
| Auditoria | Duas tabelas append-only: eventos (o que mudou) e acessos (quem viu) |
| Criptografia | Nível de aplicação, seletiva |
| Assinatura | Fornecedor ICP-Brasil atrás de uma interface de uma porta só: `criarSolicitacao`, `obterStatus`, `receberRetorno`, com dois modos de entrega ao signatário, embutido ou redirecionado. Agora cobre **envelope com múltiplos documentos** numa única sessão (RN-116) |
| Janela de assinatura | **Configurável por variável de ambiente**, não constante no código. 15 minutos de partida (RN-119) |
| Finalistas de assinatura | Clicksign e Lacuna. Escolha depende das perguntas 1.1 e 1.3 de `pendencias.md` |
| Pré-validação da B3 | Nova, rev. 5. Confere o payload contra domínios e formatos conhecidos **antes** de abrir a janela de assinatura, sem chamar a B3 (pendência 1.35) |
| Registro oficial | API da B3 com OAuth 2.0 + mTLS, conta do escritório sócio |
| Retorno da B3 | **Polling.** Não há webhook para CPR. Job de reconciliação por Número de Controle |
| Retorno da assinatura | Webhook do fornecedor mais job de varredura, porque nenhum dos dois documenta reentrega |
| Configuração B3 | Nove valores por ambiente, um binário. Nenhum no código |
| Armazenamento | Objetos privados, URL assinada curta, download imediato do assinado |
| Papéis | `visitante`, `membro`, dois ou três de backoffice (pergunta 1.10), e possivelmente `comite_admissao` se o comitê precisar de conta própria (pergunta 1.28) |
| Vídeo de negociação | Integração white-label (tipo Whereby), opcional, escopo novo a precificar |

Detalhamento em `arquitetura-seguranca.md` (rev. 2 — ainda não revisada para o escopo novo).

---

## Perguntas que ainda travam o escopo

A lista completa está em `pendencias.md`. Estas seis mudam mais coisa:

| # | Pergunta | O que muda |
|---|---|---|
| 1 | Que certificado os membros têm? | Fornecedor, horas da Fase 2 e a tela de assinatura |
| 2 | Emitente pode ser pessoa jurídica? | Se sim, a Clicksign cai ou fica parcial |
| 3 | ~~A contraparte precisa ser membro?~~ **Sim, respondida em 24/09/2026.** Todas as partes são membros | Um só fluxo de assinatura |
| 4 | Data de emissão é o envio ou a última assinatura? (escritório) | Quando o prazo legal começa a correr |
| 5 | Documento pode ficar guardado no fornecedor? | Qual rota de assinatura é aceitável |
| 6 | Comitê de admissão precisa de conta própria no sistema, ou só relatório + decisão materializada pelo backoffice? | Se existe um sexto papel (`comite_admissao`) ou não |

---

## Riscos

### O escopo cresceu de novo, e desta vez por mudança de modelo, não só de profundidade
Dossiê: 200h. Plano rev. 2: ~332–356h. Plano rev. 3: ~413–539h. As duas primeiras subidas vieram de ler mais fundo as mesmas integrações. A reunião de 24/09 é diferente: trouxe **processo novo** (proposta de adesão com comitê), **conceito novo** (envelope de assinatura) e **domínio novo** (armazéns, árbitros, amostras, vídeo). **Estratégia adotada em 01/10:** ampliar o mockup para mostrar tudo, sem comprometer preço do escopo novo ainda — cada bloco é cotado depois, em separado, e o cliente escolhe o que cabe no orçamento dele. Ver `plano-do-projeto.md`.

### Operamos sob a credencial de um terceiro
A conta B3 é do escritório. Perante a B3, a responsabilidade pela veracidade do dado é do Agente de Registro, conforme o Manual de Normas de CDA, WA e CPR. O pacote de acesso "é o seu passaporte e identificador na B3", nas palavras da própria B3. Acordo escrito, responsável pelo vencimento do certificado, e configuração trocável.

### O prazo legal transforma atraso operacional em problema jurídico
CPR não registrada em 30 dias úteis perde validade e eficácia. Uma falha que fica dois dias sem dono já é um sétimo do prazo. Alerta sem responsável nomeado não serve.

### O documento pode sair da nossa infraestrutura
Clicksign e a sessão do Rest PKI Core recebem o PDF inteiro e o guardam em painel com controle de acesso deles, fora da nossa tabela de acessos. Quem tem login de administrador lá vê todos os contratos. Isso precisa ser aceito pelo cliente ou evitado pela rota, não descoberto depois.

### O adversário mais provável continua sendo um membro
Compradores e produtores concorrem. Isolamento por registro testado vem antes de qualquer outro controle.

### Clientes não são tech-savvy
A tela de assinatura é onde isso mais pesa: instalar componente, sair para o app do certificado, voltar. Cada passo precisa de uma frase em português comum.

---

## Ativo que temos e vale usar

O escritório de advocacia é sócio. Vinte das 70 pendências são jurídicas ou da B3 e saem de dois e-mails para ele. É o bloco mais barato de destravar.

---

## Mapa de documentos

| Assunto | Fonte da verdade |
|---|---|
| O que é o sistema e o que está em aberto | Este documento |
| Estados, transições, prazos, alertas | `maquina-de-estados.md` |
| Regras com identificador (RN-xx) | `regras-de-negocio.md` |
| Segurança e proteção de dados | `arquitetura-seguranca.md` |
| Fases, horas, fornecedor, próximos passos | `plano-do-projeto.md` |
| Perguntas abertas, por destinatário | `pendencias.md` |
| Por que a rev. 4 mudou o que mudou | `consolidacao-rev4.md` |
| Por que a rev. 5 mudou o que mudou | `consolidacao-rev5.md` |
| O que foi dito nas reuniões com o cliente, organizado por tema | `planejamento/atas-reunioes-wado.md` |
| Detalhe de B3, Clicksign, Lacuna, mercado | Os quatro `estudo-*.md` |

---

## Pendência de organização

`planejamento/kickoff-md.md` continua aqui. É ata do Labeee/FEESC (UFSC), outro cliente. Mover para fora deste repositório.
