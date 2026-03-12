-- Migration : ajout sucres_g et acides_gras_satures_g à la table aliment
-- Exécuté automatiquement au premier init. Pour une BDD existante :
--   docker cp database/init/03_add_nutriments_aliment.sql postgres_health:/tmp/
--   docker exec postgres_health psql -U healthuser -d healthdb -f /tmp/03_add_nutriments_aliment.sql
ALTER TABLE aliment ADD COLUMN IF NOT EXISTS sucres_g DECIMAL(6,2);
ALTER TABLE aliment ADD COLUMN IF NOT EXISTS acides_gras_satures_g DECIMAL(6,2);
