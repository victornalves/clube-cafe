# Mockup do Clube do Café

Artefato da reunião de validação de escopo, Fase 0. HTML puro, sem framework, sem build.

**Não tem identidade visual, de propósito.** Se o cliente vir cor e tipografia, a reunião vira conversa sobre a cor do botão em vez de sobre o fluxo. As direções visuais rodam separado, na frente 5, e só entram depois que o fluxo estiver aprovado.

Abrir `index.html` no navegador. Todos os links entre telas funcionam.

---

## As telas

### Públicas
| Arquivo | Tela |
|---|---|
| `01-landing.html` | Landing discreta |
| `02-solicitar-convite.html` | Solicitar convite |
| `02b-solicitacao-enviada.html` | Confirmação do pedido |
| `03-login.html` | Login |

### Membro
| Arquivo | Tela |
|---|---|
| `04-meus-registros.html` | Meus registros, com situação simplificada |
| `05-novo-registro-partes.html` | Novo registro, etapa 1: partes |
| `06-novo-registro-objeto.html` | Novo registro, etapa 2: objeto, data, valor |
| `07-novo-registro-revisao.html` | Novo registro, etapa 3: revisão |
| `08-previa-documento.html` | Pré-visualização do documento |
| `09-assinatura.html` | Assinatura, status por parte |
| `10-detalhe-registro.html` | Detalhe do registro, linha do tempo |
| `10b-detalhe-registro-concluido.html` | Detalhe de um registro já registrado |
| `11-minha-conta.html` | Minha conta |

### Backoffice
| Arquivo | Tela |
|---|---|
| `12-fila-cadastros.html` | Fila de aprovação de cadastros |
| `13-detalhe-solicitacao.html` | Detalhe da solicitação, aprovar ou recusar |
| `14-todos-os-registros.html` | Todos os registros, com situação interna e a que o membro vê |
| `15-fila-pendencias.html` | Fila de pendências |
| `16-resolucao-falha.html` | Resolução de falha, os quatro caminhos |
| `16a-confirmar-reenvio.html` | Caminho 1, reenviar sem mudar nada |
| `16b-confirmar-correcao.html` | Caminho 2, corrigir o envio |
| `16c-confirmar-reassinatura.html` | Caminho 3, novo documento e nova assinatura |
| `16d-confirmar-cancelamento.html` | Caminho 4, cancelar |
| `17-auditoria.html` | Auditoria, os dois registros |

---

## Roteiro sugerido da reunião

Uma hora, nesta ordem. O caminho de erro é o que menos foi discutido e é onde está o trabalho diário do backoffice, então guarde tempo para ele.

**1. A jornada feliz do membro, 15 minutos.**
`01` → `02` → `02b` → `03` → `04` → `05` → `06` → `07` → `08` → `09` → `10b`

Pergunta a fazer: falta algum campo no formulário? Sobra algum?

**2. O membro vê pouco, e isso é decisão de produto, 5 minutos.**
Parar em `04` e mostrar as cinco situações. Confirmar que o cliente concorda que o membro nunca veja recusa técnica.

**3. A entrada no clube pelo lado de dentro, 10 minutos.**
`12` → `13`

Pergunta a fazer: quais são os critérios de aprovação e recusa? Hoje não existe nenhum escrito.

**4. O caminho de erro, 25 minutos. É o mais importante.**
`15` → `16` → e percorrer os quatro caminhos: `16a`, `16b`, `16c`, `16d`

Perguntas a fazer, nesta ordem:
- Quem é avisado quando um contrato cai na fila de pendências, por qual canal e em quanto tempo?
- Qual prazo é aceitável para um contrato ficar parado?
- Cancelar um contrato de R$ 1,7 milhão deveria exigir uma segunda pessoa aprovando?

**5. Auditoria, 5 minutos.**
`17`

Pergunta a fazer: o membro pode ver quem do backoffice abriu o contrato dele?

---

## Perguntas que o mockup levantou

Coisas que só apareceram quando as telas precisaram existir de verdade. Cada uma delas é escopo que ainda não está fechado.

### Sobre campos e cadastro
1. **Os campos reais do cadastro.** O mockup usa nome, CPF, e-mail, telefone, propriedade e município. Para emitir CPR de café, provavelmente falta matrícula do imóvel, área, e possivelmente CAR. Cada campo com validação é trabalho na Fase 1.
2. **Quem pode alterar o próprio cadastro.** Nome, CPF e propriedade aparecem dentro de contratos já registrados na B3. A tela 11 assume que alteração passa por aprovação. Confirmar.
3. **Segundo fator para o membro.** O backoffice tem, está no escopo. O membro comum já usa certificado digital para assinar; decidir se também precisa de segundo fator para entrar.

### Sobre a fila de cadastros
4. **Critérios de aprovação e recusa.** Não existe nenhum escrito. Sem critério, a decisão vira pessoal e não tem como auditar.
5. **Indicação por membro é obrigatória?** O formulário da tela 2 pede, mas não diz se é exigência.
6. **Candidato recusado pode pedir de novo?** Depois de quanto tempo?
7. **Prazo da fila.** A tela 2b promete "dois dias úteis" ao candidato. Nada no backoffice cobra esse prazo.

### Sobre a resolução de falhas, as mais caras
8. **Quem é avisado quando um contrato falha**, por qual canal, e com que prazo de resposta. Hoje não existe alerta: alguém precisa abrir a tela 15 por conta própria. Isto está marcado como "a definir com o cliente" na máquina de estados e continua em aberto.
9. **Quem é o dono de uma pendência sem responsável.** A tela 15 mostra um contrato parado há seis horas sem ninguém atribuído.
10. **Caminhos 3 e 4 precisam de duas pessoas?** Reassinatura e cancelamento mexem em contrato assinado de valor alto. O desenho atual deixa uma pessoa só decidir.
11. **Quem pode editar o envio à B3.** É a ação de maior poder do sistema e hoje o desenho não distingue papel técnico de operador.
12. **O texto do e-mail de reassinatura.** O membro assinou há quatro dias e vai receber um pedido para assinar de novo. Sem um texto pensado, ele liga achando que houve fraude.

### Sobre papéis
13. **Três papéis de backoffice ou dois.** A tela 13 é onde a diferença aparece: o aprovador de cadastro precisa enxergar termos comerciais? Vale cerca de 6 horas na Fase 1.

### Sobre auditoria
14. **Retenção dos dois registros.** Tem regra de LGPD e tem custo.
15. **Aviso de exportação em massa.** A tela 17 mostra uma exportação de 214 registros. Nada avisou ninguém na hora.
16. **O membro pode ver quem olhou o contrato dele?** Transparência a favor dele, desconforto para a operação.
