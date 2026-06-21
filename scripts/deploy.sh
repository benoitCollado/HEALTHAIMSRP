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
# sur 127.0.0.1:9000 ou 127.0.0.1:9100. Le port 9100 est garde pour
# node-exporter quand la stack monitoring est active.
export MINIO_PORT="127.0.0.1:19100"
export MINIO_CONSOLE_PORT="127.0.0.1:19101"
export MINIO_PUBLIC_ENDPOINT="127.0.0.1:19100"

# MongoDB microservice IA — valeur par defaut Compose si absente du .env serveur
if ! grep -qE '^MONGODB_URI=.+' .env; then
  echo "==> MONGODB_URI absent du .env — utilisation de mongodb://mongodb:27017 (Compose)"
  export MONGODB_URI="mongodb://mongodb:27017"
fi

wait_mongodb() {
  echo "==> Attente MongoDB (healthcheck)..."
  for i in $(seq 1 30); do
    if docker compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping').ok" 2>/dev/null | grep -q '^1$'; then
      echo "    MongoDB operationnel."
      return 0
    fi
    if [[ "$i" -eq 30 ]]; then
      echo "Erreur : MongoDB ne repond pas apres 30 tentatives."
      docker compose logs --tail=50 mongodb
      return 1
    fi
    sleep 2
  done
}

wait_microservice_ia() {
  echo "==> Attente microservice_ia (/health)..."
  for i in $(seq 1 30); do
    if docker compose exec -T microservice_ia python -c \
      "import json, urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8090/health', timeout=3); \
       b=json.loads(r.read()); assert b.get('persistence') in ('mongodb', 'memory')" \
      > /dev/null 2>&1; then
      echo "    microservice_ia operationnel."
      return 0
    fi
    if [[ "$i" -eq 30 ]]; then
      echo "Erreur : microservice_ia ne repond pas sur /health apres 30 tentatives."
      docker compose logs --tail=50 microservice_ia
      return 1
    fi
    sleep 2
  done
}

echo "==> Arret des services app (sans MongoDB — donnees conservees)..."
docker compose stop backend frontend minio microservice_ia || true
docker compose rm -f backend frontend minio microservice_ia || true

echo "==> Demarrage MongoDB..."
docker compose up -d mongodb
wait_mongodb

echo "==> Build image microservice_ia..."
docker compose build microservice_ia

echo "==> Migration / initialisation MongoDB (index idempotents)..."
docker compose run --rm --no-deps microservice_ia python scripts/init_mongodb.py

echo "==> Demarrage microservice_ia..."
docker compose up -d microservice_ia
wait_microservice_ia

echo "==> Build et redemarrage minio, backend, frontend..."
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
docker compose ps mongodb microservice_ia minio backend frontend

echo "==> Deploiement termine avec succes."
