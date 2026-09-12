# Arquitetura de Segurança e Proteção de Dados

**Revisão 2** · 12/09/2026 · complementa `entendimento-do-projeto.md` (rev. 4)

A rev. 2 incorpora o que as frentes 2 e 3 descobriram: a credencial da B3 é um pacote mTLS, e o fornecedor de assinatura pode virar uma segunda cópia de todos os contratos.

---

## Quem é o adversário

| Ameaça | Probabilidade | Dano |
|---|---|---|
| **Membro vê registro de outro membro** | Alta | Alto. Compradores e produtores concorrem. Preço, volume e contraparte são inteligência de mercado |
| **Operador de backoffice extrai dados em massa** | Média | Alto |
| **Login de administrador no painel do fornecedor de assinatura** | Média | Alto. Vê todos os contratos, e nada disso aparece na nossa auditoria. _Novo na rev. 2_ |
| **Vazamento do pacote de acesso da B3** | Baixa | Muito alto. Quem tem o pacote "pode se passar pela instituição", nas palavras da B3. A instituição é o escritório sócio |
| **Dump do banco** | Baixa | Alto |
| **Webhook forjado** mudando estado de registro | Baixa | Alto. Um "assinado" falso empurra um contrato não assinado para a B3. _Novo na rev. 2_ |
| **Atacante externo genérico** | Média | Médio |

O risco número um continua sendo autorização quebrada.

---

## Classificação dos dados

| Classe | Exemplos | Tratamento |
|---|---|---|
| **Comercial sensível** | Preço, volume, data de entrega, contraparte | Criptografado, acesso auditado |
| **Pessoal identificável** | CPF/CNPJ, nome, telefone, e-mail, endereço, imóvel | Criptografado, acesso auditado, LGPD |
| **Documento** | PDF do contrato, PAdES, manifesto | Storage privado, URL assinada curta, hash conferido |
| **Credencial** | Ver inventário abaixo | Cofre de segredos **com suporte a binário** |
| **Operacional** | Estados, timestamps, ids, Número de Controle B3 | Sem criptografia |

### Inventário de credenciais

| Credencial | Forma | Rotação | Observação |
|---|---|---|---|
| B3, por ambiente | `.p12` (binário) + senha + `client_id` + `client_secret` + 4 contas Cetip | Não documentada pela B3. Acordo com o escritório | Certificado vence. O aviso vai para o escritório |
| B3, token OAuth | JWT em memória | Renovar a 80% do `expires_in` lido da resposta | A documentação da B3 dá três valores diferentes. Nunca constante |
| Clicksign, por ambiente | Access token estático, sem escopo | Manual, pelo painel | Aceito em query string pela Clicksign. **Proibido no nosso código** |
| Clicksign, webhook | Secret HMAC | Pelo endpoint `/webhooks` | |
| Lacuna, por ambiente | API key + id do contexto de segurança | Não expira | O contexto de teste nunca pode chegar em produção |
| Lacuna, webhook | Segredo em header (Basic, Bearer ou API key) | Configuração | Sem HMAC do corpo |

Só as linhas do fornecedor escolhido entram no MVP.

---

## Controles, em ordem de importância

### 1. Isolamento por registro
Toda consulta filtrada na origem. Teste automatizado por endpoint: membro A pede registro do membro B e recebe 404. Sem mudança da rev. 1.

### 2. Criptografia em nível de aplicação, seletiva
Campos comerciais e pessoais criptografados, campos de listagem em claro, índice cego para CPF/CNPJ, chaves em cofre com rotação. Sem mudança da rev. 1.

### 3. Dois logs de auditoria
Eventos (o que mudou) e acessos (quem viu), ambos append-only. A rev. 2 acrescenta ao log de eventos cada tentativa automática e cada consulta de reconciliação com a B3.

### 4. Exportação controlada
Por padrão, não existe exportação em lote. Membro baixa o PDF dos próprios registros, um a um. Exportação de backoffice exige justificativa, limite e segundo aprovador acima de um volume. Sem mudança da rev. 1.

### 5. Papéis de backoffice separados
`aprovador`, `operador`, `auditor`, ou dois papéis se o cliente aceitar o custo (pendência 1.10). MFA obrigatório.

### 6. Credencial da B3 como ativo de terceiro

- Pacote de acesso inteiro no cofre, incluindo o `.p12` binário.
- **Certificate pinning** do certificado raiz da B3, como a própria B3 pede.
- TLS 1.2 ou superior, mTLS em toda chamada.
- Identidade do participante como bloco de configuração com nove valores. Trocar de conta é trocar o bloco.
- Toda chamada com id de correlação. Credencial mascarada em log e em mensagem de erro.
- `/healthcheck` da B3 consultado antes de alertar, para separar "B3 fora" de "registro recusado".
- **Responsável nominal pelo vencimento do certificado**, do lado do escritório e do nosso.

### 7. Fornecedor de assinatura como superfície de dado
_Novo na rev. 2._

A pergunta que decide é **o PDF sai da nossa infraestrutura?**

| Rota | O que o fornecedor recebe | O que guarda |
|---|---|---|
| Clicksign, qualquer modo | PDF inteiro | PDF original e assinado, enquanto houver conta. Painel com login próprio |
| Lacuna, sessão do Rest PKI Core | PDF inteiro | Original e assinado, até `availableUntil` (padrão não publicado) |
| Lacuna, Rest PKI clássico, assinatura remota | Hash do documento, certificado, IP | Nada do documento |
| Lacuna, rota estimada no estudo (`/api/signature` do Core) | **A confirmar.** Pendência 4.5 | A confirmar |

Se a rota escolhida envia o PDF:

- O cliente aceita por escrito (pendência 1.8).
- Número mínimo de logins no painel do fornecedor, nominais, revisados a cada trimestre.
- Download imediato do assinado quando o evento de conclusão chegar, com hash conferido, e gravação no nosso storage.
- Procedimento manual de expurgo do lado do fornecedor, com responsável. Na Clicksign, exclusão de documento finalizado é clique de administrador no painel; a API só apaga rascunho.

### 8. Webhooks de entrada
_Novo na rev. 2._

- HTTPS obrigatório.
- Autenticação da origem: HMAC SHA256 sobre o corpo cru (Clicksign, header `Content-Hmac`) ou segredo em header (Lacuna). Nunca Basic Auth na URL.
- Allowlist de IP quando o fornecedor publica (Clicksign publica um por ambiente).
- Responder 200 imediatamente, gravar o evento cru, processar em fila.
- Idempotência por documento, evento e horário, porque nenhum dos dois fornecedores manda id de entrega.
- **Callback JavaScript nunca muda estado.** O evento `signed` do widget troca a tela do usuário; o estado do registro só muda com o webhook validado. Os dois fornecedores dizem isso na própria documentação.

### 9. Documentos
- Bucket privado, URL assinada curta gerada por requisição.
- Nome de arquivo sem dado pessoal.
- URL temporária do fornecedor nunca persistida nem logada. A da Lacuna expira em cerca de uma hora.

### 10. Prova de longo prazo
_Novo na rev. 2._

Uma CPR de café vive anos. A assinatura precisa continuar verificável depois que certificados e carimbos vencerem.

- Carimbo do tempo de ACT credenciada na ICP-Brasil. Na Clicksign é cobrado à parte e o preço não é publicado; na Lacuna custa R$ 0,15 por carimbo na menor faixa.
- Na Lacuna, rotina periódica de extensão do carimbo de arquivamento (AD-RA), respeitando a data recomendada que a API devolve.
- PAdES ou CAdES destacado: decisão do escritório (pendência 2.14). A política PAdES ICP-Brasil ainda não existe.
- Validação externa possível em `validar.iti.gov.br`, independente do fornecedor.

### 11. Baseline de infraestrutura
TLS em tudo. MFA no backoffice. Backup criptografado com restauração testada. Dado de produção nunca em desenvolvimento.

---

## LGPD

A fechar com o escritório sócio (pendência 2.16):

1. Base legal para CPF, dados de imóvel e dados de garantia.
2. Retenção. Contrato tem guarda obrigatória que se sobrepõe à exclusão. Escrever o que é apagável.
3. Encarregado.
4. Pedido de exclusão quando o dado está numa CPR registrada na B3 **e numa cópia no fornecedor de assinatura**.
5. Retenção dos dois logs de auditoria (pendência 1.22).

---

## Fora do MVP

- Pentest externo, depois da Fase 1.
- Certificação formal.
- Detecção de anomalia e SIEM. Os logs ficam prontos para isso.

---

## O teste que prova que funcionou

Em homologação, tentar de propósito:

1. Membro A abrir registro do membro B pela URL direta.
2. Membro A buscar por CPF do membro B.
3. Operador exportar a base inteira.
4. Encontrar qualquer credencial em log, URL ou mensagem de erro.
5. Baixar um PDF com URL expirada.
6. Enviar um webhook de "assinado" com HMAC inválido, ou de IP fora da allowlist.
7. Mudar o estado de um registro disparando o evento `signed` pelo console do navegador.

Os sete precisam falhar e aparecer no log. O roteiro vira teste de regressão.
