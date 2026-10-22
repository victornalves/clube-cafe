# Mockup do Clube do Café

Artefato da reunião de validação de escopo, Fase 0. HTML puro, sem framework, sem build.

**Não tem identidade visual, de propósito.** Se o cliente vir cor e tipografia, a reunião vira conversa sobre a cor do botão em vez de sobre o fluxo. As direções visuais rodam separado, na frente 5, e só entram depois que o fluxo estiver aprovado.

Abrir `index.html` no navegador. Todos os links entre telas funcionam.

**Comentários e metainformação** (perguntas em aberto, decisões, histórico de ajustes) ficam nas **notas de rodapé** de cada tela, no fim da página, para não poluir o layout. Os números sobrescritos no corpo apontam para a nota.

### Revisão 3, reunião 4 (07/10/2026, aplicada em 21/10)

Decisões da reunião com Vado e Gesiel. Ver `planejamento/reunião 4.md` e `docs/pendencias.md`, revisão 6. O que ficou em aberto (e-CNPJ, distrato) aparece só em nota de rodapé.

| Tema | O que mudou nas telas |
|---|---|
| Assinatura | **Certificado digital em toda assinatura**: proposta (`02c`), termos (`03b`), registro (`09`, `09b`, `09-assinatura-mesa`). Token, nuvem ou arquivo A1. A tela `09a`, código por e-mail, saiu do fluxo e do índice |
| Cadastro | Um corretor pode preencher a proposta pelo produtor, que recebe o pedido por e-mail e assina (`02`, `02b`) |
| Termos | Assinatura única no primeiro acesso. Mudança vira **circular**, na plataforma e por e-mail, sem reassinatura (`03b`, `04`, `11`) |
| Registro | Corretor vira parte **intermediário** (`05`, `07`). Nova tela `05c`: corretor logado já vem marcado e informa os dois lados; membro aguardando aceite dos termos não pode ser escolhido |
| Pagamento | Opção "pagamento já adiantado" (`06`, `06b`, `07`, `07b`) |
| Assinatura | Sai a lista "Documentos deste envelope" (`09`, `09-assinatura-mesa`) |
| Mesa | Termo de aceite para gravar ou não a reunião (`05b`), indicador de gravação (`06b`) |
| Limite | "Limite de crédito" vira **limite de negociação na plataforma** (`04`, `11`, `18`, `21`, `22b`) |

### Revisão 2, reunião 3 (01/10/2026)

O mockup passou a refletir as decisões da reunião 3 com o Vado. Ver `planejamento/reunião 3.md` e `docs/diagramas/Clube do Café - Diagramas - rev 2.drawio`.

| Tema | O que mudou nas telas |
|---|---|
| Entrada | "Recomendantes" viram **proponentes**, sempre 2. O candidato anexa a carta de cada um, e os 3 assinam (`02`, `02b`, `02c`). Quem pede passa a ser o **candidato** |
| Registro | O membro escolhe o seu **lado** (comprador ou vendedor) em `05`. Saem tipo, classificação, safra e modalidade de liquidação. Entra o **prazo de entrega em mês e ano** (`06`, `06b`, `07`, `07b`) |
| Negociação | Novo estado **em negociação**, com ou sem Mesa (`04`, `05b`, `07`) |
| Limite e risco | Telas novas `21`, `21b`, `22`, `22b`; limite visível ao membro em `04`, `07` e `11`; limite inicial na aprovação (`12c`) |
| Armazém e árbitro | Armazém **geral** só para entrega, sem virar membro automático (`18`, `18b`). Termo **impedido** para o árbitro (`19`) |
| Liquidação | Entrega e troca de partes em `10b` e `23`. Seguro de performance como opcional em `07` |

### Ampliação de 01/10/2026, depois da reunião de 24/09 com o cliente

A reunião trouxe mudança de modelo, não só ajuste de campo. Ver `docs/consolidacao-rev5.md` e `planejamento/atas-reunioes-wado.md`. Mudança de estratégia: o mockup cresce para mostrar **tudo** o que o cliente descreveu, inclusive o que ainda não tem resposta nas pendências — cada bloco novo é precificado separado depois (`docs/plano-do-projeto.md`, "Fase 4"). No mesmo dia, uma segunda rodada de ajustes revisou a UX da Mesa de Negociação e duas telas — ver "Ajustes finos" abaixo.

| Tema | O que mudou no mockup |
|---|---|
| Entrada no clube | Virou **proposta de adesão**: de 1 a 3 recomendantes assinam, comitê de admissão decide (telas `02`, `02c`, `12`, `12b`, `12c`, `13`) |
| Onboarding | Nova tela `03b`: assinatura dos termos do clube no primeiro acesso |
| Assinatura do registro | Virou **envelope único** (contrato + CPR), janela curta configurável, resumo rápido com documentos a um clique (telas `08`, `08b`, `08c`, `09`, `09a`, `09b`) |
| Mesa de Negociação | Deixa de ser uma sala isolada: acompanha o fluxo de criação do registro do início à assinatura, como painel fixo (telas `05b`, `06b`, `07b`, `09-mesa`, `09-mesa-concluido`) |
| Registro — formulário | Novo fluxo de **4 etapas** (antes 3): Partes → Mesa de Negociação → Objeto e valor → Revisão. Campos reduzidos ao essencial, liquidação só física por ora |
| Armazéns, árbitros, amostras | Três telas novas: `18`/`18b`, `19`, `20`, com localidade padrão Varginha/MG e região |

### Ajustes finos de 01/10/2026, mesmo dia

Depois de ver a primeira versão ampliada, o cliente pediu estes ajustes, já aplicados:

| Tela | Ajuste |
|---|---|
| `02` | Recomendantes deixam de ser 2 fixos: agora de 1 a 3, cada um com telefone e texto de recomendação. Anexos viram área de arrastar/selecionar, múltiplos arquivos |
| `08` | Para de mostrar o documento inteiro. Mostra resumo do acordado; documentos completos ficam a um clique (`08b`, `08c`) |
| Localidade mockada | Trocada de Patrocínio/MG e Franca/SP para **Varginha/MG** (Sul de Minas), com Cerrado Mineiro e Mogiana como as outras regiões de exemplo |
| Mesa de Negociação | UX refeita: entra como etapa 2 do fluxo de criação (não mais uma sala à parte perto da assinatura), mostra participantes e formulário lado a lado como tela compartilhada, e mantém a câmera ligada até a assinatura e o registro na B3. A antiga tela `09-video.html` foi removida |

### Ajustes de 12/09/2026, depois dos estudos

| Tela | O que mudou |
|---|---|
| `02b` | Prazo de análise passou de dois para três dias úteis, alinhado à regra RN-88 |
| `06` | Campos do registro da B3 (situação, origem, fazenda, acondicionamento, finalidade, indexador, vencimento, UF, garantia). Bebida, peneira, observações e frete marcados como "só no contrato" |
| `08` | Cláusula de assinatura neutra, sem citar ICP-Brasil. O botão leva à tela 9a |
| `09a`, `09b` | Novas. As duas formas de assinar, para comparar na reunião |
| `09`, `11` | Mostram a opção A, código por e-mail |
| `15` | Ordenada pelo prazo legal de 30 dias úteis. Coluna de prazo e exemplo de por que a ordem muda |
| `16` | Mostra data de emissão e prazo legal restante |
| `16a` | Mostra a consulta à B3 antes do reenvio |

---

## As telas

### Públicas
| Arquivo | Tela |
|---|---|
| `01-landing.html` | Landing discreta |
| `02-solicitar-convite.html` | Propor adesão, com os 2 recomendantes |
| `02b-solicitacao-enviada.html` | Confirmação da proposta, enviada aos recomendantes |
| `02c-assinar-indicacao.html` | Recomendante assina a indicação |
| `03-login.html` | Login |
| `03b-aceite-termos.html` | Aceite dos termos do clube, primeiro acesso |

### Membro
| Arquivo | Tela |
|---|---|
| `04-meus-registros.html` | Meus registros, com situação simplificada |
| `05-novo-registro-partes.html` | Novo registro, etapa 1 de 4: partes. Qualquer parte membro pode criar |
| `05c-novo-registro-partes-corretor.html` | Etapa 1 de 4, com corretor logado: papel de intermediário marcado, informa os dois lados |
| `05b-sessao-negociacao.html` | Etapa 2 de 4: decidir se abre a Mesa de Negociação |
| `06-novo-registro-objeto.html` | Etapa 3 de 4, sem Mesa: objeto, safra, quantidade, preço, liquidação (só física), armazém, entrega |
| `06b-novo-registro-objeto-mesa.html` | Etapa 3 de 4, com Mesa: mesmo formulário, preenchido com todos vendo em tempo real |
| `07-novo-registro-revisao.html` | Etapa 4 de 4, sem Mesa: revisão |
| `07b-novo-registro-revisao-mesa.html` | Etapa 4 de 4, com Mesa: revisão com a chamada ativa, vai direto para a assinatura |
| `08-previa-documento.html` | Resumo rápido do envelope (contrato + CPR), sem mostrar o texto inteiro |
| `08b-documento-contrato.html` | Contrato completo, a um clique do resumo |
| `08c-documento-cpr.html` | CPR completa, a um clique do resumo |
| `09b-assinar-certificado.html` | Assinar o envelope com certificado digital ICP-Brasil, em token, nuvem ou arquivo |
| `09-assinatura.html` | Envelope de assinatura, sem Mesa, janela curta, status por parte |
| `09-assinatura-mesa.html` | Envelope de assinatura, com Mesa ativa: assina sem sair da chamada |
| `09-assinatura-mesa-concluido.html` | Negócio fechado e já registrado na B3, Mesa ainda ativa |
| `10-detalhe-registro.html` | Detalhe do registro, linha do tempo |
| `10b-detalhe-registro-concluido.html` | Detalhe de um registro já registrado |
| `11-minha-conta.html` | Minha conta |

### Backoffice
| Arquivo | Tela |
|---|---|
| `12-fila-cadastros.html` | Propostas de adesão, por situação (assinatura dos recomendantes, fila do comitê, diligência) |
| `12b-relatorio-comite.html` | Relatório para a reunião semanal do comitê de admissão |
| `12c-registrar-decisao-comite.html` | Materializar a decisão do comitê, com parecer opcional |
| `13-detalhe-solicitacao.html` | Detalhe da proposta: proponente, 2 recomendantes, diligência |
| `14-todos-os-registros.html` | Todos os registros, com situação interna e a que o membro vê |
| `15-fila-pendencias.html` | Fila de pendências |
| `16-resolucao-falha.html` | Resolução de falha, os quatro caminhos |
| `16a-confirmar-reenvio.html` | Caminho 1, reenviar sem mudar nada |
| `16b-confirmar-correcao.html` | Caminho 2, corrigir o envio |
| `16c-confirmar-reassinatura.html` | Caminho 3, novo documento e nova assinatura |
| `16d-confirmar-cancelamento.html` | Caminho 4, cancelar |
| `17-auditoria.html` | Auditoria, os dois registros |

### Escopo novo (reunião de 24/09, ainda sem preço fechado)
| Arquivo | Tela |
|---|---|
| `18-armazens.html` | Armazéns credenciados, por região |
| `18b-credenciar-armazem.html` | Analisar um pedido de credenciamento |
| `19-arbitros.html` | Árbitros classificadores, com a regra de imparcialidade |
| `20-amostras.html` | Fluxo de amostras: coleta, classificação, aprovação |

---

## Roteiro sugerido da reunião

Uma hora e meia, nesta ordem. O caminho de erro continua sendo o mais importante; o escopo novo é para o cliente ver a ideia completa, não para fechar preço na hora.

**1. Propor adesão, 15 minutos.**
`01` → `02` → `02c` → `02b` → `12` → `12b` → `12c` → `13` → `03` → `03b`

Perguntas a fazer: como um recomendante que não é membro assina (1.27)? O comitê precisa de conta própria, ou o relatório + a tela 12c bastam (1.28)?

**2. Criar e assinar um envelope, sem Mesa, 15 minutos.**
`04` → `05` → `05b` (sem mesa) → `06` → `07` → `08` → `08b`/`08c` → `09b` → `09` → `10`

Perguntas a fazer: falta algum campo no formulário? A janela de 15 minutos é realista? E se uma parte precisar de dois signatários (1.31)?

Em seguida, abrir `05c` e mostrar o mesmo início com um corretor logado.

**2b. O mesmo caminho, com a Mesa de Negociação, 10 minutos.**
`05b` (iniciar mesa) → `06b` → `07b` → `09-assinatura-mesa` → `09-assinatura-mesa-concluido`

Perguntas a fazer: a UX de tela compartilhada faz sentido? Vale manter a câmera ligada até o registro na B3 confirmar?

**3. O membro vê pouco, e isso é decisão de produto, 5 minutos.**
Parar em `04` e mostrar as cinco situações. Confirmar que o cliente concorda que o membro nunca veja recusa técnica.

**4. O caminho de erro, 20 minutos. Continua o mais importante.**
`15` → `16` → e percorrer os quatro caminhos: `16a`, `16b`, `16c`, `16d`

Perguntas a fazer, nesta ordem:
- Quem é avisado quando um contrato cai na fila de pendências, por qual canal e em quanto tempo?
- A pré-validação antes da assinatura (que evita assinar algo que vai falhar na B3) cobre o que o cliente quis dizer com "erro grave"?

**5. Escopo novo, 15 minutos. Para validar a ideia, não para fechar preço.**
`18` → `18b` → `19` → `20`

Perguntas a fazer: washout e liquidação por diferença fazem sentido numa CPR física (1.36)? Quem credencia um armazém (1.37)? Como o sistema sabe o vínculo de um árbitro (1.38)?

**6. Fechar com prova e conta, 10 minutos.**
`17` e `11`

---

## Perguntas que o mockup levantou

A lista completa e atualizada está em `docs/pendencias.md`. As que nasceram desta ampliação de 01/10 (reunião de 24/09) são as 1.27 a 1.39 e 2.21 a 2.24. Abaixo, o registro original das perguntas que o mockup de 12/09 levantou, ainda válido.

### Sobre campos e cadastro
1. **Os campos reais do cadastro.** O mockup usa nome, CPF, e-mail, telefone, propriedade e município. Para emitir CPR de café, provavelmente falta matrícula do imóvel, área, e possivelmente CAR. Cada campo com validação é trabalho na Fase 1.
2. **Quem pode alterar o próprio cadastro.** Nome, CPF e propriedade aparecem dentro de contratos já registrados na B3. A tela 11 assume que alteração passa por aprovação. Confirmar.
3. **Segundo fator para o membro.** O backoffice tem, está no escopo. O membro comum já usa certificado digital para assinar; decidir se também precisa de segundo fator para entrar.

### Sobre a fila de propostas de adesão
4. **Critérios de aprovação e recusa.** Não existe nenhum escrito. Sem critério, a decisão vira pessoal e não tem como auditar.
5. ~~Indicação por membro é obrigatória?~~ **Superada em 24/09:** agora são 2 recomendantes obrigatórios, que assinam.
6. ~~Candidato recusado pode pedir de novo?~~ **Respondida em 24/09: sim, sem carência e sem limite.**
7. **Prazo da fila.** Depende do ciclo semanal do comitê — ver pendência 1.20/1.30.

### Sobre a resolução de falhas, as mais caras
8. **Quem é avisado quando um contrato falha**, por qual canal, e com que prazo de resposta. Continua em aberto (pendência 1.19).
9. **Quem é o dono de uma pendência sem responsável.** A tela 15 mostra um contrato parado há seis horas sem ninguém atribuído.
10. **Caminhos 3 e 4 precisam de duas pessoas?** Reassinatura e cancelamento mexem em contrato assinado de valor alto. O desenho atual deixa uma pessoa só decidir.
11. **Quem pode editar o envio à B3.** É a ação de maior poder do sistema e hoje o desenho não distingue papel técnico de operador.
12. **O texto do e-mail de reassinatura.** Sem um texto pensado, a parte liga achando que houve fraude.

### Sobre papéis
13. **Três papéis de backoffice ou dois.** Vale cerca de 6 horas na Fase 1. **Nova, 24/09:** existe ainda a pergunta se o comitê de admissão precisa de um sexto papel próprio (pendência 1.28).

### Sobre auditoria
14. **Retenção dos dois registros.** Tem regra de LGPD e tem custo.
15. **Aviso de exportação em massa.** A tela 17 mostra uma exportação de 214 registros. Nada avisou ninguém na hora.
16. **O membro pode ver quem olhou o contrato dele?** Transparência a favor dele, desconforto para a operação.
