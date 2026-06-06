#!/usr/bin/env bash
# Script exécuté sur le serveur de production via SSH (GitHub Actions).
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/HEALTHAIMSRP}"

if [[ ! -d "$DEPLOY_PATH" ]]; then
  echo "Erreur : le répertoire de déploiement '$DEPLOY_PATH' n'existe pas."
  exit 1
fi

cd "$DEPLOY_PATH"

echo "==> Mise à jour du code (branche main)..."
git fetch origin main
git reset --hard origin/main

if [[ ! -f .env ]]; then
  echo "Erreur : fichier .env manquant dans $DEPLOY_PATH"
  echo "Créez-le à partir de .env.example avant le premier déploiement."
  exit 1
fi

# La base applicative est externe (PostgreSQL managé, ex. Neon).
# DATABASE_URL doit être renseigné dans .env sur le serveur, pas dans GitHub Actions.
if ! grep -qE '^DATABASE_URL=.+' .env; then
  echo "Erreur : DATABASE_URL manquant ou vide dans .env"
  echo "Renseignez la connection string Neon (dashboard Neon -> Connection Details)."
  exit 1
fi

if ! grep -qE '^SECRET_KEY=.+' .env; then
  echo "Erreur : SECRET_KEY manquant ou vide dans .env"
  exit 1
fi

echo "==> Arrêt des services app (backend, frontend) — Airflow non inclus..."
docker compose stop backend frontend
docker compose rm -f backend frontend

echo "==> Build et redémarrage (backend, frontend uniquement)..."
docker compose up -d --build backend frontend

echo "==> Attente du backend (connexion Neon via DATABASE_URL)..."
for i in $(seq 1 30); do
  if docker compose exec -T backend python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=3)" \
    > /dev/null 2>&1; then
    echo "    Backend opérationnel (health OK, BDD externe joignable)."
    break
  fi
  if [[ "$i" -eq 30 ]]; then
    echo "Erreur : le backend ne répond pas sur /api/health après 30 tentatives."
    echo "Vérifiez DATABASE_URL (Neon) et les logs ci-dessous."
    docker compose logs --tail=50 backend
    exit 1
  fi
  sleep 2
done

echo "==> État des conteneurs app :"
docker compose ps backend frontend

echo "==> Déploiement terminé avec succès."
