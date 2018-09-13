DROP TABLE IF EXISTS `gBrewlogs`;
CREATE TABLE gBrewlogs (entity int not null AUTO_INCREMENT, owner char(255), brewlog char(128), recipe char(128), brewhash char(128), realrecipe char(128), boilVolume float, process char(128), largeImage char(255), smallImage char(255), brewdate int, brewdate2 int, bottledate int, PRIMARY KEY(entity));
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2011-11-04','Green','dGVzdEBleGFtcGxlLmNvbS9HcmVlbiBCdWxsZXQgUGFsZSBBbGUvMjAxMS0xMS0wNA==','Green Bullet Pale Ale',0.0,'15AG10i11','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2011-10-1','Pure Gold Goose','dGVzdEBleGFtcGxlLmNvbS9UaGUgR29sZCBHb29zZS8yMDExLTEwLTE=','The Gold Goose',0.0,'13AG8i9','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2012-03-1','Pure Green Goose','dGVzdEBleGFtcGxlLmNvbS9QdXJlIEdyZWVuIEdvb3NlLzIwMTItMDMtMQ==','Pure Green Goose',0.0,'16AG11i12','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2012-03-18','ABC','dGVzdEBleGFtcGxlLmNvbS9BQkMvMjAxMi0wMy0xOA==','ABC',0.0,'17AG12i13','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2012-06-08','Citra','dGVzdEBleGFtcGxlLmNvbS9DaXRyYS8yMDEyLTA2LTA4','Citra',0.0,'17AG12i13','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2012-10-20','Nelson','dGVzdEBleGFtcGxlLmNvbS9OZWxzb24vMjAxMi0xMC0yMA==','Nelson',0.0,'19AG16i17','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2012_11_10','Dark Green Goose','dGVzdEBleGFtcGxlLmNvbS9EYXJrIEdyZWVuIEdvb3NlLzIwMTJfMTFfMTA=','Dark Green Goose',0.0,'20AG17i18','','',0,0,0);
INSERT INTO gBrewlogs VALUES (null,'test@example.com','2012_11_25','Yellow Goose 2','dGVzdEBleGFtcGxlLmNvbS9ZZWxsb3cgR29vc2UgMi8yMDEyXzExXzI1','Yellow Goose 2',0.001,'21AG18i19','','',0,0,0);


