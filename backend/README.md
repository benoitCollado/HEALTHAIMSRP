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

Les tests sont exécutés **dans le conteneur Docker**.

Commande :

```bash
docker exec -it backend_api python -m pytest app/test
```

Les tests couvrent :

* l’authentification
* la sécurité (admin / non admin)
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
│   ├── models/          # Modèles SQLAlchemy
│   ├── schemas/         # Schémas Pydantic
│   ├── routers/         # Routes de l’API
│   └── test/            # Tests Pytest
│
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

