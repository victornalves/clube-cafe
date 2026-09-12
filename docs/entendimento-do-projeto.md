# Clube do Café / CRTC — Entendimento do Projeto

**Revisão 3** · 12/09/2026
Fontes: `planejamento/Dossie_Contexto_CRTC.pdf` + kickoffs de setembro.

---

## O que mudou da revisão 2

| Tema | Antes | Agora |
|---|---|---|
| Homologação B3 | Risco de cronograma, prazo desconhecido | **Resolvida.** Usaremos a conta do escritório de advocacia sócio. Falta só pedir a API key de homologação |
| ICP-Brasil | Em aberto | **Confirmado.** É requisito, e determina a escolha do parceiro de assinatura |
| Falha no registro | Buraco no fluxo | **Resolvido por design.** Estado simplificado para o membro, máquina completa no backoffice, com human in the loop |
| Segurança | Não mencionada | **Requisito de primeira classe.** Criptografia em nível de aplicação, auditoria de acesso, controle de exportação |

Os dois riscos maiores da rev. 2 morreram. Entraram dois novos, ambos menores e gerenciáveis.

---

## Em uma frase

Um clube fechado onde membros aprovados criam, assinam com certificado ICP-Brasil e registram contratos de café na B3, com um time de backoffice acompanhando e resolvendo o que falhar.

---

## Escopo

### Dentro

1. **Cadastro com homologação.** Solicitação pública, aprovação manual por admin.
2. **Criação de registro.** Partes (2 ou 3, corretor opcional), objeto, data, valor.
3. **Geração do documento** a partir de modelo.
4. **Assinatura ICP-Brasil** via parceiro externo.
5. **Registro na B3**, sob a conta do escritório sócio.
6. **Área do membro.** Conta, listagem, detalhe.
7. **Painel de backoffice.** Aprovação, acompanhamento, resolução de falhas, auditoria.

### Fora

- Negociação e formação de preço.
- Liquidação financeira.
- Ser registradora. Quem registra é a B3.
- Marketing e aquisição. Clube de convidados não tem funil.

---

## A decisão de produto mais importante

**O membro não vê a máquina de estados. O backoffice vê.**

Para o membro, depois que ele envia, o registro fica **EM PROCESSAMENTO** até virar **REGISTRADO**. Tudo que acontece entre esses dois pontos é problema nosso, não dele.

Para o backoffice, cada etapa é visível, cada falha gera alerta, e existe uma pessoa responsável por resolver.

Isso resolve duas coisas de uma vez: o cliente não-técnico não precisa entender rejeição de payload, e nós ganhamos liberdade para corrigir sem expor processo interno.

Detalhamento em `maquina-de-estados.md`.

---

## Arquitetura

Tudo que é crítico é terceirizado. Sobra para nós o cadastro, o formulário, o documento, **o controle de estado** e **a proteção dos dados**.

| Peça | Decisão |
|---|---|
| Banco | Relacional comum, sem extensões exóticas |
| Auditoria de escrita | Tabela append-only de eventos |
| Auditoria de leitura | Tabela de acessos: quem viu o dado de quem |
| Criptografia | Nível de aplicação, seletiva |
| Assinatura | Parceiro ICP-Brasil, a definir |
| Registro oficial | API B3, conta do escritório sócio |
| Armazenamento | Objetos privados, URL assinada com expiração curta |
| Papéis | `visitante`, `membro`, e papéis separados no backoffice |

Detalhamento em `arquitetura-seguranca.md`.

---

## Perguntas que ainda travam o escopo

### 1. Que tipo de certificado ICP-Brasil os membros têm?
Isso define a experiência inteira de assinatura:

| Tipo | Experiência possível |
|---|---|
| A1 ou A3 **em nuvem** (Vidaas, Bird ID, Safeweb e similares) | Assinatura por API com autorização do usuário. Dá para manter quase tudo dentro da nossa tela |
| A3 em **token ou cartão físico** | Exige componente local no navegador. O usuário sai da nossa interface ou instala extensão |

Se a maioria dos membros usa token físico, a promessa de "assinar sem sair da plataforma" precisa ser revista. **Perguntar isso ao cliente antes de escolher o parceiro.**

### 2. Quem assina precisa ser membro do clube?
Se o comprador não é membro aprovado, ele assina como convidado externo? Muda o fluxo de assinatura e o de cadastro.

### 3. Quantos modelos de documento entram no preço fechado?
"Múltiplos modelos" é escopo aberto. Sugestão: 1 no MVP, adicionais cotados por unidade, autoria é tarefa de desenvolvimento e não funcionalidade do usuário.

### 4. Quais são os campos reais do cadastro?
Nome, e-mail e telefone servem para o mockup. Para emitir CPR de café o cadastro real precisa de CPF/CNPJ e provavelmente dados da propriedade. Cada campo com validação é trabalho.

---

## Riscos

### Operamos sob a credencial de um terceiro
A conta B3 é do escritório sócio. Isso resolve o cronograma e cria uma dependência de outra natureza:

- Perante a B3, quem registra é o escritório. A responsabilidade legal é deles.
- Se a sociedade mudar, perdemos o acesso de um dia para o outro.
- Um incidente nosso vira problema reputacional deles.

**Ações:** acordo escrito sobre uso, responsabilidade e rotação da credencial. E, no código, a identidade do participante B3 vira configuração, nunca constante, para que uma conta própria no futuro seja troca de variável e não reescrita.

### A escolha do parceiro de assinatura é irreversível na prática
Trocar de provedor depois de ter contratos assinados em produção é caro. A escolha precisa sair de uma comparação escrita, não da primeira demo. Critérios em `plano-do-projeto.md`.

### O adversário mais provável é um membro do clube
Compradores e produtores de café concorrem entre si. Preço, volume e contraparte são inteligência de mercado. Um membro que consiga ver o registro de outro causa mais dano comercial do que um vazamento de CPF. Isso muda a prioridade dos controles. Ver `arquitetura-seguranca.md`.

### Clientes não são tech-savvy
Requisito de produto, não observação. Um caminho óbvio por tela, linguagem do agronegócio, estado sempre em português claro, zero jargão de software na interface.

---

## Ativo que temos e vale usar

O escritório de advocacia é **sócio**, não fornecedor. Validação jurídica de modelo de contrato, retenção de dados, LGPD e responsabilidade perante a B3 sai rápido e sem custo de consultoria externa. Vale transformar isso em rotina de trabalho, não em consulta pontual.

---

## Pendência de organização

`planejamento/kickoff-md` é ata do **Labeee/FEESC** (UFSC). Outro cliente, outro projeto. Mover para fora deste repositório.
