-- Données de test : activités physiques (7 derniers jours)
-- id_utilisateur : 1=testuser, 3=marie.dupont, 4=pierre.martin, 5=sophie.bernard
-- id_exercice :
--   1=Course à pied, 2=Natation, 3=Vélo d'appartement, 4=HIIT
--   5=Squat, 6=Développé couché, 7=Tractions, 8=Gainage
--   9=Yoga, 10=Rowing machine

INSERT INTO activite (date_activite, duree_minutes, calories_depensees, intensite, id_exercice, id_utilisateur)
VALUES
  -- testuser (id=1)
  ('2026-04-21', 30, 280.00, 'Modérée',  1, 1),  -- Course à pied
  ('2026-04-22', 45, 320.00, 'Modérée',  3, 1),  -- Vélo
  ('2026-04-23', 20, 260.00, 'Élevée',   4, 1),  -- HIIT
  ('2026-04-25', 35, 300.00, 'Modérée',  1, 1),  -- Course à pied
  ('2026-04-26', 40, 180.00, 'Faible',   8, 1),  -- Gainage
  ('2026-04-27', 45, 350.00, 'Élevée',   4, 1),  -- HIIT

  -- marie.dupont (id=3) - musculation intensive
  ('2026-04-21', 60, 400.00, 'Élevée',   5, 3),  -- Squat
  ('2026-04-21', 30, 200.00, 'Modérée',  8, 3),  -- Gainage
  ('2026-04-23', 60, 420.00, 'Élevée',   6, 3),  -- Développé couché
  ('2026-04-23', 20, 150.00, 'Modérée',  7, 3),  -- Tractions
  ('2026-04-25', 60, 390.00, 'Élevée',   5, 3),  -- Squat
  ('2026-04-27', 45, 300.00, 'Modérée',  7, 3),  -- Tractions

  -- pierre.martin (id=4) - cardio légère pour perte de poids
  ('2026-04-22', 40, 260.00, 'Faible',   1, 4),  -- Course à pied
  ('2026-04-24', 50, 220.00, 'Faible',   3, 4),  -- Vélo
  ('2026-04-24', 30, 120.00, 'Faible',   9, 4),  -- Yoga
  ('2026-04-26', 45, 280.00, 'Modérée',  1, 4),  -- Course à pied
  ('2026-04-27', 60, 240.00, 'Faible',   3, 4),  -- Vélo

  -- sophie.bernard (id=5) - endurance course
  ('2026-04-21', 60, 520.00, 'Élevée',   1, 5),  -- Course à pied (long)
  ('2026-04-23', 45, 350.00, 'Modérée',  2, 5),  -- Natation
  ('2026-04-24', 30, 150.00, 'Faible',   9, 5),  -- Yoga (récupération)
  ('2026-04-25', 70, 600.00, 'Élevée',   1, 5),  -- Course à pied (long)
  ('2026-04-26', 50, 380.00, 'Modérée', 10, 5),  -- Rowing
  ('2026-04-27', 45, 350.00, 'Modérée',  2, 5);  -- Natation
