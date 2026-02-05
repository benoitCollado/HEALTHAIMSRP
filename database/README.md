## Lancer le projet

### Depuis le dossier database :

```docker
docker compose up -d
```

### Lancer test

```docker
docker exec -it postgres_health psql -U healthuser -d healthdb
```

### Arrête tout

```docker
docker compose down
```