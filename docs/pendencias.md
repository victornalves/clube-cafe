# Pendências — Lista Única

12/09/2026 · revisão 4 · junta, sem repetição, as perguntas abertas das seis frentes.

Organizada por **quem responde**, para cada bloco virar uma reunião ou um e-mail. Dentro de cada bloco, o que trava preço vem primeiro.

Legenda da coluna Trava: **P** preço · **A** arquitetura · **F** fluxo · **O** operação

---

## 1. Cliente — reunião de validação

Usar junto com o roteiro de `mockup/README.md`.

### Travam preço ou arquitetura

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 1.1 | Que certificado os membros têm hoje: A1, A3 em token, A3 em nuvem, nenhum? Com proporção aproximada | P A | Panorama 1 |
| 1.2 | Quantos membros usam Mac ou Linux? | P | Panorama 2 |
| 1.3 | Quem emite CPR: só pessoa física, ou também cooperativa e empresa? | A | Panorama 4. Clicksign só aceita e-CPF |
| 1.4 | A contraparte precisa ser membro aprovado, ou pode assinar como convidada externa? | P F | Regras RN-62/63 |
| 1.5 | Volume esperado de CPRs por mês, e quantas partes por CPR | P | Panorama 8 |
| 1.6 | As CPRs terão garantia real (hipoteca, penhor, alienação fiduciária)? | A | Panorama 3. Muda o nível mínimo de assinatura |
| 1.7 | O clube banca certificado para quem não tem? Aceita assinatura avançada gov.br quando não houver garantia real? | P | Panorama 5, 6 |
| 1.8 | O contrato assinado pode ficar guardado também no sistema do fornecedor de assinatura? | A | Consolidação C-10 |
| 1.9 | Campos reais do cadastro e do registro. Levar o mapa de campos da B3 | P | Regras RN-05, §3.2; B3 §2 |
| 1.10 | Três papéis de backoffice ou dois | P | Regras RN-37 |
| 1.25 | Aceita assinatura por e-mail, sem certificado, para CPR sem garantia real? | P A | `estudo-assinatura-sem-certificado.md` |
| 1.26 | Haverá CPR com garantia real no início? Se sim: e-mail com fator extra, ICP só nesses casos, ou fora do MVP? | A | Idem, §4 |

### Travam fluxo

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 1.11 | Critérios de entrada no clube e motivos de recusa | F | Regras RN-04, RN-13 a 23 |
| 1.12 | Recusado pode pedir de novo? Com carência, com limite? O que ele recebe como resposta? | F | Regras RN-27, 28, 30 |
| 1.13 | Quem pode criar um registro? O corretor cria pelas partes? O corretor assina? | F | Regras RN-52, RN-59 |
| 1.14 | O autor pode descartar rascunho, cancelar durante a coleta de assinaturas, e corrigir depois de uma recusa? | F | Regras L-01, L-02, L-08 |
| 1.15 | Falha claramente passageira da B3 pode ser reenviada automaticamente, ou toda falha passa por uma pessoa? | F | Consolidação I-03 |
| 1.16 | Cancelar ou reassinar contrato de valor alto exige segunda pessoa aprovando? | F | Mockup 10 |
| 1.17 | Membro pode alterar o próprio cadastro sem aprovação? Membro precisa de segundo fator para entrar? | F | Mockup 2, 3 |
| 1.18 | O membro pode ver quem do backoffice abriu o contrato dele? | F | Mockup 16 |

### Travam operação

| # | Pergunta | Trava | Origem |
|---|---|---|---|
| 1.19 | Quem é avisado quando um registro falha, por qual canal, e em quanto tempo precisa assumir e resolver | O | Regras RN-94 a 96 |
| 1.20 | Prazo de análise de cadastro: dois dias úteis (mockup) ou três (regras)? | O | Consolidação M-01 |
| 1.21 | Validade do convite, prazo de coleta de assinaturas, lembretes | O | Regras RN-89 a 92 |
| 1.22 | Por quanto tempo guardar os registros de auditoria | O | Mockup 14 |

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
| 2.3 | Códigos de conta Cetip: registrador, custodiante, favorecido, agente de pagamento | A | B3 §9.3 |
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
| 2.12 | Corretor fica só no documento, sem campo no registro. Confirma? | F | B3 §2 |
| 2.13 | Critério de "o contrato já produziu efeito", quem decide entre substituição e aditivo, e em quanto tempo | F | Regras L-05, RN-85, RN-97 |
| 2.14 | PAdES ou CAdES destacado? Carimbo do tempo é obrigatório? | P | Lacuna §8, Clicksign §8 |
| 2.15 | Tarifa da B3 por registro de CPR: valor e quem paga | P | Consolidação I-05 |
| 2.16 | LGPD: base legal, retenção, encarregado, e o que fazer com pedido de exclusão de dado que está em CPR registrada | A | Arquitetura, seção LGPD |
| 2.17 | O escritório ou a B3 já usam algum fornecedor de assinatura? | A | Panorama 9 |
| 2.18 | Como Agente de Registro, aceita registrar CPR assinada por e-mail? Que cláusula de forma de assinatura vai no termo de adesão e na CPR? | A | `estudo-assinatura-sem-certificado.md` |
| 2.19 | E-mail mais login com segundo fator na plataforma enquadra como assinatura avançada? | A | Idem, §3.1 |
| 2.20 | Pix ou biometria facial da Clicksign atendem o art. 3º, § 4º, II para garantia real? | A | Idem, §4 |

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

Nem tudo acima precisa estar respondido. Para emitir proposta de escopo fechado da **Fase 1**, bastam:

- Cliente: 1.4, 1.9, 1.10, 1.14, 1.15, 1.25
- Escritório: 2.8, 2.9, 2.12, 2.18

Para fechar **Fases 2 e 3** com número, somam-se:

- Cliente: 1.1, 1.3, 1.5, 1.6, 1.8
- Escritório: 2.1, 2.2, 2.4, 2.14
- Fornecedor escolhido: o bloco dele inteiro
