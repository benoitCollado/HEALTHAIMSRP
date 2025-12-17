CREATE TABLE utilisateurs(
   id_utilisateur INT,
   age INT NOT NULL,
   sexe VARCHAR(1) NOT NULL,
   taille_cm DECIMAL(15,2) NOT NULL,
   poids_kg DECIMAL(15,2) NOT NULL,
   niveau_activite SMALLINT NOT NULL,
   type_abonnement SMALLINT NOT NULL,
   date_inscription DATE NOT NULL,
   PRIMARY KEY(id_utilisateur)
);

CREATE TABLE OBJECTIF(
   id_objectif INT,
   type_objectif VARCHAR(20) NOT NULL,
   description VARCHAR(250) NOT NULL,
   date_debut DATE NOT NULL,
   date_fin DATE NOT NULL,
   statut VARCHAR(10) NOT NULL,
   id_utilisateur INT NOT NULL,
   PRIMARY KEY(id_objectif),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateurs(id_utilisateur)
);

CREATE TABLE ALIMENT(
   id_aliment INT,
   nom_aliment VARCHAR(50) NOT NULL,
   calories DECIMAL(15,2) NOT NULL,
   proteines_g DECIMAL(15,2) NOT NULL,
   glucides_g DECIMAL(15,2) NOT NULL,
   lipides_g DECIMAL(15,2) NOT NULL,
   categorie VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_aliment)
);

CREATE TABLE CONSOMMATION(
   id_consommation INT,
   date_consommation DATE NOT NULL,
   quantite_g DECIMAL(15,2) NOT NULL,
   calories_calculees DECIMAL(15,2) NOT NULL,
   id_aliment INT NOT NULL,
   id_utilisateur INT NOT NULL,
   PRIMARY KEY(id_consommation),
   FOREIGN KEY(id_aliment) REFERENCES ALIMENT(id_aliment),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateurs(id_utilisateur)
);

CREATE TABLE EXERCICE(
   id_exercice INT,
   nom_exercice VARCHAR(100) NOT NULL,
   type_exercice VARCHAR(50) NOT NULL,
   niveau_difficulte VARCHAR(20) NOT NULL,
   equipement VARCHAR(50),
   muscle_principal VARCHAR(30),
   PRIMARY KEY(id_exercice)
);

CREATE TABLE ACTIVITE(
   id_activite INT,
   date_activite DATE NOT NULL,
   duree_minutes INT NOT NULL,
   calories_depensees DECIMAL(15,2) NOT NULL,
   intensite VARCHAR(20),
   id_exercice INT NOT NULL,
   id_utilisateur INT NOT NULL,
   PRIMARY KEY(id_activite),
   FOREIGN KEY(id_exercice) REFERENCES EXERCICE(id_exercice),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateurs(id_utilisateur)
);

CREATE TABLE METRIQUE_SANTE(
   id_metrique INT,
   date_mesure DATE NOT NULL,
   poids_kg DECIMAL(15,2),
   frequence_cardiaque SMALLINT,
   duree_sommeil_h DECIMAL(15,2),
   calories_brulees INT,
   pas INT,
   id_utilisateur INT NOT NULL,
   PRIMARY KEY(id_metrique),
   FOREIGN KEY(id_utilisateur) REFERENCES utilisateurs(id_utilisateur)
);
