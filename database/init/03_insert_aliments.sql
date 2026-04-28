-- Données de test : aliments (valeurs nutritionnelles pour 100g)

INSERT INTO aliment (nom_aliment, calories, proteines_g, glucides_g, lipides_g, categorie, sucres_g, acides_gras_satures_g)
VALUES
  ('Poulet grillé',        165.00, 31.00,  0.00, 3.60, 'Viande',             0.00, 1.00),
  ('Saumon grillé',        208.00, 20.00,  0.00,13.00, 'Poisson',            0.00, 3.10),
  ('Oeuf entier',          155.00, 13.00,  1.10,11.00, 'Oeufs',              1.10, 3.30),
  ('Riz blanc cuit',       130.00,  2.70, 28.00, 0.30, 'Céréales',           0.10, 0.10),
  ('Pâtes cuites',         131.00,  5.00, 25.00, 1.10, 'Céréales',           0.50, 0.20),
  ('Pain complet',         247.00, 13.00, 41.00, 3.40, 'Céréales',           4.00, 0.70),
  ('Brocoli cuit',          35.00,  2.40,  7.00, 0.40, 'Légumes',            1.70, 0.10),
  ('Tomate',                18.00,  0.90,  3.90, 0.20, 'Légumes',            2.60, 0.00),
  ('Banane',                89.00,  1.10, 23.00, 0.30, 'Fruits',            12.20, 0.10),
  ('Pomme',                 52.00,  0.30, 14.00, 0.20, 'Fruits',            10.40, 0.00),
  ('Avocat',               160.00,  2.00,  9.00,15.00, 'Fruits',             0.70, 2.10),
  ('Yaourt nature 0%',      56.00,  5.70,  7.70, 0.10, 'Produits laitiers',  7.70, 0.10),
  ('Fromage blanc 0%',      46.00,  8.00,  4.00, 0.20, 'Produits laitiers',  4.00, 0.10),
  ('Lentilles cuites',     116.00,  9.00, 20.00, 0.40, 'Légumineuses',       1.80, 0.10),
  ('Amandes',              579.00, 21.00, 22.00,50.00, 'Oléagineux',         4.40,3.80);
