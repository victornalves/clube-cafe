# Deploy do MVP

Uma VM e2-micro na GCP, projeto `camara-cafe-dev` (conta `victornalves@gmail.com`), com Docker Compose: Postgres, app e Caddy.

**Endereço:** <https://35-196-32-152.sslip.io>. O sslip.io resolve o nome para o IP fixo da VM, e isso basta para o Caddy emitir um certificado Let's Encrypt. Quando houver domínio próprio, troque `DOMINIO` em `deploy/.env.prod` e republique.

## Comandos

Rodar da raiz do repositório. O gcloud precisa estar na configuração `camara`, o que `.envrc` (direnv) e `.claude/settings.json` já garantem; o script recusa qualquer outra conta ou projeto.

| Comando | O que faz |
|---|---|
| `deploy/gcp.sh publicar` | Envia o **último commit** (não o que está sem commit) e reconstrói na VM. Leva de 1 a 15 min: a etapa "exporting layers" é lenta no disco standard. A versão anterior fica no ar até o fim, e há uns 10 s de 502 na troca |
| `deploy/gcp.sh demo` | Zera o banco da VM e monta os oito cenários de demonstração. Rodar logo antes de apresentar: a janela do envelope do CRTC-2026-0008 é de 60 min |
| `deploy/gcp.sh logs` | Últimas 50 linhas do app |
| `deploy/gcp.sh criar` | Cria IP fixo, firewall e VM. Já foi rodado em 04/11/2026; é idempotente |

## Segredos

`deploy/.env.prod`, fora do git, gerado na primeira publicação: senha do Postgres, segredo de sessão, senha dos usuários de demonstração e o domínio. A senha de demonstração (`SENHA_DEMO`) vale para todos os usuários do README da raiz. Se o arquivo se perder, a VM tem a cópia em `/opt/clube-cafe/deploy/.env.prod`.

## Custos

| Item | Custo |
|---|---|
| VM e2-micro em us-east1 | Free tier |
| Disco standard de 30 GB | Free tier |
| IPv4 externo fixo | ~US$ 3,65/mês |
| Tráfego de saída | 1 GB/mês grátis, sobra para demonstração |

Alerta de orçamento de **R$ 50/mês** no projeto, com aviso em 50%, 90% e 100%.

## Limitações conhecidas

- **Login de demonstração ligado** (`LOGIN_DEMO=true` em `deploy/.env.prod`, desde 05/11/2026): quem tiver o link entra como qualquer persona, inclusive a operadora. Para desligar, `LOGIN_DEMO=false` e republicar.
- **1 GB de RAM**, com 2 GB de swap. Em uso, o app ocupa ~150 MB e o Postgres ~50 MB. O build é o momento mais pesado.
- **Servidor nos EUA**: ~130 ms de latência do Brasil, e o NiceGUI faz uma ida e volta por interação. Perceptível, aceitável para demonstração.
- **Só dado fictício**: sem criptografia de aplicação, sem MFA e sem backup do banco.
- **Uma instância só**: o NiceGUI guarda o estado da tela em memória e não escala horizontalmente sem mudança.
