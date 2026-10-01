# CLUBE DO CAFÉ \- Com Wado Aranha

Acerto por telefone com Wado:

- R\$300 a hora minha, ao invés de R\$350 da minha proposta inicial  
- No futuro, um projeto de escopo fechado  
- Envio as horas trabalhadas no final do mês, com descritivo.

# Reunião 1: 10 de setembro de 2026 \- 14:30

Gesiel Barros, da [souzabarquette.adv.br](http://souzabarquette.adv.br). Vinicius não pode entrar.  
Oswaldo Aranha Neto  
Victor

7 minutos de de atraso

Escopo:

1) Primeiro: Registro do contrato  
   1) Precisa ser válido, para ter certificado digital. Como um docusign.

   2) Para ter validade jurídica, assinado por partes de duas testemunhas. Digital, sem testemunhas funciona se tiver certificado digital.

   3) Podemos integrar com um player de assinatura digital

2) CPR  
   1) Precisa ser depositado ou registrado numa entidade do banco central  
      1) B3, CRDC, e outra  
      2) Funciona como uma conta bancária, para cada player.  
      3) O escritório já tem isso, e podemos oferecer a conta deles para o clube

      4) Sistema: novo mercado  
      5) Hoje, ele faz tudo manual

      6) Documentaçõa de API  
         1) [https://developers.b3.com.br/apis](https://developers.b3.com.br/apis) buscar CPR

- CPR é um documento que nós emitimos, e enviamos as informações para a B3  
  - Nós definimos o formato. Só o payload que enviamos para lá

Existe CPR como nao produtos, outros papeis também

Corretor que é quem vai preencher

Comprador e vendedor só assinam

Proposta de ingressar como sócio:

- Primeiro é cadastrado  
- Depois, examinada para ser aprovada ou não  
- A “pessoa” que ingressou pode assumir diferentes papeis \- validar isso

É possível ter transação sem corretor \- é opcional.

- Sistema precisa incentivar que tenha corretor, mas não exigir.

Registro é só entre sócios do clube. Ninguém pode estar de fora

Avaliar: como é o preenchimento \- que compra ou quem vende, e vice e versa.

**Cronograma do lado jurídico:**

- Está em definição de modelo de cobrança \- vai demorar mais tempo

**TODO:**

- Fazer planejamento da arquitetura

- Falar com Gesiel sobre B3, autenticação, cadastros e sandbox

- Pesquisar sobre plataforma de assinatura digital

# 

# Reunião 2: 24/09 \- 15:30

Victor \+ Wado

O time de ADV fez análise da CPR errada e contrato também.

Ideia que cobrisse operações de barter, mas pelo visto não.

- É um contrato financeiro apenas. (CPR financeira)  
- Fora do escopo do clube, que é só CPR física

- Isso nao atrapalha o projeto

Apenas o Seguro está em aberto.

Sobre fluxos:

- Palavra não é “convite". O ideal seria mais como “proposta de adesão”

- Usuário sim, faz a proposta, preenchendo um formulário explicando quem é ela.

  - Neste formulário, ele tem que indicar 2 proponentes precisam recomendar entrada de um candidato no sistema- apenas 2 nomes no pedido (podem ser membros ou nao, pq pode ser alguém de renome fora do clube)

  - Estes outros 2 que recomendam, também precisam assinar a proposta também.

    - Eles recebem um email para confirmar a aprovação

    - Assinam essa indicação \- usamos o mesmo processo para assinatura, como docusign.

  - Com os 3 assinados (proponente \+ 2 indicações) entra na fila de avaliação do **comite de admissão** \- usuários que tem este role \- 3 pessoas no comite, Wado e \+2) \- avaliar se isso ficará dinâmico ou fixo.

    - **Comitê de admissão** deve se reunir 1x por semana

- Processo de “onboard":  
  - Avaliar o que será anexado à proposta, para apreciação do comitê

  - Pode ter alguns anexos

  - Pode haver solicitações adicionais na análise. Não é provável que aconteça, mas a avaliação pode existir pedidos de dados adicionais.

  - São geradas dúvidas sobre o processo, solicitando novos dados ao proponente e aos que recomendam

- Na conclusão:  
  - Um clique só, feito pelo backoffice, para aprovação ou não do processo  
  - Dispara um e-mail com o resultado

- Sobre trava de documentos existentes:  
  - Não podemos bloquear automaticamente no processo.

  - Usuário pode fazer nova proposta, mesmo se já tiver sido rejeitado antes.

  - O pedido de criação de proposição não gera um usuário. E sim, uma base separada que o CPF pode estar duplicado.

- Porém, se tiver usuário ativo, aí nao podemos deixar duplicar. Direcionar para login

- Nao podemos usar o nome “sócio” pq na prática não será um clube

- Onboard do usuário:  
  - Temos que explicar como funciona.  
  - As transações que acontecem aqui, estão debaixo do contrato padrão do clube  
  - “Esta transação está sujeita às regras da empresa X (clube)”

- Registro  
  - Além do CPR, também contrato, etc

  - Processo em rascunho \- avaliar se precisa mesmo ou não.

  - Formulário:  
    - Comprador \+ vendedor (talvez o corretor)  
    - Quantidade  
    - Preço  
    - Prazo de entrega  
    - Ponto/condição de entrega (talvez)

  - Não existe negociação de cláusulas. Sempre é um template.  
    - “Qualidade” já está fixa no contrato

  - Tempo de “Aguardar assinatura” tem que ser curto \- algo em torno de alguns minutos \- 5 ou 10 minutos.

  - Tem que avaliar que a assinatura não será só do contrato, mas talvez novos outros documentos  
    - Como o CPR ou outros artefatos gerados

    - Se assinar o contrato, isso se aplica a todo o resto.

    - A assinatura é de um envelope, na verdade, com vários docs

    - Evitar que tenham que assinar mais de uma vez

  - Gerar cópia de documentos para todos os envolvidos

  - Cancelado: negócio não existiu

  - Rascunho: pode ser até um template de negociação:  
    - Pode ter até um visual amigável de mostrar o preenchimento e forma de negociação.

  - Avaliar casos onde uma parte necessita mais de uma assinatura:  
    - Empresas que necessitam mais de uma

- Ideia nova: negociação com vídeo \- facilitador  
  - Adicionar um chat/ google meet dentro da aplicação para realizar processo de negociação por vídeo \- usar ferramenta whitelabel

  - Um serviço adicional para o clube:  
    - Oferece um whereby, um meeting room para os papéis envolvidos.

    - Podem até assinar por ali, como se estivessem um na frente do outro

- Registro no backoffice:  
  - Cancelado, motivo de cancelamento, não é necessário registrar  
  - Wado não quer saber se houve tentativas de registro, mas não efetivou.

  - Falhar com a B3 é um erro grave\!  
    - Isso é um risco para o clube  
    - As partes assumiram o contrato, e este contrato não pode ser void devido a um erro técnico ou com B3

    - O fluxo EM\_CORREÇÃO é MUITO danoso para o clube. Então, temos que avaliar muito bem isso. Temos que investigar melhor como funciona com a B3.

  - Temos que mapear, o que pode dar errado no registro \- e mapear soluções já de antemao

- Novo escopo: armazéns  
  - Local de entrega da negociação

  - Só na liquidação física (não por diferença ou adiantado ou washout (desfaz o contrato))

  - Registro interno de árbitros para classificar o café

  - Árbitro imparcial: Não deixar árbitro que trabalhe para alguma empresa envolvida na negociação

  - Armazéns credenciados  
    - Fluxo de credenciamento também

  - Fluxo de amostras  
    - Aprovação de amostras

  - No cadastro do registro:  
    - Em local de entrega, escolher  
      - Região  
      - Armazens cadastrados desta regiao

- Sobre mudanças de registros:  
  - O que acontece se mudar a qualidade na entrega? Só renegocia o preço?

  - Pergunta: é possível mudar um registro realizado? Ou só cancelar e refazer? Um aditivo?

  - Como lidar com washout, mudança de local de entrega, aditivos?

- Serviço do clube fora da plataforma:  
  - Serviço de arbitragem e classificação:  
    - Se tiver litígio, os membros podem escalar para um time do clube fazer um avaliação \- um laudo

        
- Sobre assinatura:  
  - Nao precisamos mostrar o contrato preenchido

  - Temos que ser mais como assinatura de contratos futuros, como compra de ação: não mostra o contrato inteiro na hora  
  - O contrato já foi acordado assim que fez a conta na corretora (neste caso, no clube) \- vamos avaliar contratos futuro de café

  - Talvez, no início onboard, o usuário precisa confirmar e assinar os termos todos  
    - Se tiver atualização de termos, eles precisam reassinar

- Fechar horas dia 30 e pagamento pro dia 05 seguinte