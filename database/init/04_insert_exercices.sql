-- Données de test : exercices
-- INSERT ... WHERE NOT EXISTS pour éviter les doublons si le script est rejoué

INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Course à pied',       'Cardio',         'Débutant',      NULL,                  'Jambes'        WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Course à pied');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Natation',            'Cardio',         'Intermédiaire', 'Piscine',             'Corps entier'  WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Natation');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Vélo d''appartement', 'Cardio',         'Débutant',      'Vélo stationnaire',   'Jambes'        WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Vélo d''appartement');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'HIIT',                'Cardio',         'Intermédiaire', NULL,                  'Corps entier'  WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'HIIT');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Squat',               'Musculation',    'Débutant',      NULL,                  'Quadriceps'    WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Squat');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Développé couché',    'Musculation',    'Intermédiaire', 'Barre et haltères',   'Pectoraux'     WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Développé couché');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Tractions',           'Musculation',    'Avancé',        'Barre de traction',   'Dorsaux'       WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Tractions');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Gainage',             'Renforcement',   'Débutant',      'Tapis',               'Abdominaux'    WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Gainage');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Yoga',                'Flexibilité',    'Débutant',      'Tapis',               'Corps entier'  WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Yoga');
INSERT INTO exercice (nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal)
SELECT 'Rowing machine',      'Cardio',         'Intermédiaire', 'Machine à ramer',     'Dos'           WHERE NOT EXISTS (SELECT 1 FROM exercice WHERE nom_exercice = 'Rowing machine');
