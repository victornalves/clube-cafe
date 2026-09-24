# Clube do Café / CRTC — Entendimento do Projeto

**Revisão 4** · 12/09/2026
Fontes: `planejamento/Dossie_Contexto_CRTC.pdf`, kickoffs de setembro, e as seis frentes de estudo. O porquê de cada mudança está em `consolidacao-rev4.md`.

---

## O que mudou da revisão 3

| Tema | Rev. 3 | Rev. 4 |
|---|---|---|
| Nível de assinatura | ICP-Brasil é requisito confirmado | **Em reavaliação.** A lei admite simples, avançada ou qualificada na CPR. Proposta em análise: autenticação por e-mail para CPR sem garantia real. Ver `estudo-assinatura-sem-certificado.md` |
| Prazo legal | Não existia | **30 dias úteis** entre emissão e registro na B3. Vira relógio visível no backoffice |
| Credencial B3 | "Falta pedir a API key" | **Pacote de acesso mTLS**: certificado `.p12`, `client_id`, `client_secret`, senha |
| Assinatura embutida | Nuvem mantém o usuário na tela | **Depende da rota do fornecedor.** Com a Clicksign há saída para o app do provedor |
| Guarda do documento | Só nós | **Nós e, conforme a rota, o fornecedor de assinatura.** Decisão do cliente |
| Formulário | Poucos campos | **~45 campos** exigidos pela B3, seis com lista fechada vinda da B3 |
| Corretor | Parte do registro | **Parte do documento.** A B3 não tem campo para ele |
| Horas | ~332–356h | **~413–539h.** Ver `plano-do-projeto.md` |

---

## Em uma frase

Um clube fechado onde membros aprovados criam, assinam com certificado ICP-Brasil e registram contratos de café na B3 dentro do prazo legal, com um time de backoffice acompanhando e resolvendo o que falhar.

---

## Escopo

### Dentro

1. **Cadastro com homologação.** Solicitação pública, aprovação manual.
2. **Criação de registro.** Produtor e comprador, corretor opcional, e os campos que a CPR física exige na B3.
3. **Geração do documento** a partir de um modelo.
4. **Assinatura ICP-Brasil** via fornecedor externo.
5. **Registro na B3**, sob a conta do escritório sócio, com reconciliação por consulta.
6. **Área do membro.** Conta, listagem, detalhe.
7. **Painel de backoffice.** Aprovação, fila de pendências ordenada por prazo legal, resolução de falhas, auditoria.

### Fora

- Negociação e formação de preço.
- Liquidação financeira.
- Ser registradora.
- Marketing e aquisição.
- **Aditamento de CPR já registrada.** É outra operação na B3, sem estimativa. Proposta para fase futura.
- **Registro no SCR**, se o escritório confirmar que não se aplica.

---

## A decisão de produto mais importante

**O membro vê cinco estados. O backoffice vê a máquina inteira.**

Depois de enviar, o membro vê **Em processamento** até **Registrado**. Entre um e outro, tudo é trabalho do backoffice, com alerta, dono e prazo.

A rev. 4 acrescenta um segundo relógio a essa decisão: o prazo legal. Um registro parado em processamento consome os 30 dias úteis do membro sem que ele saiba. Por isso a fila de pendências ordena por prazo restante.

Detalhamento em `maquina-de-estados.md` (rev. 2).

---

## Arquitetura

Tudo que é crítico é terceirizado. Sobra para nós o cadastro, o formulário, o documento, **o controle de estado**, **o relógio do prazo** e **a proteção dos dados**.

| Peça | Decisão |
|---|---|
| Banco | Relacional comum |
| Auditoria | Duas tabelas append-only: eventos (o que mudou) e acessos (quem viu) |
| Criptografia | Nível de aplicação, seletiva |
| Assinatura | Fornecedor ICP-Brasil atrás de uma interface de uma porta só: `criarSolicitacao`, `obterStatus`, `receberRetorno`, com dois modos de entrega ao signatário, embutido ou redirecionado |
| Finalistas de assinatura | Clicksign e Lacuna. Escolha depende das perguntas 1.1 e 1.3 de `pendencias.md` |
| Registro oficial | API da B3 com OAuth 2.0 + mTLS, conta do escritório sócio |
| Retorno da B3 | **Polling.** Não há webhook para CPR. Job de reconciliação por Número de Controle |
| Retorno da assinatura | Webhook do fornecedor mais job de varredura, porque nenhum dos dois documenta reentrega |
| Configuração B3 | Nove valores por ambiente, um binário. Nenhum no código |
| Armazenamento | Objetos privados, URL assinada curta, download imediato do assinado |
| Papéis | `visitante`, `membro`, e dois ou três de backoffice (pergunta 1.10) |

Detalhamento em `arquitetura-seguranca.md` (rev. 2).

---

## Perguntas que ainda travam o escopo

A lista completa, com 70 itens agrupados por quem responde, está em `pendencias.md`. Estas cinco mudam mais coisa:

| # | Pergunta | O que muda |
|---|---|---|
| 1 | Que certificado os membros têm? | Fornecedor, horas da Fase 2 e a tela de assinatura |
| 2 | Emitente pode ser pessoa jurídica? | Se sim, a Clicksign cai ou fica parcial |
| 3 | A contraparte precisa ser membro? | Um ou dois fluxos de assinatura |
| 4 | Data de emissão é o envio ou a última assinatura? (escritório) | Quando o prazo legal começa a correr |
| 5 | Documento pode ficar guardado no fornecedor? | Qual rota de assinatura é aceitável |

---

## Riscos

### O escopo cresceu de novo
Dossiê: 200h. Plano rev. 2: ~332–356h. Plano rev. 3: ~413–539h. As duas subidas têm a mesma causa: cada leitura mais funda de uma integração revela trabalho que a leitura anterior não enxergava. As faixas só estreitam com a documentação fechada da B3 e as respostas dos fornecedores. **Levar o número e a explicação ao cliente antes da proposta.**

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
| Detalhe de B3, Clicksign, Lacuna, mercado | Os quatro `estudo-*.md` |

---

## Pendência de organização

`planejamento/kickoff-md` continua aqui. É ata do Labeee/FEESC (UFSC), outro cliente. Mover para fora deste repositório.
