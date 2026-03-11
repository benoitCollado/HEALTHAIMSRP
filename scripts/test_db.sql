SELECT 'Connexion OK' AS statut;
SELECT current_database() AS base, current_user AS utilisateur;
SELECT COUNT(*) AS nb_utilisateurs FROM utilisateur;
SELECT COUNT(*) AS nb_aliments FROM aliment;
