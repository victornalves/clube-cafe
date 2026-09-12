# Frentes de Trabalho — Estudos Paralelos

> **Status em 12/09/2026:** as seis frentes terminaram. A Frente 2 avaliou dois fornecedores em documentos separados (Clicksign e Lacuna). A consolidação foi feita: ver `consolidacao-rev4.md`. Este documento fica como registro do briefing original.
>
> | Passo da consolidação | Situação |
> |---|---|
> | 1. Listar contradições | Feito, `consolidacao-rev4.md` |
> | 2. Atualizar os docs principais | Feito: entendimento rev. 4, máquina rev. 2, segurança rev. 2, plano rev. 3 |
> | 3. Fechar as perguntas abertas | Não fecham sem o cliente. Reunidas em `pendencias.md` |
> | 4. Refazer a estimativa | Feito, `plano-do-projeto.md` |
> | 5. Emitir a proposta | Aguarda respostas. Ver "O que fecha a proposta" em `pendencias.md` |

12/09/2026 · seis frentes a rodar em sessões separadas, com contexto novo.

---

## Como isso funciona

Cada frente roda numa janela Claude própria, do zero. Por isso cada uma tem aqui: o que ler antes, o que responder, e **um arquivo próprio para escrever**.

### Regra de convivência

Seis sessões escrevendo no mesmo repositório se atropelam. Para evitar:

- **Cada frente cria e edita apenas o seu arquivo.** Nunca os quatro docs existentes.
- Se um estudo contradisser algo já documentado, ele **anota a contradição no próprio arquivo**. A consolidação nos docs principais é feita por você, depois, numa sessão só.

---

## Visão geral

| # | Frente | Arquivo de saída | Depende de | Pode começar |
|---|---|---|---|---|
| 1 | Fornecedores de assinatura: token vs nuvem | `docs/estudo-assinatura-panorama.md` | — | Agora |
| 2 | Avaliação da API do fornecedor escolhido | `docs/estudo-assinatura-api.md` | Frente 1 | Depois da 1 |
| 3 | Estudo da API da B3 | `docs/estudo-api-b3.md` | — | Agora |
| 4 | Regras de negócio + diagramas | `docs/regras-de-negocio.md` | — | Agora |
| 5 | Identidade visual e direções de UI | `docs/estudo-ui-identidade.md` | — | Agora |
| 6 | Mockup HTML dos fluxos | `mockup/` | Frente 4 (parcial) | Agora |

Quatro podem rodar hoje em paralelo. A 2 espera a 1.

### Uma ordem a respeitar

**A frente 5 não entra na frente 6.** O mockup é deliberadamente sem estilo: serve para validar fluxo, e fluxo se discute melhor sem cor. Se o cliente vir uma identidade visual no mockup, a reunião vira conversa sobre a cor do botão.

Rodar as duas em paralelo tudo bem. Juntar as duas, só depois que o fluxo estiver aprovado.

---

## Frente 1 — Panorama de assinatura digital

**Objetivo:** entender o mercado antes de escolher fornecedor.

**Ler antes:** `docs/entendimento-do-projeto.md`, seção "Perguntas que ainda travam o escopo".

**Perguntas a responder:**
- Diferença prática entre A1, A3 em token físico e A3 em nuvem, para quem assina.
- O que cada tipo exige do navegador e do usuário. Extensão? Applet? Nada?
- Quais tipos permitem assinatura embutida na nossa tela e quais forçam sair.
- Como o tipo de certificado afeta a validade da CPR e o aceite da B3.
- Panorama dos fornecedores: ZapSign, Clicksign, D4Sign, BRy, Lacuna, Certisign, e outros que aparecerem.
- Certificados em nuvem: Vidaas, Bird ID, Safeweb. Como funcionam por API.

**Entregar:** comparativo em tabela + recomendação justificada de 2 ou 3 finalistas.

```
Estude o mercado brasileiro de assinatura digital ICP-Brasil para uma
plataforma de registro de contratos de café. Leia docs/entendimento-do-projeto.md
e docs/plano-do-projeto.md primeiro. Responda: diferenças práticas entre A1, A3
token físico e A3 em nuvem; qual permite assinatura embutida sem tirar o usuário
da nossa aplicação; impacto na validade da CPR e no registro na B3; e um
comparativo de fornecedores. Escreva em docs/estudo-assinatura-panorama.md.
Não edite outros arquivos.
```

---

## Frente 2 — API do fornecedor escolhido

**Objetivo:** saber exatamente quanto custa integrar, em horas e em reais.

**Ler antes:** frente 1 concluída.

**Perguntas a responder:**
- Fluxo completo: criar documento, adicionar signatários, disparar, receber retorno.
- Assinatura embutida existe? iframe, SDK ou redirect?
- Webhooks: quais eventos, como autenticar, como tratar reentrega.
- Sandbox: existe, é gratuito, é fiel à produção?
- Quem armazena o documento e por quanto tempo. Conseguimos guardar nós?
- Manifesto de assinatura e trilha de auditoria: o que o provedor devolve.
- Preço por documento, mínimo mensal, e o que acontece com volume baixo.

**Entregar:** mapa do fluxo de integração + estimativa de horas da Fase 2 + custo real de opex.

---

## Frente 3 — API da B3

**Objetivo:** transformar a estimativa da Fase 3 em número, e conhecer o payload antes de precisar dele.

**Ler antes:** `docs/entendimento-do-projeto.md` e `docs/maquina-de-estados.md`.

**Contexto:** a homologação já está aprovada, via conta do escritório de advocacia sócio. Falta apenas solicitar a API key de homologação.

**Perguntas a responder:**
- Autenticação: OAuth 2.0 Client Credentials, ciclo de vida do token, rotação.
- Payload de registro de CPR física de café: campos obrigatórios, formatos, limites.
- Códigos de erro e quais são transitórios (dá retry) contra definitivos (exige correção).
- Existe consulta de status? Dá para reconciliar sem depender de webhook?
- Idempotência: reenviar o mesmo registro duplica?
- Diferenças entre homologação e produção.
- Como a identidade do participante entra na chamada. Confirma que dá para tratar como configuração?

**Entregar:** mapa do payload + tabela de erros classificados em transitório/definitivo + estimativa fechada da Fase 3.

A tabela de erros alimenta diretamente os quatro caminhos de resolução em `docs/maquina-de-estados.md`.

```
Estude a API de registro da B3 para CPR física. Leia
docs/entendimento-do-projeto.md e docs/maquina-de-estados.md primeiro.
Preciso de: autenticação, payload completo de registro, classificação dos
códigos de erro entre transitórios e definitivos, idempotência, e consulta
de status. Escreva em docs/estudo-api-b3.md. Não edite outros arquivos.
```

---

## Frente 4 — Regras de negócio

**Objetivo:** escrever as regras que hoje só existem implícitas nos docs.

**Ler antes:** os quatro docs em `docs/`.

**Usar a skill `drawio-diagram`** para os diagramas.

**Cobrir:**
- Quem pode ser membro, e critérios de aprovação e recusa.
- Papéis e o que cada um pode fazer, em tabela de permissões.
- Regras do registro: quantas partes, corretor opcional, campos obrigatórios, validações.
- Quando um registro pode ser editado, cancelado, ou nada.
- As duas variantes de reassinatura: quando é substituição, quando é aditivo.
- Prazos: assinatura expira? registro tem janela?

**Diagramas a produzir:**
1. Fluxo de entrada no clube
2. Ciclo de vida do registro, camada do membro
3. Ciclo de vida do registro, camada do backoffice
4. Os quatro caminhos de resolução de falha
5. Matriz de papéis e permissões

**Entregar:** `docs/regras-de-negocio.md` + `.drawio` em `docs/diagramas/`.

**Marcar explicitamente o que é decisão pendente do cliente.** Regra inventada por nós vira requisito fantasma.

---

## Frente 5 — Identidade visual e UI

**Objetivo:** ter 2 ou 3 direções visuais prontas para depois da validação de fluxo.

**Usar a skill `design`** (canvas de design da Claude).

**Contexto que a sessão precisa saber:**
- Público: produtores e compradores de café. Não são pessoas de tecnologia.
- É clube fechado e por convite. Sóbrio, não startup.
- O documento é um contrato. A interface precisa transmitir seriedade e rastreabilidade.
- Uso provável em desktop, mas checar mobile para acompanhamento de status.
- Acessibilidade importa: público pode ter idade mais alta. Contraste e tamanho de fonte de verdade.

**Entregar:** 2 ou 3 direções aplicadas às mesmas 3 telas (listagem, novo registro, detalhe), para comparação justa.

**Não aplicar no mockup da frente 6.**

---

## Frente 6 — Mockup HTML dos fluxos

**Objetivo:** o artefato da reunião de validação com o cliente.

**Ler antes:** `docs/plano-do-projeto.md`, seção "Telas do mockup", e `docs/maquina-de-estados.md`.

**Regras:**
- HTML puro. Sem framework, sem build.
- Sem identidade visual. Estilo mínimo, só o suficiente para ser legível.
- Links reais entre as telas. O cliente clica e percorre a jornada inteira.
- Dados falsos, mas plausíveis: nomes brasileiros, sacas de café, valores realistas.
- Zero jargão de software na tela.

**As 17 telas estão listadas em `docs/plano-do-projeto.md`.** As três últimas (fila de pendências, resolução de falha, auditoria) são as mais importantes de validar, porque é onde o backoffice trabalha todo dia.

**Publicar como Artifact.** O cliente abre um link em vez de receber um zip, e funciona no celular dele durante a reunião.

```
Monte um mockup HTML navegável do Clube do Café. Leia
docs/plano-do-projeto.md (seção "Telas do mockup") e docs/maquina-de-estados.md.
São 17 telas, HTML puro, sem framework, sem identidade visual, com links reais
entre elas e dados falsos plausíveis. É para validar FLUXO com um cliente não
técnico, não aparência. Crie em mockup/ e publique como Artifact no final.
```

---

## Depois que as seis terminarem

Uma sessão de consolidação, feita por você:

1. Ler os seis resultados e listar as contradições.
2. Atualizar os quatro docs principais para a revisão 4.
3. Fechar as quatro perguntas abertas do README.
4. Refazer a estimativa da Fase 1 com os números reais das frentes 2 e 3.
5. Emitir a proposta de escopo fechado.

As frentes 2 e 3 são as que mais podem mexer no preço. As outras quatro mexem no escopo.

---

## Nota

Se quiser um fluxo formal de specs com fases e aprovação, existe a skill `spec-driven-dev`. Para estudos exploratórios como estes, provavelmente é cerimônia demais. Um arquivo por frente resolve.
