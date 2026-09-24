# Validação: Assinatura Sem Certificado Digital, via Clicksign

12/09/2026 · complementa `estudo-assinatura-api-clicksign.md` e `consolidacao-rev4.md`

**Pergunta:** cada parte pode assinar a CPR autenticando só por e-mail, sem certificado ICP-Brasil, apoiada na identidade que o clube já validou no cadastro?

---

## Veredito

**Sim, para CPR sem garantia real. Com três condições e um limite.**

| | |
|---|---|
| Base legal | Lei 8.929/1994, art. 3º, § 4º, I: na CPR "será admitida a utilização de assinatura eletrônica simples, avançada ou qualificada" |
| Condição 1 | As partes precisam **estabelecer por escrito** o nível de assinatura aceito (§ 4º, caput). Termo de adesão do clube e cláusula na própria CPR |
| Condição 2 | Todo signatário precisa ter passado pelo cadastro do clube. A premissa "a identidade já foi validada" não vale para contraparte externa |
| Condição 3 | O escritório sócio, como Agente de Registro, precisa aceitar. Perante a B3 ele responde pela veracidade do que registra |
| Limite | **Com garantia real, e-mail sozinho não basta.** O registro e a averbação da garantia exigem assinatura avançada ou qualificada (§ 4º, II), e a Clicksign classifica o token por e-mail como simples |

Texto da lei conferido na versão consolidada da Câmara dos Deputados em 12/09/2026. Isso resolve a checagem de artigo que estava pendente (pendência 2.7). A interpretação para o caso concreto continua sendo do escritório.

---

## 1. O que a lei diz, literalmente

**Lei 8.929/1994, art. 3º, § 4º** (redação da Lei 14.421/2022):

> As partes contratantes, observada a legislação específica, estabelecerão a forma e o nível de segurança da assinatura eletrônica que serão admitidos para fins de validade, eficácia e executividade, observadas as seguintes disposições:
> I - na CPR e no documento à parte com a descrição dos bens vinculados em garantia, se houver, será admitida a utilização de assinatura eletrônica simples, avançada ou qualificada; e
> II - no registro e na averbação de garantia real constituída por bens móveis e imóveis, será admitida a utilização de assinatura eletrônica avançada ou qualificada.

**Lei 14.063/2020, art. 4º**, que define os níveis:

| Nível | Definição legal |
|---|---|
| Simples | "a que permite identificar o seu signatário" e "a que anexa ou associa dados a outros dados em formato eletrônico do signatário" |
| Avançada | Certificado não ICP-Brasil "ou outro meio de comprovação da autoria e da integridade", aceito pelas partes, associado ao signatário "de maneira unívoca", sob seu "controle exclusivo" com "elevado nível de confiança", e com detecção de modificação posterior |
| Qualificada | Certificado ICP-Brasil |

**Detalhe para o escritório:** o art. 2º, parágrafo único, II, "a", diz que o capítulo da Lei 14.063 não se aplica à interação "entre pessoas naturais ou entre pessoas jurídicas de direito privado". A Lei 8.929 importa a classificação por referência ("observada a legislação específica"). A leitura de como os níveis se aplicam entre particulares é jurídica.

**O que se perde sem ICP-Brasil:** a presunção de veracidade da MP 2.200-2/2001, art. 10, § 1º. Numa disputa, a autoria é provada pelo conjunto de evidências, não presumida. Por isso a condição 1 e a trilha de auditoria importam.

Fontes: https://www2.camara.leg.br/legin/fed/lei/1994/lei-8929-22-agosto-1994-349613-normaatualizada-pl.pdf e https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14063.htm (acesso 12/09/2026).

---

## 2. Como a Clicksign classifica cada autenticação

A central de ajuda da Clicksign coloca e-mail em "identificação básica (e-mail, CPF, geolocalização)", que é o nível **simples**. Para o nível **avançado**, cita "PIX, biometria facial, ou mesmo a combinação de um ou mais pontos de autenticação". Qualificada é só certificado ICP-Brasil.

Fonte: https://ajuda.clicksign.com/article/654-diferenca-assinatura-digital-assinatura-eletronica (acesso 12/09/2026).

### Autenticações disponíveis na API v3

| `auth` | O que é | Custo publicado |
|---|---|---|
| `email` | Token por e-mail | Incluso |
| `sms`, `whatsapp` | Token por SMS ou WhatsApp. Um só método de token por signatário | Incluso |
| `pix` | Transação Pix, exige CPF. Substitui o token | Não publicado nesta página |
| `selfie`, `official_document`, `address_proof`, `handwritten` | Coleta de evidência | Incluso |
| `liveness` | Selfie dinâmica | Não publicado |
| `facial_biometrics` | Biometria facial | R$ 1,50 por reconhecimento |
| `biometric` | Base SERPRO, exige CPF | R$ 4,50 por consulta |
| `documentscopy` | Documentoscopia | R$ 4,50 por solicitação |
| `embedded_signature` | Assinatura dentro da nossa tela, sem token | Não publicado |
| `icp_brasil` | Certificado digital | — |

Fonte: https://developers.clicksign.com/docs/tipos-de-requisitos-de-autenticacao (acesso 12/09/2026).

---

## 3. A premissa "a identidade já foi validada no cadastro"

Ela é boa e é o que torna o cenário defensável. Tem três pontos frágeis.

### 3.1 O token prova a caixa de e-mail, não a pessoa
O cadastro valida quem a pessoa é. O token valida que, no momento da assinatura, alguém controlava aquele e-mail. A corrente de prova é **identidade validada → e-mail cadastrado → token usado**. Se o e-mail for comprometido, a corrente quebra.

Mitigações, todas baratas:
- A assinatura acontece **dentro da nossa plataforma, com o membro logado**. A trilha passa a ter login (e segundo fator, se houver) mais token. Nossa tabela de eventos registra a sessão que assinou.
- Troca de e-mail do membro passa por aprovação e gera aviso (amarra com a pendência 1.17).
- Troca de e-mail perto de uma assinatura pendente bloqueia a assinatura até o backoffice confirmar.

Se isso eleva a prova ao nível avançado é leitura jurídica. Ela fortalece a prova de qualquer forma.

### 3.2 Contraparte externa não tem cadastro
Se a pendência 1.4 for respondida com "contraparte pode ser externa", a premissa não se aplica a ela. Para externo: e-mail mais evidência de identidade (`official_document` com `selfie`, ou `biometric` SERPRO).

### 3.3 Pessoa jurídica assina por representante
Com e-mail, a cooperativa assina pelo representante legal. O cadastro do clube passa a precisar validar **poderes de representação** (contrato social ou procuração), senão o cadastro validou a pessoa e não o direito dela de assinar pela empresa.

---

## 4. Garantia real

O layout da B3 tem dez tipos de garantia. Quatro deles são garantia real sobre bens (hipoteca, penhor, alienação fiduciária, cessão fiduciária). Quando a CPR tiver uma delas, o registro e a averbação da garantia exigem assinatura avançada ou qualificada.

Três saídas, a escolher com o escritório:

| Saída | Como | Custo por signatário |
|---|---|---|
| E-mail mais fator que a Clicksign enquadra como avançado | `pix`, ou `facial_biometrics`, ou combinação | R$ 0 a R$ 1,50, conforme o fator |
| ICP-Brasil só nesses casos | `icp_brasil` | Certificado do signatário |
| Fora do MVP | Clube só registra CPR sem garantia real no início | Nenhum |

**Consequência de desenho:** o nível de assinatura vira **regra por registro**, decidida pelo campo tipo de garantia. Não é configuração global.

---

## 5. O que muda no projeto se o cliente aceitar

### Fica mais simples

| Item | Com ICP-Brasil | Com e-mail |
|---|---|---|
| Certificado do membro | Custo e burocracia do produtor | Nenhum |
| Assinatura dentro da nossa tela | Sai para o app do provedor | **Fica na tela.** O membro só olha o e-mail para pegar o código |
| Restrição e-CPF da Clicksign | Derruba cooperativa | Irrelevante |
| Dúvida sobre ICP no widget | Aberta | Irrelevante |
| Falha silenciosa de certificado (consolidação I-06) | Existe | Não existe. Resta e-mail que não chega |
| Público não tech-savvy | Instalar, sair, voltar | Digitar um código |

### Fase 2 com Clicksign

| Bloco do estudo Clicksign | Antes | Com e-mail |
|---|---|---|
| 6. Tela de assinatura | 8–12h | 5–8h. Sem estados de saída e retorno |
| 8. Sandbox para produção | 4–8h | 3–5h. Sem teste de certificado real |
| Nível por registro, para garantia real | — | +2–4h |
| **Total da Fase 2** | **51–75h** | **~49–72h** |

A economia de horas é pequena. O ganho real está na adoção e na experiência, e no custo do certificado que ninguém paga.

### A escolha de fornecedor muda
As vantagens da Lacuna eram todas de certificado: token físico, cinco provedores de nuvem, e-CNPJ, política ICP. Sem certificado, a Lacuna perde o motivo de estar na disputa. **A Clicksign passa a ser a candidata natural**, e ZapSign e D4Sign, descartadas por limites de certificado, voltam a ser comparáveis por preço. Não refiz essa comparação.

### Continua igual
- Carimbo do tempo e prova de longo prazo. Sem presunção de veracidade, pesam mais.
- O documento fica guardado também na Clicksign (pendência 1.8).
- Webhook sem reentrega documentada.

---

## 6. Perguntas novas

| Para | Pergunta |
|---|---|
| Cliente | Aceita assinatura por e-mail, sem certificado, para CPR sem garantia real? |
| Cliente | Terá CPR com garantia real no início? Se sim, qual saída da seção 4? |
| Escritório | Como Agente de Registro, aceita registrar CPR assinada por e-mail? Que cláusula de forma de assinatura vai no termo de adesão e na CPR? |
| Escritório | E-mail mais login na plataforma com segundo fator enquadra como avançada? |
| Escritório | Pix ou biometria facial da Clicksign atendem o § 4º, II? |
| Clicksign suporte | Como funciona a autenticação da `embedded_signature`, e o que aparece no log do documento? |
| Clicksign suporte | Quais combinações de autenticação a Clicksign declara como avançada? |
