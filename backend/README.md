# Backend – HealthAI Coach API

Ce projet fournit une **API REST sécurisée** pour la gestion :

* des utilisateurs
* de la nutrition
* des exercices
* des activités
* des métriques de santé
* des objectifs

Le backend est développé avec **FastAPI**, **PostgreSQL**, **JWT** et **Docker**.

---

## Technologies utilisées

* Python 3.11
* FastAPI
* SQLAlchemy
* Alembic (migrations de base de données)
* PostgreSQL (Neon serverless)
* JWT (JSON Web Token)
* Docker / Docker Compose
* Pytest + pytest-cov

---

## Prérequis

Avant de commencer, assure-toi d'avoir installé :

* Docker
* Docker Compose

Aucune installation Python locale n'est nécessaire.

---

## Lancer le projet

À la **racine du projet** :

```bash
docker compose up -d --build backend
```

Au démarrage, le conteneur exécute automatiquement :
1. `seed_db.py` — import des données CSV
2. Migrations Alembic (`alembic upgrade head` ou `stamp head` si base existante)
3. `uvicorn` — serveur API sur le port 8000

---

## Accès à l'API

* API : [http://localhost:8000](http://localhost:8000)
* Documentation interactive (Swagger / OpenAPI) : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Authentification

L'API est protégée par **JWT (Bearer Token)**.

### Connexion

```
POST /login
```

Les identifiants sont envoyés sous forme de **form-data** (OAuth2).

Réponse :

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

Utilisation dans les requêtes protégées :

```
Authorization: Bearer <token>
```

**Identifiants par défaut** : `admin` / `password`

---

## Gestion des rôles

* Chaque utilisateur possède le champ `is_admin`
* Les routes d'administration sont réservées aux utilisateurs `is_admin = true`
* Les autres routes sont accessibles aux utilisateurs authentifiés

---

## Migrations Alembic

La base de données est versionnée avec **Alembic**.

### Commandes utiles

| Commande | Description |
| -------- | ----------- |
| `alembic current` | Voir la révision active |
| `alembic history` | Historique des migrations |
| `alembic upgrade head` | Appliquer toutes les migrations |
| `alembic downgrade -1` | Revenir à la migration précédente |
| `alembic revision --autogenerate -m "desc"` | Générer une migration depuis les modèles |

### Depuis le conteneur Docker

```bash
docker exec backend_api alembic current
docker exec backend_api alembic revision --autogenerate -m "ajout_colonne_x"
docker exec backend_api alembic upgrade head
```

### Logique de démarrage (`start.sh`)

| Situation | Action |
| --------- | ------ |
| Base vide (nouveau déploiement) | `alembic upgrade head` — crée toutes les tables |
| Base existante sans `alembic_version` | `alembic stamp head` — marque sans rejouer |
| Base avec `alembic_version` | `alembic upgrade head` — applique les nouvelles migrations |

---

## Tests automatisés

Les tests utilisent **pytest** avec rapport de couverture **pytest-cov**.

### Lancer les tests (dans le conteneur Docker)

```bash
docker exec -it backend_api python -m pytest
```

### Options utiles

| Commande | Description |
| -------- | ----------- |
| `python -m pytest` | Tests + couverture (config `pytest.ini`) |
| `python -m pytest --cov-report=xml` | Rapport XML (compatible CI/CD) |
| `python -m pytest -v` | Affichage détaillé par test |
| `python -m pytest -k test_securite` | Filtrer un module de test |

### Configuration couverture

* Seuil minimum : **70 %**
* Rapport terminal : lignes non couvertes (`term-missing`)
* Rapport HTML : `coverage_html/index.html`
* Exclus du calcul : `app/test/`, `app/database.py`, `app/routers/admin.py`

### Les tests couvrent

* Authentification JWT
* Sécurité des rôles (admin / non admin)
* En-têtes de sécurité HTTP
* Routes principales de l'API (aliments, exercices, utilisateurs)

---

## Structure du projet

```
backend/
│
├── app/
│   ├── main.py            # Point d'entrée FastAPI + exception handler global
│   ├── database.py        # Connexion PostgreSQL (pool_pre_ping, pool_recycle)
│   ├── security.py        # JWT et gestion des mots de passe
│   ├── middleware.py      # En-têtes de sécurité HTTP
│   ├── email_alert.py     # Alertes email sur erreurs 500
│   ├── models/            # Modèles SQLAlchemy
│   ├── schemas/           # Schémas Pydantic v2
│   ├── routers/           # Routes de l'API
│   └── test/              # Tests Pytest
│
├── migrations/
│   ├── env.py             # Configuration Alembic
│   ├── script.py.mako     # Template de migration
│   └── versions/          # Fichiers de migration versionnés
│
├── coverage_html/         # Rapport de couverture HTML (généré)
├── alembic.ini            # Configuration Alembic
├── .coveragerc            # Configuration pytest-cov
├── pytest.ini             # Configuration pytest
├── start.sh               # Script de démarrage (migrations + uvicorn)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Sécurité

* Mots de passe stockés **hachés (bcrypt)**
* JWT signé avec une clé secrète (`SECRET_KEY`)
* Vérification des rôles côté backend
* Accès aux routes protégé par dépendances FastAPI

### En-têtes de sécurité HTTP

Le middleware `SecurityHeadersMiddleware` (`app/middleware.py`) ajoute automatiquement les en-têtes suivants à chaque réponse :

| En-tête | Valeur | Rôle |
| ------- | ------ | ---- |
| `X-Frame-Options` | `DENY` | Protection contre le clickjacking |
| `X-Content-Type-Options` | `nosniff` | Blocage du MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | Filtre XSS (navigateurs legacy) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Force HTTPS pendant 1 an |
| `Content-Security-Policy` | `default-src 'self'; ...` | Restriction des sources de contenu autorisées |

### Alertes email (erreurs 500)

`app/email_alert.py` envoie automatiquement un email à l'administrateur lors de toute erreur 500 non gérée :

* Email HTML avec type d'erreur, message, stack trace, URL et timestamp
* Cooldown de 60 s par type d'erreur pour éviter le flood
* Désactivé silencieusement si les variables SMTP ne sont pas configurées

---

## Variables d'environnement

```env
# Base de données
DATABASE_URL=postgresql://<user>:<password>@<host>.neon.tech/<db>?sslmode=require

# JWT
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Alertes email (laisser vide pour désactiver)
EMAIL_PASS=xxxx xxxx xxxx xxxx
ADMIN_EMAIL=admin@example.com
```

> **Gmail** : générer un mot de passe d'application sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## Arrêter le projet

```bash
docker compose down
```
