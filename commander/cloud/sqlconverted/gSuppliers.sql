

DROP TABLE IF EXISTS `gSuppliers`;
CREATE TABLE gSuppliers (entity int not null AUTO_INCREMENT ,owner char(255), supplier char(128),supplierName char(255), PRIMARY KEY (entity) );
INSERT INTO gSuppliers VALUES (null,'test@example.com','sheffieldbrewmart','Sheffield Brewmart');
INSERT INTO gSuppliers VALUES (null,'test@example.com','homebrewcentregrimsby','Homebrew Centre Grimsby');
INSERT INTO gSuppliers VALUES (null,'test@example.com','tesco','Tesco');
INSERT INTO gSuppliers VALUES (null,'test@example.com','copperkettlehomebrewing','Copper Kettle Homebrewing');
INSERT INTO gSuppliers VALUES (null,'test@example.com','recycledreused','Reused and Recycled');
INSERT INTO gSuppliers VALUES (null,'test@example.com','leylandhomebrew','Leyland Homebrew');
INSERT INTO gSuppliers VALUES (null,'test@example.com','worcesterhopshop','Worcester Hop Shop');
INSERT INTO gSuppliers VALUES (null,'test@example.com','brewuk','BrewUK');
INSERT INTO gSuppliers VALUES (null,'test@example.com','thehomebrewcompany','The Homebrew Company');
INSERT INTO gSuppliers VALUES (null,'test@example.com','themaltmiller','The Malt Miller');
