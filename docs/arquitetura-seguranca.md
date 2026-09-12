# Arquitetura de Segurança e Proteção de Dados

12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 3)

---

## Quem é o adversário

Antes de escolher controle, definir contra quem.

| Ameaça | Probabilidade | Dano |
|---|---|---|
| **Membro vê registro de outro membro** | Alta | Alto. Compradores e produtores de café concorrem. Preço, volume e contraparte são inteligência de mercado |
| **Operador de backoffice extrai dados em massa** | Média | Alto. É o papel com acesso amplo por definição |
| **Vazamento da credencial B3 do escritório** | Baixa | Muito alto. A conta é de terceiro. Um incidente nosso vira problema reputacional do sócio |
| **Dump do banco** (backup exposto, acesso indevido de infra) | Baixa | Alto |
| **Atacante externo genérico** | Média | Médio |

A primeira linha é a que importa mais e é a que menos gente protege. **O risco número um não é invasão. É autorização quebrada.**

---

## Classificação dos dados

| Classe | Exemplos | Tratamento |
|---|---|---|
| **Comercial sensível** | Preço, volume, data de entrega, contraparte | Criptografado, acesso auditado |
| **Pessoal identificável** | CPF/CNPJ, nome, telefone, e-mail, endereço | Criptografado, acesso auditado, sujeito à LGPD |
| **Documento** | PDF do contrato, assinado ou não | Contém tudo acima. Armazenamento privado, URL assinada de curta duração |
| **Credencial** | API key B3, chaves do parceiro de assinatura | Cofre de segredos. Nunca em código, nunca em log |
| **Operacional** | Estados, timestamps, ids | Sem criptografia. É o que permite listar e filtrar |

---

## Controles, em ordem de importância

### 1. Isolamento por registro
Toda consulta filtrada na origem por "sou parte deste registro, ou sou backoffice com permissão". Nunca filtrar na tela.

Isso vem antes de criptografia porque é o vetor mais provável. Criptografia não protege contra uma verificação de permissão ausente: a aplicação descriptografa e entrega o dado ao usuário errado com prazer.

**Precisa de teste automatizado dedicado.** Um teste por endpoint, verificando que o membro A recebe 404 ao pedir o registro do membro B. Sem isso o controle não existe, só a intenção dele.

### 2. Criptografia em nível de aplicação, seletiva
Protege contra dump de banco, backup vazado e acesso de infraestrutura. Não protege contra aplicação comprometida nem autorização quebrada.

| Decisão | Razão |
|---|---|
| Criptografar campos comerciais e pessoais | São o alvo |
| **Não** criptografar campos de listagem e filtro | Quebra busca, ordenação e paginação |
| Índice cego para CPF/CNPJ | Permite buscar por documento sem guardar o valor em claro |
| Chaves em cofre gerenciado, com rotação | Chave no `.env` do repositório anula o controle |

Criptografar tudo é a decisão que parece mais segura e trava o produto. Criptografar o alvo é o que funciona.

### 3. Dois logs de auditoria, com propósitos diferentes

| Log | Responde | Granularidade |
|---|---|---|
| **Eventos** | O que mudou neste registro, por quem | Toda transição de estado e toda escrita |
| **Acessos** | Quem viu o dado de quem | Abertura de registro, visualização de documento, resultado de busca, exportação |

O log de acessos é o que o cliente pediu e é o mais incomum de existir. Granularidade no nível do recurso, não do campo: "usuário X abriu o registro Y às 14h03". Por campo vira volume inútil.

Ambos append-only. Ninguém apaga log de auditoria, nem admin.

### 4. Exportação controlada
A pergunta do kickoff era se dados saem em lote. **Proposta de resposta: por padrão, não.**

| Papel | Pode exportar |
|---|---|
| Membro | Apenas o PDF dos próprios registros, um a um |
| Operador de backoffice | Nada em lote sem justificativa registrada |
| Auditor | Relatórios agregados, sem dado individual |

Toda exportação, sem exceção: justificativa obrigatória, entrada no log de acessos, limite de volume e limite de frequência. Exportação acima de um volume a definir exige aprovação de um segundo administrador.

Se existir um botão "exportar tudo em CSV" sem essas condições, ele é o vazamento.

### 5. Quebrar o papel de admin
Um único papel `admin` é grosso demais para este modelo de ameaça. No mínimo três:

| Papel | Pode |
|---|---|
| `aprovador` | Aprovar e recusar cadastros. **Não vê termos comerciais de registros** |
| `operador` | Resolver falhas de registro. Vê o necessário para agir |
| `auditor` | Lê os logs. Não altera nada |

Quem aprova cadastro não precisa saber a que preço o fulano vendeu café. Separar isso custa pouco agora e é caro depois.

### 6. Credencial da B3 como ativo de terceiro
Porque é do escritório sócio, e não nossa:

- Cofre de segredos. Nunca em código, nunca em log, nunca em mensagem de erro.
- Chaves separadas para homologação e produção.
- Toda chamada à B3 registrada com id de correlação, para reconstruir qualquer incidente.
- Procedimento de rotação acordado por escrito com o escritório.
- Identidade do participante B3 é configuração, não constante. Conta própria no futuro deve ser troca de variável.

### 7. Documentos
- Bucket privado. Nunca público, nunca "não listado mas acessível".
- URL assinada com expiração curta, gerada por requisição.
- Nome de arquivo sem dado pessoal. Nada de `contrato-joao-silva-cpf.pdf`.

### 8. Baseline de infraestrutura
TLS em tudo. MFA obrigatório para qualquer papel de backoffice. Backup criptografado com restauração testada de verdade, não presumida. Dado de produção nunca em ambiente de desenvolvimento.

---

## LGPD

Pontos a fechar com o escritório sócio, que é a forma barata de resolver isso:

1. **Base legal** para tratar CPF e dados de propriedade.
2. **Retenção.** Contrato tem obrigação legal de guarda que se sobrepõe a pedido de exclusão. Precisa estar escrito o que é apagável e o que não é, e por quê.
3. **Encarregado.** Quem é, e como o titular fala com ele.
4. **Pedido de exclusão.** Qual é o procedimento quando o dado está dentro de um documento assinado e registrado na B3.

O item 2 é o que costuma virar problema depois. Resolver antes de ter dado de produção.

---

## O que fica fora do MVP

Dito aqui para não virar expectativa implícita:

- Pentest externo. Contratar separado, depois da Fase 1.
- Certificação formal (ISO, SOC2). Não faz sentido neste estágio.
- Detecção de anomalia e SIEM. Os logs ficam prontos para isso; a análise vem depois.

---

## O teste que prova que funcionou

Criar dois membros concorrentes e um operador de backoffice em ambiente de homologação, e tentar, de propósito:

1. Membro A abrir registro do membro B, pela URL direta.
2. Membro A buscar por CPF do membro B.
3. Operador exportar a base inteira.
4. Encontrar a chave da B3 em algum log.
5. Baixar um PDF com URL expirada.

Os cinco precisam falhar, e os cinco precisam aparecer no log de acessos. Esse roteiro vira teste de regressão.
