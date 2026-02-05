# Base de données – HealthAI Coach

Cette base de données stocke toutes les informations nécessaires au fonctionnement de l’API HealthAI Coach.

Elle utilise **PostgreSQL** et est lancée via **Docker Compose**.

---

## Prérequis

* Docker
* Docker Compose

Aucune installation PostgreSQL locale n’est requise.

---

## Lancer la base de données

### Depuis le dossier `database`

```bash
docker compose down
docker compose up
```

Le conteneur PostgreSQL démarre sur le port **5432**.

---

## Connexion à PostgreSQL

### Depuis Docker

```bash
docker exec -it postgres_health psql -U healthuser -d healthdb
```

Paramètres par défaut :

* utilisateur : `healthuser`
* base : `healthdb`
* port : `5432`

---

## Structure de la base

### Table `utilisateurs`

Contient les informations utilisateurs et les rôles.

Champs principaux :

* `id_utilisateur`
* `username`
* `password_hash`
* `is_admin`
* `age`
* `sexe`
* `taille_cm`
* `poids_kg`
* `niveau_activite`
* `type_abonnement`
* `date_inscription`

Par défaut :

* `is_admin = FALSE`
* les mots de passe sont stockés **hachés**

---

### Autres tables

* `objectif` : objectifs utilisateurs
* `aliment` : base alimentaire
* `consommation` : suivi nutritionnel
* `exercice` : exercices sportifs
* `activite` : activités réalisées
* `metrique_sante` : suivi santé quotidien

Toutes les relations utilisent des **clés étrangères** avec suppression en cascade si nécessaire.

---

## Scripts SQL

Les scripts sont exécutés automatiquement au premier démarrage du conteneur.

```
database/
└── init/
    ├── 01_create_tables.sql
    └── 02_insert_test_data.sql
```

* `01_create_tables.sql`
  Création des tables et contraintes

* `02_insert_test_data.sql`
  Données de test (dont un compte admin)

---

## Compte administrateur

Un compte administrateur est créé par script ou par commande Python.

Exemple :

* username : `admin`
* mot de passe : `admin123`
* rôle : admin

Ce compte permet :

* création / modification / suppression des utilisateurs
* accès complet à l’API

---

## Sécurité base de données

* Aucune requête SQL brute côté API
* Utilisation exclusive de **SQLAlchemy**
* Protection contre SQL injection
* Mots de passe jamais stockés en clair

---

## Arrêter la base de données

```bash
docker compose down
```

Pour supprimer aussi les données :

```bash
docker compose down -v
```

