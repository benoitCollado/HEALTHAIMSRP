-- Données de test : objectifs
-- LIMIT 1 sur les sous-requêtes en sécurité contre d'éventuels doublons résiduels

INSERT INTO objectif (type_objectif, description, date_debut, date_fin, statut, id_utilisateur)
VALUES
  -- testuser
  ('Perte de poids', 'Perdre 5 kg en maintenant une alimentation équilibrée et en faisant du cardio 3x/semaine', '2026-04-01', '2026-06-30', 'En cours',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),
  ('Cardio',         'Courir 5 km sans s''arrêter en moins de 30 minutes',                                       '2026-04-01', '2026-06-01', 'En cours',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'testuser'       LIMIT 1)),

  -- marie.dupont
  ('Prise de masse', 'Gagner 3 kg de masse musculaire grâce à la musculation et une alimentation riche en protéines', '2026-03-01', '2026-07-31', 'En cours',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),
  ('Flexibilité',    'Pratiquer le yoga 3 fois par semaine pour améliorer la souplesse',                              '2026-03-01', '2026-05-31', 'En cours',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'marie.dupont'   LIMIT 1)),

  -- pierre.martin
  ('Perte de poids', 'Perdre 10 kg pour retrouver un IMC normal',                             '2026-03-05', '2026-09-05', 'En cours',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),
  ('Bien-être',      'Réduire le stress avec 30 minutes d''activité physique par jour',        '2026-03-05', '2026-06-05', 'En cours',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'pierre.martin'  LIMIT 1)),

  -- sophie.bernard
  ('Bien-être', 'Améliorer la qualité du sommeil en faisant du sport le soir', '2026-01-01', '2026-03-31', 'Terminé',  (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1)),
  ('Cardio',    'Participer à un semi-marathon en mai 2026',                   '2026-02-01', '2026-05-31', 'En cours', (SELECT id_utilisateur FROM utilisateurs WHERE username = 'sophie.bernard' LIMIT 1));
