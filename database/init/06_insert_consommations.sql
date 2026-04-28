-- Données de test : consommations alimentaires (7 derniers jours)
-- LIMIT 1 sur les sous-requêtes en sécurité contre d'éventuels doublons résiduels
-- calories_calculees = (quantite_g / 100) * calories_aliment

INSERT INTO consommation (date_consommation, quantite_g, calories_calculees, id_aliment, id_utilisateur)
VALUES
  -- testuser - semaine du 21 au 27 avril 2026
  ('2026-04-21', 150.00, 247.50,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-21', 200.00, 260.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-21', 100.00,  35.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Brocoli cuit'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-22', 100.00, 208.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Saumon grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-22', 200.00, 262.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pâtes cuites'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-22', 100.00,  89.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Banane'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-23', 120.00, 198.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-23', 150.00, 195.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-23', 200.00,  36.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Tomate'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-24', 150.00, 247.50,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-24', 150.00, 196.50,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pâtes cuites'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-24', 100.00,  89.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Banane'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-25', 100.00, 116.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Lentilles cuites' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-25', 200.00, 260.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-25', 150.00,  27.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Tomate'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-26', 100.00, 208.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Saumon grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-26',  80.00, 197.60,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pain complet'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-26',  50.00,  28.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Yaourt nature 0%' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-27', 120.00, 198.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-27', 150.00, 195.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-27',  30.00, 173.70,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Amandes'          LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),

  -- marie.dupont - haute protéines
  ('2026-04-21', 200.00, 330.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-21', 200.00, 260.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-21', 150.00,  69.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Fromage blanc 0%' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-23', 150.00, 312.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Saumon grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-23', 200.00, 262.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pâtes cuites'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-23',  30.00, 173.70,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Amandes'          LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-25', 200.00, 330.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-25', 150.00, 174.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Lentilles cuites' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-25', 100.00, 155.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Oeuf entier'      LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-27', 150.00, 247.50,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-27', 100.00, 160.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Avocat'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-27', 200.00, 112.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Yaourt nature 0%' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),

  -- pierre.martin - perte de poids, portions contrôlées
  ('2026-04-22', 120.00, 198.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-22', 100.00, 116.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Lentilles cuites' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-22', 200.00,  36.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Tomate'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-24', 100.00, 208.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Saumon grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-24', 100.00,  35.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Brocoli cuit'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-24', 150.00,  78.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pomme'            LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-26', 130.00, 214.50,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-26', 150.00, 195.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-26', 100.00,  35.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Brocoli cuit'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),

  -- sophie.bernard - cardio endurance, glucides pré-effort
  ('2026-04-21', 100.00, 165.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-21', 150.00, 196.50,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pâtes cuites'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-21', 100.00,  89.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Banane'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-23', 100.00, 208.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Saumon grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-23', 200.00, 260.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Riz blanc cuit'   LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-23', 150.00,  69.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Fromage blanc 0%' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-25', 100.00, 165.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-25',  80.00, 197.60,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pain complet'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-25', 100.00, 160.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Avocat'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-27', 120.00, 198.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Poulet grillé'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-27', 200.00, 262.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Pâtes cuites'     LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-27', 100.00,  89.00,  (SELECT id_aliment FROM aliment WHERE nom_aliment = 'Banane'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1));
