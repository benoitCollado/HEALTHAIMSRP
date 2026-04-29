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
* PostgreSQL
* JWT (JSON Web Token)
* Docker / Docker Compose
* Pytest

---

## Prérequis

Avant de commencer, assure-toi d’avoir installé :

* Docker
* Docker Compose

Aucune installation Python locale n’est nécessaire.

---

## Lancer le projet

À la **racine du projet** :

```bash
docker compose down -v
docker compose up --build
```

Le backend démarre automatiquement.

Port utilisé : **8000**

---

## Accès à l’API

* API :
  [http://localhost:8000](http://localhost:8000)

* Documentation interactive (Swagger / OpenAPI) :
  [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Authentification

L’API est protégée par **JWT (Bearer Token)**.

### Connexion

Endpoint :

```
POST /login
```

Les identifiants sont envoyés sous forme de **form-data** (OAuth2).

Exemple :

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Réponse :

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

Le token doit être ajouté dans les requêtes protégées :

```
Authorization: Bearer <token>
```

---

## Gestion des rôles

* Chaque utilisateur possède le champ `is_admin`
* Par défaut, un utilisateur n’est **pas administrateur**
* Certaines routes sont **réservées aux administrateurs** :

  * création d’utilisateurs
  * modification
  * suppression

Les autres routes sont accessibles aux utilisateurs authentifiés.

---

## Tests automatisés

Les tests sont exécutés avec **pytest** et le rapport de couverture est généré automatiquement par **pytest-cov**.

### Lancer les tests (dans le conteneur Docker)

```bash
docker exec -it backend_api python -m pytest
```

La configuration dans `pytest.ini` active automatiquement :
- le rapport **terminal** avec les lignes non couvertes (`term-missing`)
- le rapport **HTML** dans `coverage_html/index.html`
- un seuil minimum de **70 %** de couverture (échec si non atteint)

### Lancer les tests en local

```bash
cd backend
pip install -r requirements.txt
python -m pytest
```

### Options utiles

| Commande | Description |
| -------- | ----------- |
| `python -m pytest` | Tests + couverture (config `pytest.ini`) |
| `python -m pytest --cov-report=xml` | Rapport XML (compatible CI/CD) |
| `python -m pytest -v` | Affichage détaillé par test |
| `python -m pytest -k test_securite` | Filtrer un module de test |

### Rapport HTML

Le rapport HTML est généré dans `backend/coverage_html/`.  
Ouvrir `coverage_html/index.html` dans un navigateur pour naviguer ligne par ligne.

### Les tests couvrent

* l’authentification JWT
* la sécurité des rôles (admin / non admin)
* les en-têtes de sécurité HTTP
* les routes principales de l’API

---

## Structure du projet

```
backend/
│
├── app/
│   ├── main.py          # Point d’entrée FastAPI
│   ├── database.py      # Connexion à PostgreSQL
│   ├── security.py      # JWT et gestion des mots de passe
│   ├── middleware.py    # En-têtes de sécurité HTTP
│   ├── models/          # Modèles SQLAlchemy
│   ├── schemas/         # Schémas Pydantic
│   ├── routers/         # Routes de l’API
│   └── test/            # Tests Pytest
│
├── coverage_html/       # Rapport de couverture HTML (généré)
├── .coveragerc          # Configuration pytest-cov
├── pytest.ini           # Configuration pytest
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

---

## Variables d’environnement

Exemple de fichier `.env` :

```env
DATABASE_URL=postgresql://healthuser:healthpass@postgres:5432/healthdb
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Arrêter le projet

```bash
docker compose down
```

