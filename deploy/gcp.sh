#!/bin/sh
# Deploy do MVP numa VM e2-micro (free tier) no projeto camara-cafe-dev. Runbook: deploy/README.md
#
#   deploy/gcp.sh criar      cria IP fixo, firewall e VM (uma vez)
#   deploy/gcp.sh publicar   envia o commit atual e sobe os containers
#   deploy/gcp.sh demo       zera o banco da VM e monta os cenários de demonstração
#   deploy/gcp.sh logs       últimas linhas do app
set -eu

CONTA=victornalves@gmail.com
PROJETO=camara-cafe-dev
REGIAO=us-east1
ZONA=us-east1-b
VM=camara-mvp
IP_NOME=camara-ip
DIR=/opt/clube-cafe
cd "$(dirname "$0")/.."

# Nunca na conta ou no projeto da Demetria
[ "$(gcloud config get account 2>/dev/null)" = "$CONTA" ] || { echo "gcloud não está na conta $CONTA (use CLOUDSDK_ACTIVE_CONFIG_NAME=camara)"; exit 1; }
[ "$(gcloud config get project 2>/dev/null)" = "$PROJETO" ] || { echo "gcloud não está no projeto $PROJETO"; exit 1; }

g() { gcloud --project "$PROJETO" "$@"; }
na_vm() { g compute ssh "$VM" --zone "$ZONA" --quiet --command "$1"; }
ip() { g compute addresses describe "$IP_NOME" --region "$REGIAO" --format='value(address)'; }

criar() {
  g services enable compute.googleapis.com
  g compute addresses describe "$IP_NOME" --region "$REGIAO" >/dev/null 2>&1 \
    || g compute addresses create "$IP_NOME" --region "$REGIAO"
  g compute firewall-rules describe camara-web >/dev/null 2>&1 \
    || g compute firewall-rules create camara-web --allow tcp:80,tcp:443 --target-tags camara-web
  # e2-micro em us-east1 e disco standard de 30 GB: dentro do free tier (o IPv4 é cobrado à parte)
  g compute instances describe "$VM" --zone "$ZONA" >/dev/null 2>&1 \
    || g compute instances create "$VM" --zone "$ZONA" --machine-type e2-micro \
         --image-family debian-12 --image-project debian-cloud \
         --boot-disk-size 30GB --boot-disk-type pd-standard \
         --address "$(ip)" --tags camara-web
  echo "Esperando o SSH da VM..."
  until na_vm true 2>/dev/null; do sleep 5; done
  g compute scp deploy/vm-preparar.sh "$VM":/tmp/ --zone "$ZONA" --quiet
  na_vm 'sudo sh /tmp/vm-preparar.sh'
  echo "VM pronta em $(ip)"
}

env_prod() {
  # Segredos gerados uma vez e guardados só aqui (fora do git)
  [ -f deploy/.env.prod ] && return
  cat > deploy/.env.prod <<FIM
DOMINIO=$(ip | tr . -).sslip.io
POSTGRES_PASSWORD=$(openssl rand -hex 24)
STORAGE_SECRET=$(openssl rand -hex 32)
SENHA_DEMO=$(openssl rand -base64 9 | tr -d '/+=')
JANELA_ASSINATURA_MINUTOS=60
FIM
  chmod 600 deploy/.env.prod
}

publicar() {
  env_prod
  [ -z "$(git status --porcelain -- app migrations scripts deploy Dockerfile pyproject.toml uv.lock alembic.ini)" ] \
    || { echo "Há mudanças sem commit no código: o deploy envia só o que está commitado."; exit 1; }
  git archive --format=tar.gz -o /tmp/clube-cafe.tar.gz HEAD
  g compute scp /tmp/clube-cafe.tar.gz deploy/.env.prod "$VM":/tmp/ --zone "$ZONA" --quiet
  na_vm "sudo sh -c 'cd $DIR && tar xzf /tmp/clube-cafe.tar.gz && mv /tmp/.env.prod deploy/.env.prod && chmod 600 deploy/.env.prod \
    && docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build --remove-orphans \
    && docker image prune -f'"
  echo "Publicado: https://$(grep ^DOMINIO deploy/.env.prod | cut -d= -f2)  (commit $(git rev-parse --short HEAD))"
}

demo() {
  na_vm "sudo docker compose -f $DIR/deploy/docker-compose.prod.yml --env-file $DIR/deploy/.env.prod exec -T app python -m scripts.demo --apagar-tudo"
}

logs() {
  na_vm "sudo docker compose -f $DIR/deploy/docker-compose.prod.yml --env-file $DIR/deploy/.env.prod logs --tail 50 app"
}

"${1:?uso: deploy/gcp.sh criar|publicar|demo|logs}"
