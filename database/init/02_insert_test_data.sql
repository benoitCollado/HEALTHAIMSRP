-- Mot de passe pour tous les utilisateurs de test : "password"
-- Hash bcrypt : $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW

INSERT INTO utilisateurs (username, password_hash, age, sexe, taille_cm, poids_kg, niveau_activite, type_abonnement, date_inscription, is_admin)
VALUES
  ('testuser',       '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 30, 'H', 175.00, 78.00, 2, 1, '2026-01-15', FALSE),
  ('admin',          '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 35, 'H', 180.00, 80.00, 1, 2, '2025-11-01', TRUE),
  ('marie.dupont',   '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 28, 'F', 165.00, 62.00, 3, 1, '2026-02-10', FALSE),
  ('pierre.martin',  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 45, 'H', 178.00, 90.00, 1, 2, '2026-03-05', FALSE),
  ('sophie.bernard', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 32, 'F', 170.00, 68.00, 2, 1, '2026-03-20', FALSE)
ON CONFLICT (username) DO NOTHING;
