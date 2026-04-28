-- Données de test : exercices

INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
VALUES
  ('Course à pied',       'Cardio',         'Débutant',      NULL,                  'Jambes'),
  ('Natation',            'Cardio',         'Intermédiaire', 'Piscine',             'Corps entier'),
  ('Vélo d''appartement', 'Cardio',         'Débutant',      'Vélo stationnaire',   'Jambes'),
  ('HIIT',                'Cardio',         'Intermédiaire', NULL,                  'Corps entier'),
  ('Squat',               'Musculation',    'Débutant',      NULL,                  'Quadriceps'),
  ('Développé couché',    'Musculation',    'Intermédiaire', 'Barre et haltères',   'Pectoraux'),
  ('Tractions',           'Musculation',    'Avancé',        'Barre de traction',   'Dorsaux'),
  ('Gainage',             'Renforcement',   'Débutant',      'Tapis',               'Abdominaux'),
  ('Yoga',                'Flexibilité',    'Débutant',      'Tapis',               'Corps entier'),
  ('Rowing machine',      'Cardio',         'Intermédiaire', 'Machine à ramer',     'Dos');
