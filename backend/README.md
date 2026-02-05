# Backend – HealthAI Coach API

Ce backend fournit une API REST sécurisée pour gérer les utilisateurs, la nutrition, les exercices et les données de santé.

L’API est développée avec **FastAPI**, **PostgreSQL**, **JWT** et **Docker**.

---

## Prérequis

Avant de commencer, assure-toi d’avoir installé :

* Docker
* Docker Compose

Aucune installation Python locale n’est nécessaire.

---

## Lancer le projet

### Depuis le dossier `backend`

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Le backend démarre automatiquement sur le port **8000**.

---

## Accès à l’API

* API :
  [http://localhost:8000](http://localhost:8000)

* Documentation interactive (OpenAPI / Swagger) :
  [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Authentification

L’API est sécurisée avec **JWT (Bearer Token)**.

### Connexion

Endpoint :

```
POST /login
```

Body JSON :

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Réponse :

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

Le token doit être utilisé dans l’en-tête HTTP :

```
Authorization: Bearer <token>
```

---

## Gestion des rôles

* Par défaut, un utilisateur est **non admin**
* Le champ `is_admin` est stocké en base de données
* Certaines routes sont **réservées aux administrateurs** :

  * création d’utilisateurs
  * modification
  * suppression

Les autres routes sont accessibles aux utilisateurs authentifiés.

---

## Tests automatisés

Les tests sont exécutés **dans le conteneur Docker**.

```bash
docker exec -it backend_api python -m pytest
```

Les tests couvrent :

* authentification
* sécurité (admin / non admin)
* routes utilisateurs

---

## Structure du projet

```
backend/
│
├── app/
│   ├── main.py          # Point d’entrée FastAPI
│   ├── database.py      # Connexion PostgreSQL
│   ├── security.py      # JWT et mots de passe
│   ├── models/          # Modèles SQLAlchemy
│   ├── schemas/         # Schémas Pydantic
│   ├── routers/         # Routes API
│   └── test/            # Tests Pytest
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Sécurité

* Mots de passe stockés **hachés (bcrypt)**
* JWT signé avec clé secrète
* Vérification du rôle admin côté backend
* Accès aux routes protégé par dépendances FastAPI

---

## Arrêter le projet

```bash
docker compose down
```
