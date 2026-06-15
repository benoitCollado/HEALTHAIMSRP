#!/usr/bin/env bash
# Script execute sur le serveur de production via SSH (GitHub Actions).
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/HEALTHAIMSRP}"

if [[ ! -d "$DEPLOY_PATH" ]]; then
  echo "Erreur : le repertoire de deploiement '$DEPLOY_PATH' n'existe pas."
  exit 1
fi

cd "$DEPLOY_PATH"

echo "==> Mise a jour du code (branche main)..."
git fetch origin main
git reset --hard origin/main

if [[ ! -f .env ]]; then
  echo "Erreur : fichier .env manquant dans $DEPLOY_PATH"
  echo "Creez-le a partir de .env.example avant le premier deploiement."
  exit 1
fi

# La base applicative est externe (PostgreSQL manage, ex. Neon).
# DATABASE_URL doit etre renseigne dans .env sur le serveur, pas dans GitHub Actions.
if ! grep -qE '^DATABASE_URL=.+' .env; then
  echo "Erreur : DATABASE_URL manquant ou vide dans .env"
  echo "Renseignez la connection string Neon (dashboard Neon -> Connection Details)."
  exit 1
fi

if ! grep -qE '^SECRET_KEY=.+' .env; then
  echo "Erreur : SECRET_KEY manquant ou vide dans .env"
  exit 1
fi

# Ces exports priment sur un ancien .env serveur qui exposerait encore MiniIO
# sur 127.0.0.1:9000 ou 127.0.0.1:9100, ports souvent deja utilises.
export MINIO_PORT="127.0.0.1:9100"
export MINIO_CONSOLE_PORT="127.0.0.1:9101"
export MINIO_PUBLIC_ENDPOINT="127.0.0.1:9100"

echo "==> Arret des services app (minio, backend, frontend) - Airflow non inclus..."
docker compose stop backend frontend minio
docker compose rm -f backend frontend minio

echo "==> Build et redemarrage (minio, backend, frontend uniquement)..."
docker compose up -d --build minio backend frontend

echo "==> Attente du backend (connexion Neon via DATABASE_URL)..."
for i in $(seq 1 30); do
  if docker compose exec -T backend python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" \
    > /dev/null 2>&1; then
    echo "    Backend operationnel (health OK, BDD externe joignable)."
    break
  fi
  if [[ "$i" -eq 30 ]]; then
    echo "Erreur : le backend ne repond pas sur /health apres 30 tentatives."
    echo "Verifiez DATABASE_URL (Neon) et les logs ci-dessous."
    docker compose logs --tail=50 backend
    exit 1
  fi
  sleep 2
done

echo "==> Etat des conteneurs app :"
docker compose ps minio backend frontend

echo "==> Deploiement termine avec succes."
