-- Mot de passe pour tous les utilisateurs de test : "password"
-- Hash bcrypt généré avec passlib bcrypt rounds=12
-- python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('password'))"

INSERT INTO utilisateurs (username, email, password_hash, age, sexe, taille_cm, poids_kg, niveau_activite, type_abonnement, date_inscription, is_admin)
VALUES
  ('testuser',       'testuser@healthai.local',       '$2b$12$0mQ1I8Kk72Ox3eajUkkzGOMM8p3F/u96YZsdOQnYiIefh8CQC3unK', 30, 'H', 175, 78, 2, 1, '2026-01-15', FALSE),
  ('admin',          'admin@healthai.local',          '$2b$12$0mQ1I8Kk72Ox3eajUkkzGOMM8p3F/u96YZsdOQnYiIefh8CQC3unK', 35, 'H', 180, 80, 1, 2, '2025-11-01', TRUE),
  ('marie.dupont',   'marie.dupont@healthai.local',   '$2b$12$0mQ1I8Kk72Ox3eajUkkzGOMM8p3F/u96YZsdOQnYiIefh8CQC3unK', 28, 'F', 165, 62, 3, 1, '2026-02-10', FALSE),
  ('pierre.martin',  'pierre.martin@healthai.local',  '$2b$12$0mQ1I8Kk72Ox3eajUkkzGOMM8p3F/u96YZsdOQnYiIefh8CQC3unK', 45, 'H', 178, 90, 1, 2, '2026-03-05', FALSE),
  ('sophie.bernard', 'sophie.bernard@healthai.local', '$2b$12$0mQ1I8Kk72Ox3eajUkkzGOMM8p3F/u96YZsdOQnYiIefh8CQC3unK', 32, 'F', 170, 68, 2, 1, '2026-03-20', FALSE)
ON CONFLICT (username) DO NOTHING;
