#!/usr/bin/env bash
# Réinitialise le mot de passe admin Grafana depuis GRAFANA_ADMIN_PASSWORD (.env).
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/HEALTHAIMSRP}"
CONTAINER="${GRAFANA_CONTAINER:-healthaim_grafana}"

cd "$DEPLOY_PATH"

if [[ ! -f .env ]]; then
  echo "Erreur : .env introuvable dans $DEPLOY_PATH"
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

if [[ -z "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
  echo "Erreur : GRAFANA_ADMIN_PASSWORD manquant dans .env"
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Erreur : conteneur $CONTAINER non démarré"
  exit 1
fi

echo "==> Réinitialisation du mot de passe admin Grafana..."
docker exec -i "$CONTAINER" grafana cli admin reset-admin-password "$GRAFANA_ADMIN_PASSWORD"
echo "==> Terminé. Connexion : utilisateur admin + mot de passe du .env"
