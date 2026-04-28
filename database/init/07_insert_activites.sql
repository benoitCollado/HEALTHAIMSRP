-- Données de test : activités physiques (7 derniers jours)
-- LIMIT 1 sur les sous-requêtes en sécurité contre d'éventuels doublons résiduels

INSERT INTO activite (date_activite, duree_minutes, calories_depensees, intensite, id_exercice, id_utilisateur)
VALUES
  -- testuser
  ('2026-04-21', 30, 280.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Course à pied'       LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-22', 45, 320.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Vélo d''appartement' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-23', 20, 260.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'HIIT'                LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-25', 35, 300.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Course à pied'       LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-26', 40, 180.00, 'Faible',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Gainage'             LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('2026-04-27', 45, 350.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'HIIT'                LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),

  -- marie.dupont - musculation intensive
  ('2026-04-21', 60, 400.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Squat'               LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-21', 30, 200.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Gainage'             LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-23', 60, 420.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Développé couché'    LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-23', 20, 150.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Tractions'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-25', 60, 390.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Squat'               LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('2026-04-27', 45, 300.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Tractions'           LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),

  -- pierre.martin - cardio légère pour perte de poids
  ('2026-04-22', 40, 260.00, 'Faible',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Course à pied'       LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-24', 50, 220.00, 'Faible',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Vélo d''appartement' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-24', 30, 120.00, 'Faible',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Yoga'                LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-26', 45, 280.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Course à pied'       LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('2026-04-27', 60, 240.00, 'Faible',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Vélo d''appartement' LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),

  -- sophie.bernard - endurance course longue distance
  ('2026-04-21', 60, 520.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Course à pied'       LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-23', 45, 350.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Natation'            LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-24', 30, 150.00, 'Faible',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Yoga'                LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-25', 70, 600.00, 'Élevée',  (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Course à pied'       LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-26', 50, 380.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Rowing machine'      LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('2026-04-27', 45, 350.00, 'Modérée', (SELECT id_exercice FROM exercice WHERE nom_exercice = 'Natation'            LIMIT 1), (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1));
