-- Données de test : métriques de santé quotidiennes
-- LIMIT 1 sur les sous-requêtes en sécurité contre d'éventuels doublons résiduels
-- Contrainte : une seule mesure par utilisateur par jour (UNIQUE id_utilisateur, date_mesure)

INSERT INTO metrique_sante (date_mesure, poids_kg, frequence_cardiaque, duree_sommeil_h, calories_brulees, pas, id_utilisateur)
VALUES
  -- testuser - poids en légère baisse
  ('2026-04-21', 78.00, 72, 7.50, 2100, 8500,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-22', 77.90, 74, 7.00, 2350, 9200,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-23', 77.80, 71, 8.00, 2400, 7800,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-24', 77.70, 70, 7.50, 2200, 9500,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-25', 77.60, 73, 7.00, 2320, 8900,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-26', 77.50, 72, 8.50, 2150, 7200,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-27', 77.40, 70, 7.50, 2380, 9800,  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),

  -- marie.dupont - prise de masse, fréquence cardiaque basse (athlète)
  ('2026-04-21', 62.10, 58, 8.00, 2800, 10200, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-22', 62.20, 60, 7.50, 2200,  7500, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-23', 62.30, 57, 8.50, 2900, 11000, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-24', 62.20, 59, 7.00, 2100,  6800, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-25', 62.40, 56, 8.00, 2850, 10500, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-26', 62.50, 60, 7.50, 2300,  8200, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-27', 62.40, 58, 8.00, 2750, 10800, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),

  -- pierre.martin - surpoids, poids en baisse progressive
  ('2026-04-21', 90.20, 82, 6.50, 2800,  6200, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-22', 90.10, 80, 7.00, 2900,  7800, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-23', 89.90, 83, 6.00, 2600,  5500, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-24', 89.80, 81, 7.50, 2750,  8200, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-25', 89.70, 79, 6.50, 2650,  6900, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-26', 89.60, 80, 7.00, 2820,  7600, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-27', 89.50, 78, 7.50, 2900,  8500, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),

  -- sophie.bernard - cardio endurance, excellent sommeil
  ('2026-04-21', 68.00, 55, 8.50, 3200, 14500, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-22', 67.90, 57, 8.00, 2400,  9800, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-23', 67.80, 54, 9.00, 3100, 13200, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-24', 67.90, 58, 8.50, 2300,  8500, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-25', 67.70, 53, 8.00, 3400, 15800, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-26', 67.80, 56, 8.50, 3000, 12600, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-27', 67.70, 54, 9.00, 3100, 13900, (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1));
