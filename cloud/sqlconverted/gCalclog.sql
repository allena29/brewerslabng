DROP TABLE IF EXISTS `gCalclogs`;

CREATE TABLE gCalclogs (entity int not null AUTO_INCREMENT,owner char(255),recipe char(255),brewlog char(255),calclog text,PRIMARY KEY (entity));


