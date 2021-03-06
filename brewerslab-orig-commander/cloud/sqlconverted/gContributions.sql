DROP TABLE IF EXISTS `gContributions`;
CREATE TABLE gContributions (entity int not null AUTO_INCREMENT, owner char(255), recipeName char(255), ingredientType char(128), ingredient char(128), hopAddAt float, ibu float, srm float, gravity float, PRIMARY KEY(entity) );
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','fermentables','Maris Otter',0.0,0.0,0.0,40.0101404452);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','fermentables','Honey',0.0,0.0,0.0,2.51547938955);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','fermentables','Torrified Wheat',0.0,0.0,0.0,1.51863306799);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','hops','Citra',0.001,0.000735666298827,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','hops','Citra',60.0,22.2980512182,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','hops','Citra',15.0,8.29826780687,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','fermentables','Maris Otter',0.0,0.0,33.0647577093,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Citra','fermentables','Torrified Wheat',0.0,0.0,0.447577092511,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Maris Otter',0.0,0.0,0.0,32.7814721053);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,2.07169332473);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Crystal 80',0.0,0.0,0.0,2.91124995582);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Honey',0.0,0.0,0.0,4.12201089635);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','hops','Hallertau Hersbrucker',0.001,0.00015283220232,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','hops','Willamette',60.0,12.4620157181,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','hops','Green Bullet',60.0,19.0328967331,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','hops','Willamette',15.0,3.09184400108,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','hops','Hallertau Hersbrucker',15.0,1.12055921979,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','hops','Green Bullet',15.0,6.13871572579,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Maris Otter',0.0,0.0,33.0647577093,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Torrified Wheat',0.0,0.0,0.745215859031,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Crystal 80',0.0,0.0,88.1726872247,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Maris Otter',0.0,0.0,0.0,31.8266719469);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Honey',0.0,0.0,0.0,4.00195232656);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,2.01135274245);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Crystal 80',0.0,0.0,0.0,2.82645626779);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Maris Otter',0.0,0.0,0.0,27.7809085638);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Honey',0.0,0.0,0.0,3.49322957318);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,1.75567230909);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Crystal 80',0.0,0.0,0.0,2.46716097951);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Maris Otter',0.0,0.0,0.0,27.7809085638);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,1.75567230909);
INSERT INTO gContributions VALUES (null,'test@example.com','Dark Green Goose','fermentables','Crystal 80',0.0,0.0,0.0,2.46716097951);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Torrified Wheat',0.0,0.0,0.0,3.27877849154);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Tipple',0.0,0.0,0.0,34.5532810262);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Honey',0.0,0.0,0.0,2.17240092875);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','hops','Nelson Sauvin',0.001,0.000591564515967,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','hops','Nelson Sauvin',60.0,22.4129063288,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','hops','Nelson Sauvin',15.0,4.44853940467,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Torrified Wheat',0.0,0.0,1.11894273128,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Tipple',0.0,0.0,33.0647577093,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Honey',0.0,0.0,0.0,2.10912711529);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Torrified Wheat',0.0,0.0,0.0,3.18328008887);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Tipple',0.0,0.0,0.0,33.5468747827);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Honey',0.0,0.0,0.0,1.84101773623);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Torrified Wheat',0.0,0.0,0.0,2.77862584029);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Tipple',0.0,0.0,0.0,29.2824415477);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Torrified Wheat',0.0,0.0,0.0,2.77862584029);
INSERT INTO gContributions VALUES (null,'test@example.com','Nelson','fermentables','Tipple',0.0,0.0,0.0,29.2824415477);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Maris Otter',0.0,0.0,0.0,37.6494001774);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','CaraGold',0.0,0.0,0.0,5.179906599);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,2.91194749349);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Honey',0.0,0.0,0.0,2.34075779284);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','hops','Hallertau Hersbrucker',0.001,8.27705713265e-05,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','hops','Willamette',60.0,11.9984970615,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','hops','Centennial',60.0,22.9062216628,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','hops','Willamette',15.0,5.95368871306,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','hops','Hallertau Hersbrucker',15.0,0.622431092729,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','hops','Centennial',15.0,11.3661329977,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Maris Otter',0.0,0.0,31.6165213216,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','CaraGold',0.0,0.0,7.35822524024,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Torrified Wheat',0.0,0.0,0.872085954399,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Maris Otter',0.0,0.0,0.0,36.5528157062);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Honey',0.0,0.0,0.0,2.2725803814);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','CaraGold',0.0,0.0,0.0,5.02903553301);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,2.82713348883);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Maris Otter',0.0,0.0,0.0,31.9062713368);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Honey',0.0,0.0,0.0,1.98369304478);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','CaraGold',0.0,0.0,0.0,4.38975135508);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,2.46775211313);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Maris Otter',0.0,0.0,0.0,31.9062713368);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','CaraGold',0.0,0.0,0.0,4.38975135508);
INSERT INTO gContributions VALUES (null,'test@example.com','Pure Gold Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,2.46775211313);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','CaraGold',0.0,0.0,0.0,3.69683883495);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,1.94833398058);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Maris Otter',0.0,0.0,0.0,30.5933396505);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Honey',0.0,0.0,0.0,1.74650656311);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','hops','Hallertau Hersbrucker',0.001,0.000137197728277,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','hops','Centennial',60.0,18.9842931199,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','hops','Centennial',15.0,4.71003039358,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','hops','Hallertau Hersbrucker',15.0,2.306696012,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','CaraGold',0.0,0.0,5.03524229075,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Torrified Wheat',0.0,0.0,0.559471365639,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Maris Otter',0.0,0.0,24.6332444934,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','CaraGold',0.0,0.0,0.0,3.58916391743);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,1.89158638892);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Honey',0.0,0.0,0.0,1.69563743991);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Maris Otter',0.0,0.0,0.0,29.7022715053);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','CaraGold',0.0,0.0,0.0,3.13291426691);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,1.65113049202);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Honey',0.0,0.0,0.0,1.48009030772);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Maris Otter',0.0,0.0,0.0,25.9265590258);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','CaraGold',0.0,0.0,0.0,3.13291426691);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Torrified Wheat',0.0,0.0,0.0,1.65113049202);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose','fermentables','Maris Otter',0.0,0.0,0.0,25.9265590258);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Maris Otter',0.0,0.0,0.0,41.4281182946);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Torrified Wheat',0.0,0.0,0.0,1.61112102977);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Honey',0.0,0.0,0.0,2.59018688632);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','hops','Green Bullet',0.001,0.000637515248383,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','hops','Green Bullet',60.0,30.9169473899,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','hops','Green Bullet',15.0,4.79408691185,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Maris Otter',0.0,0.0,33.513367879,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Torrified Wheat',0.0,0.0,0.464804969057,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Maris Otter',0.0,0.0,0.0,40.2214740724);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Honey',0.0,0.0,0.0,2.51474454982);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Torrified Wheat',0.0,0.0,0.0,1.56419517453);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Maris Otter',0.0,0.0,0.0,35.108574826);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Honey',0.0,0.0,0.0,2.19507363247);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Torrified Wheat',0.0,0.0,0.0,1.36535680489);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Maris Otter',0.0,0.0,0.0,35.108574826);
INSERT INTO gContributions VALUES (null,'test@example.com','Green','fermentables','Torrified Wheat',0.0,0.0,0.0,1.36535680489);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Maris Otter',0.0,0.0,0.0,41.5782347744);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','CaraGold',0.0,0.0,0.0,2.39555376997);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Torrified Wheat',0.0,0.0,0.0,2.95903495657);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Honey',0.0,0.0,0.0,3.22914173722);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','hops','Hallertau Hersbrucker',0.001,0.000103904210302,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','hops','Willamette',60.0,26.4866126725,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','hops','Green Bullet',60.0,16.180912469,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','hops','Willamette',15.0,0.0,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','hops','Hallertau Hersbrucker',15.0,0.781355137713,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','hops','Green Bullet',15.0,6.69084604515,0.0,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Maris Otter',0.0,0.0,26.4518061674,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','CaraGold',0.0,0.0,2.57804405286,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Torrified Wheat',0.0,0.0,0.671365638767,0.0);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Maris Otter',0.0,0.0,0.0,40.3672182276);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Honey',0.0,0.0,0.0,3.13508906527);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','CaraGold',0.0,0.0,0.0,2.3257803592);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Torrified Wheat',0.0,0.0,0.0,2.8728494724);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Maris Otter',0.0,0.0,0.0,35.2357921817);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Honey',0.0,0.0,0.0,2.73656079426);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','CaraGold',0.0,0.0,0.0,2.03013031354);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Torrified Wheat',0.0,0.0,0.0,2.50765674286);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Maris Otter',0.0,0.0,0.0,35.2357921817);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','CaraGold',0.0,0.0,0.0,2.03013031354);
INSERT INTO gContributions VALUES (null,'test@example.com','Yellow Goose 2','fermentables','Torrified Wheat',0.0,0.0,0.0,2.50765674286);


