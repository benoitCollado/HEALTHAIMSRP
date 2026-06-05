# CI/CD — HealthAI MSPR

Ce document récapitule l’intégration et le déploiement continus du projet **HealthAI MSPR** : pipeline GitHub Actions, qualité de code, tests, analyse SonarQube et déploiement SSH en production.

**Fichier principal** : `.github/workflows/main.yml`  
**Dépôt** : `benoitCollado/HEALTHAIMSRP`

---

## 1. Vue d’ensemble

### 1.1 Objectifs

| Objectif | Outil / mécanisme |
|----------|-------------------|
| Vérifier la qualité du code Python | **Ruff** (lint + format) |
| Vérifier la qualité du code TypeScript / Vue | **ESLint** |
| Tester le backend | **pytest** + couverture ≥ 70 % |
| Tester le frontend | **Vitest** + build Vite |
| Analyser la dette technique et la sécurité | **SonarQube** / SonarCloud |
| Déployer en production si tout est vert | **SSH** + Docker Compose |

### 1.2 Déclencheurs

| Événement | Branche | Jobs exécutés |
|-----------|---------|---------------|
| **Pull Request** | `main` | `test-backend`, `test-frontend` |
| **Push** | `main` | Tous les jobs (tests + SonarQube + deploy) |

### 1.3 Schéma du pipeline

```
                    ┌─────────────────┐
                    │  Push / PR main │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │  test-backend   │          │  test-frontend  │
     │  ruff + pytest  │          │ eslint + vitest │
     └────────┬────────┘          └────────┬────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
              ┌──────────────┴──────────────┐  (push main uniquement)
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │    sonarqube    │          │     deploy      │
     │  analyse complète│          │   SSH + Docker  │
     └─────────────────┘          └─────────────────┘
```

Les jobs `sonarqube` et `deploy` s’exécutent **en parallèle** après les tests, uniquement sur un **push vers `main`**.

---

## 2. Job `test-backend`

### 2.1 Environnement

- **Runner** : `ubuntu-latest`
- **Python** : 3.11
- **PostgreSQL éphémère** : conteneur `postgres:17` (isolé, **pas Neon**)
- Variables CI :
  - `DATABASE_URL=postgresql://ci:ci@localhost:5432/healthdb`
  - `SECRET_KEY=ci-test-secret-key`

> La base Neon de production n’est **jamais** utilisée en CI. Le PostgreSQL temporaire sert uniquement aux tests (notamment `/health`).

### 2.2 Étapes

1. Checkout du code
2. Installation des dépendances : `pip install -r backend/requirements-dev.txt`
3. **Lint Python** (Ruff) :
   ```bash
   ruff check backend/app backend/migrations airflow/dags
   ruff format --check backend/app backend/migrations airflow/dags
   ```
4. **Tests** : `python -m pytest` (depuis `backend/`)
5. Upload de `backend/coverage.xml` (artefact pour SonarQube)

### 2.3 Configuration pytest

Fichier : `backend/pytest.ini`

- Couverture minimale : **70 %**
- Rapports : terminal, HTML (`coverage_html/`), XML (`coverage.xml`)
- Tests : `backend/app/tests/` (base SQLite en mémoire via `conftest.py`)

### 2.4 Linter Python — Ruff

Fichier : `ruff.toml` (racine du projet)

| Paramètre | Valeur |
|-----------|--------|
| Version cible | Python 3.11 |
| Longueur de ligne | 120 |
| Règles actives | `E`, `F`, `I`, `UP`, `B` |
| Règles ignorées | `E501`, `B008`, `E402`, `F401`, `I001`, `UP007`, `UP035` |

**Périmètre analysé** : `backend/app`, `backend/migrations`, `airflow/dags`

**Commandes locales** :
```bash
pip install -r backend/requirements-dev.txt
ruff check backend/app backend/migrations airflow/dags
ruff format --check backend/app backend/migrations airflow/dags
# Pour corriger le formatage :
ruff format backend/app backend/migrations airflow/dags
```

---

## 3. Job `test-frontend`

### 3.1 Environnement

- **Runner** : `ubuntu-latest`
- **Node.js** : 20

### 3.2 Étapes

1. Checkout du code
2. `npm ci` (dans `Frontend/`)
3. **Lint** : `npm run lint` (ESLint)
4. **Tests + couverture** : `npm run test:coverage` (Vitest)
5. **Build** : `npm run build` (Vite)
6. Upload de `Frontend/coverage/lcov.info` (artefact pour SonarQube)

### 3.3 Linter TypeScript / Vue — ESLint

Fichier : `Frontend/eslint.config.mjs`

- Règles : JavaScript recommandé, TypeScript recommandé, Vue essential
- Fichiers analysés : `Frontend/src`, `vite.config.ts`, etc.
- Exclusions : `dist/`, `node_modules/`, `coverage/`, `ios/`, `android/`

**Commandes locales** :
```bash
cd Frontend
npm ci
npm run lint
npm test              # tests sans couverture
npm run test:coverage # tests avec couverture (comme en CI)
npm run build
```

### 3.4 Tests Vitest

| Fichier de test | Contenu testé |
|-----------------|---------------|
| `src/services/auth.test.ts` | Login, logout, JWT, rôles |
| `src/components/Navbar.test.ts` | Navbar admin, déconnexion |
| `src/components/AppFooter.test.ts` | Contenu du footer |
| `src/config.test.ts` | URLs par défaut |

---

## 4. Job `sonarqube`

### 4.1 Conditions

- Uniquement sur **push vers `main`**
- Nécessite que `test-backend` et `test-frontend` aient réussi
- S’exécute en parallèle du job `deploy`

### 4.2 Fonctionnement

1. Checkout complet (`fetch-depth: 0` pour l’historique Git)
2. Téléchargement des rapports de couverture (backend + frontend)
3. Vérification de la présence de `coverage.xml` et `lcov.info`
4. Scan via `SonarSource/sonarqube-scan-action@v7`

### 4.3 Périmètre d’analyse

Fichier : `sonar-project.properties`

| Zone | Analysée |
|------|----------|
| `backend/` | API FastAPI, modèles, routers, migrations |
| `Frontend/src/` | Vue, TypeScript, composants |
| `airflow/dags/` | DAGs Python |
| `scripts/` | Scripts de déploiement |
| `.github/workflows/` | Pipelines CI |

**Exclusions** : `node_modules/`, `dist/`, `data/`, `database/`, `docs/`, projets mobiles natifs, fichiers CSV/HTML/MD.

### 4.4 Configuration SonarQube

```properties
sonar.projectKey=HEALTHAIMSRP
sonar.projectName=HealthAI MSPR
sonar.python.coverage.reportPaths=backend/coverage.xml
sonar.javascript.lcov.reportPaths=Frontend/coverage/lcov.info
```

Pour **SonarCloud**, décommenter dans `sonar-project.properties` :
```properties
sonar.organization=benoitCollado
```

---

## 5. Job `deploy`

### 5.1 Conditions

- Uniquement sur **push vers `main`**
- Nécessite que `test-backend` et `test-frontend` aient réussi
- Indépendant du résultat de SonarQube (les deux jobs sont parallèles)

### 5.2 Mécanisme

1. Connexion SSH au serveur via clé privée (`webfactory/ssh-agent`)
2. Ajout du serveur aux `known_hosts`
3. Exécution distante de `scripts/deploy.sh`

### 5.3 Script de déploiement (`scripts/deploy.sh`)

| Étape | Action |
|-------|--------|
| 1 | `git fetch` + `git reset --hard origin/main` |
| 2 | Vérification du `.env` (`DATABASE_URL`, `SECRET_KEY`) |
| 3 | `docker compose build backend frontend` |
| 4 | `docker compose up -d backend frontend` |
| 5 | Vérification `/health` (API + connexion Neon) |

> **Aucun secret applicatif** (Neon, JWT, SMTP) n’est stocké dans GitHub. Tout est dans le `.env` **sur le serveur**.

### 5.4 Architecture production

```
GitHub Actions ──SSH──► Serveur
                          │
                          ├── .env (DATABASE_URL → Neon)
                          ├── docker compose
                          │     ├── backend_api  → port 8089
                          │     └── frontend_nginx → port 89
                          └── PostgreSQL Neon (externe, managé)
```

---

## 6. Secrets et configuration

### 6.1 Secrets GitHub (Settings → Secrets and variables → Actions)

#### Obligatoires pour le déploiement

| Secret | Description |
|--------|-------------|
| `SSH_PRIVATE_KEY` | Clé privée SSH complète |
| `SSH_HOST` | IP ou hostname du serveur |
| `SSH_USER` | Utilisateur SSH |

#### Obligatoires pour SonarQube

| Secret | Description |
|--------|-------------|
| `SONAR_TOKEN` | Token généré dans SonarQube / SonarCloud |

#### Optionnels

| Secret | Défaut | Description |
|--------|--------|-------------|
| `SSH_PORT` | `22` | Port SSH |
| `DEPLOY_PATH` | `/opt/HEALTHAIMSRP` | Chemin du projet sur le serveur |
| `SONAR_HOST_URL` | — | URL SonarQube auto-hébergé (inutile pour SonarCloud) |

#### Aucun secret requis pour

- Ruff, ESLint, pytest, Vitest, build frontend

### 6.2 Configuration serveur (hors GitHub)

Prérequis **une seule fois** sur le serveur :

```bash
# Cloner le projet
sudo mkdir -p /opt/HEALTHAIMSRP
sudo chown $USER:$USER /opt/HEALTHAIMSRP
git clone git@github.com:benoitCollado/HEALTHAIMSRP.git /opt/HEALTHAIMSRP

# Créer le .env de production
cd /opt/HEALTHAIMSRP
cp .env.example .env
nano .env   # DATABASE_URL (Neon), SECRET_KEY, etc.
```

L’utilisateur SSH doit pouvoir exécuter `git` et `docker compose` sans mot de passe.

### 6.3 Mise en place de la clé SSH

```bash
# 1. Générer une clé dédiée
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/healthaim_deploy -N ""

# 2. Installer la clé publique sur le serveur
ssh-copy-id -i ~/.ssh/healthaim_deploy.pub VOTRE_USER@VOTRE_SERVEUR

# 3. Copier la clé privée dans le secret GitHub SSH_PRIVATE_KEY
cat ~/.ssh/healthaim_deploy
```

---

## 7. Exécution locale complète (avant push)

Reproduire la CI en local :

```bash
# ── Backend ──
pip install -r backend/requirements-dev.txt
ruff check backend/app backend/migrations airflow/dags
ruff format --check backend/app backend/migrations airflow/dags
cd backend
DATABASE_URL="postgresql://ci:ci@localhost:5432/healthdb" SECRET_KEY="ci-test-secret-key" python -m pytest

# ── Frontend ──
cd Frontend
npm ci
npm run lint
npm run test:coverage
npm run build
```

---

## 8. Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| `ruff format --check` échoue | Fichier Python non formaté | `ruff format backend/app backend/migrations airflow/dags` |
| `npm run lint` échoue | Erreur ESLint | Corriger le fichier signalé ou adapter `eslint.config.mjs` |
| pytest : couverture < 70 % | Nouveau code non testé | Ajouter des tests dans `backend/app/tests/` |
| pytest : `test_health_ok` échoue en local | Pas de PostgreSQL local | Normal : en CI le service postgres est fourni |
| SonarQube : token invalide | `SONAR_TOKEN` manquant ou expiré | Régénérer le token dans SonarQube |
| Deploy : `DATABASE_URL manquant` | `.env` absent sur le serveur | Créer `.env` depuis `.env.example` |
| Deploy : `/health` timeout | Neon injoignable ou backend crash | `docker compose logs backend` sur le serveur |
| Deploy : permission denied (SSH) | Clé mal configurée | Vérifier `SSH_PRIVATE_KEY` et `authorized_keys` |

---

## 9. Fichiers de référence

| Fichier | Rôle |
|---------|------|
| `.github/workflows/main.yml` | Pipeline CI/CD GitHub Actions |
| `scripts/deploy.sh` | Script de déploiement SSH |
| `sonar-project.properties` | Configuration SonarQube |
| `ruff.toml` | Configuration linter Python |
| `Frontend/eslint.config.mjs` | Configuration linter TypeScript / Vue |
| `backend/pytest.ini` | Configuration pytest + couverture |
| `backend/requirements-dev.txt` | Dépendances dev (ruff + pytest) |
| `Frontend/package.json` | Scripts `lint`, `test`, `test:coverage`, `build` |
| `.env.example` | Modèle des variables serveur (Neon, JWT, SMTP) |

---

*HealthAI MSPR — Documentation CI/CD — Mise à jour : juin 2026*
