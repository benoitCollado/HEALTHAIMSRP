CREATE TABLE utilisateurs (
    id_utilisateur SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    sexe CHAR(1) NOT NULL CHECK (sexe IN ('H','F')),
    taille_cm DECIMAL(5,2) NOT NULL,
    poids_kg DECIMAL(5,2) NOT NULL,
    niveau_activite SMALLINT NOT NULL,
    type_abonnement SMALLINT NOT NULL,
    date_inscription DATE NOT NULL DEFAULT CURRENT_DATE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE objectif (
    id_objectif SERIAL PRIMARY KEY,
    type_objectif VARCHAR(20) NOT NULL,
    description VARCHAR(250) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    statut VARCHAR(10) NOT NULL,
    id_utilisateur INT NOT NULL,
    FOREIGN KEY(id_utilisateur)
        REFERENCES utilisateurs(id_utilisateur)
        ON DELETE CASCADE
);

CREATE TABLE aliment (
    id_aliment SERIAL PRIMARY KEY,
    nom_aliment VARCHAR(50) NOT NULL,
    calories DECIMAL(6,2) NOT NULL,
    proteines_g DECIMAL(6,2) NOT NULL,
    glucides_g DECIMAL(6,2) NOT NULL,
    lipides_g DECIMAL(6,2) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    sucres_g DECIMAL(6,2),
    acides_gras_satures_g DECIMAL(6,2)
);

CREATE TABLE consommation (
    id_consommation SERIAL PRIMARY KEY,
    date_consommation DATE NOT NULL,
    quantite_g DECIMAL(6,2) NOT NULL,
    calories_calculees DECIMAL(6,2) NOT NULL,
    id_aliment INT NOT NULL,
    id_utilisateur INT NOT NULL,
    FOREIGN KEY(id_aliment)
        REFERENCES aliment(id_aliment),
    FOREIGN KEY(id_utilisateur)
        REFERENCES utilisateurs(id_utilisateur)
        ON DELETE CASCADE
);

CREATE TABLE exercice (
    id_exercice SERIAL PRIMARY KEY,
    nom_exercice VARCHAR(100) NOT NULL,
    type_exercice VARCHAR(50) NOT NULL,
    niveau_difficulte VARCHAR(20) NOT NULL,
    equipement VARCHAR(50),
    muscle_principal VARCHAR(30)
);

CREATE TABLE activite (
    id_activite SERIAL PRIMARY KEY,
    date_activite DATE NOT NULL,
    duree_minutes INT NOT NULL,
    calories_depensees DECIMAL(6,2) NOT NULL,
    intensite VARCHAR(20),
    id_exercice INT NOT NULL,
    id_utilisateur INT NOT NULL,
    FOREIGN KEY(id_exercice)
        REFERENCES exercice(id_exercice),
    FOREIGN KEY(id_utilisateur)
        REFERENCES utilisateurs(id_utilisateur)
        ON DELETE CASCADE
);

CREATE TABLE metrique_sante (
   id_metrique SERIAL PRIMARY KEY,
   date_mesure DATE NOT NULL,
   poids_kg DECIMAL(5,2),
   frequence_cardiaque SMALLINT,
   duree_sommeil_h DECIMAL(4,2),
   calories_brulees INT,
   pas INT,
   id_utilisateur INT NOT NULL,
   CONSTRAINT uq_metrique_jour
      UNIQUE (id_utilisateur, date_mesure),
   FOREIGN KEY (id_utilisateur)
      REFERENCES utilisateurs(id_utilisateur)
      ON DELETE CASCADE
);

