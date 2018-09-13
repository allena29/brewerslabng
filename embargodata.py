


class brewerslabEmbargoData:

	"""
	This class provides data inherrited from various sources. At this stage none have been cleared for use.
	The data may not be compatible with the final license.
	
	"""

	def __init__(self):
		self.fermentable_descriptions = {
			}
		self.fermentable_names = {
			'ukpilsner2row' : 'UK Pilsner 2-Row',
			'maltedoats' : 'Malted Oats',
			'2rowmalt' : '2-Row Malt',
			'6rowmalt' : '6-Row Malt',
			'belgianpilsner2row' : 'Belgian Pilsner 2-Row',
			'germanpilsner2row' : 'German Pilsner 2-Row',
			'lagermalt' : 'Lager Malt',
			'belgianwheat' : 'Belgian Wheat',
			'germanwheat' : 'German Wheat',
			'whitewheat' : 'White Wheat',
			'carapils' : 'CaraPils',
			'dextrinemalt' : 'Dextrine Malt',
			'acidmalt' : 'Acid Malt',
			'peatedmalt' : 'Peated Malt',
			'marisotter' : 'Maris Otter',
			'briesspalealemalt' : 'Briess Pale Ale Malt',
			'englishmild' : 'English Mild',
			'viennamalt' : 'Vienna Malt',
			'toastedmalt' : 'Toasted Malt',
			'darkwheat' : 'Dark Wheat',
			'munichmalt' : 'Munich Malt',
			'smokedmalt' : 'Smoked Malt',
			'crystal10' : 'Crystal 10',
			'carastan15' : 'Carastan 15',
			'munich10' : 'Munich 10',
			'crystal20' : 'Crystal 20',
			'munich20' : 'Munich 20',
			'carared' : 'CaraRed',
			'melanoidinmalt' : 'Melanoidin Malt',
			'ambermalt' : 'Amber Malt',
			'caravienna' : 'CaraVienna',
			'biscuit' : 'Belgian Biscuit Malt',
			'brumalt' : 'Brumalt',
			'gambrinushoneymalt' : 'Gambrinus Honey Malt',
			'belgianaromatic' : 'Belgian Aromatic',
			'victorymalt' : 'Victory Malt',
			'crystal30' : 'Crystal 30',
			'carastan35' : 'Carastan 35',
			'crystal40' : 'Crystal 40',
			'caramelwheatmalt' : 'Caramel Wheat Malt',
			'specialroast' : 'Special Roast',
			'caramunich' : 'CaraMunich',
			'crystal60' : 'Crystal 60',
			'brownmalt' : 'Brown Malt',
			'crystal80' : 'Crystal 80',
			'crystal90' : 'Crystal 90',
			'crystal120' : 'Crystal 120',
			'caraaroma' : 'CaraAroma',
			'crystal150' : 'Crystal 150',
			'specialb' : 'Special B',
			'chocolateryemalt' : 'Chocolate Rye Malt',
			'roastedbarley' : 'Roasted Barley',
			'carafai' : 'Carafa I',
			'chocolatemalt' : 'Chocolate Malt',
			'chocolatewheatmalt' : 'Chocolate Wheat Malt',
			'carafaii' : 'Carafa II',
			'blackpatentmalt' : 'Black Patent Malt',
			'blackbarley' : 'Black Barley',
			'carafaiii' : 'Carafa III',
		}


		# Malt Details taken from the Malts Chart at homebrewtalk.com/wiki
		# not cleared for use.
		# SRM converted to EBC
		self.fermentable_details = {
			'ukpilsner2row' : (77.9,1.97,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'maltedoats' : (80.0,1.97,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1),
			'2rowmalt' : (77.9,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'6rowmalt' : (75.7,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'belgianpilsner2row' : (77.9,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'germanpilsner2row' : (80.0,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'lagermalt' : (82.2,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'belgianwheat' : (80.0,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'germanwheat' : (84.4,3.94,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'whitewheat' : (86.7,3.94,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1),
			'carapils' : (71.4,3.94,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1),
			'dextrinemalt' : (71.4,3.94,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1),
			'acidmalt' : (58.4,5.91,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1),
			'peatedmalt' : (73.6,5.91,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'marisotter' : (82.2,5.91,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1),
			'englishmild' : (80.0,7.88,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'viennamalt' : (77.9,7.88,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'toastedmalt' : (62.8,9.85,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'darkwheat' : (84.4,17.73,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'munichmalt' : (80.0,17.73,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1),
			'smokedmalt' : (80.0,17.73,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1),
			'crystal10' : (73,19.7,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'carastan15' : (73,29.55,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'munich10' : (75.7,19.7,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1),
			'crystal20' : (73,39.4,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'munich20' : (75.7,39.4,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1),
			'carared' : (75.7,39.4,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1),
			'melanoidinmalt' : (80.0,39.4,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1),
			'ambermalt' : (75.7,43.34,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'caravienna' : (73.6,43.34,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'biscuit' : (77.9,45.31,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'brumalt' : (71.4,45.31,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1),
			'gambrinushoneymalt' : (80.0,49.25,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1),
			'belgianaromatic' : (77.9,51.22,1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1),
			'victorymalt' : (73.6,55.16,1,1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,1),
			'crystal30' : (73,59.1,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'carastan35' : (73,68.95,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'crystal40' : (73,78.8,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'caramelwheatmalt' : (75.7,90.62,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'specialroast' : (71.4,98.5,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1),
			'caramunich' : (71.4,110.32,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1),
			'crystal60' : (73,118.2,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'brownmalt' : (69.2,128.05,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'crystal80' : (73,157.6,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'crystal90' : (73,177.3,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'crystal120' : (73,236.4,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'caraaroma' : (75.7,256.1,0,0,0,1,0,1,0,0,0,1,1,0,0,0,0,0,1),
			'crystal150' : (75.7,295.5,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1,0,1),
			'specialb' : (64.9,354.6,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1),
			'chocolateryemalt' : (67.1,492.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'roastedbarley' : (54.1,591.0,0,0,0,0,1,0,0,1,1,0,0,1,1,0,0,0,1),
			'carafai' : (69.2,663.89,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'chocolatemalt' : (73.6,689.5,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,1,1),
			'chocolatewheatmalt' : (71.4,788.0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'carafaii' : (69.2,811.64,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			'blackpatentmalt' : (54.1,985.0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1),
			'blackbarley' : (54.1,985.0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1),
			'carafaiii' : (69.2,1034.25,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
		}


	
		# Straight Translation of Hop Names	
		self.hop_names = {
			'eroica' : 'Eroica',
			'eastkentgoldings' : 'East Kent Goldings',
			'liberty' : 'Liberty',
			'fuggle' : 'Fuggle',
			'perle' : 'Perle',
			'pioneer' : 'Pioneer',
			'kentgoldings' : 'Kent Goldings',
			'yamhillgoldings' : 'Yamhill Goldings',
			'fuggles' : 'Fuggles',
			'yeoman' : 'Yeoman',
			'superstyrians' : 'Super Styrians',
			'amarillo' : 'Amarillo',
			'banner' : 'Banner',
			'styriangoldings' : 'Styrian Goldings',
			'sladek' : 'Sladek',
			'nugget' : 'Nugget',
			'millenium' : 'Millenium',
			'firstgold' : 'First Gold',
			'herald' : 'Herald',
			'newport' : 'Newport',
			'hullerbitterer' : 'Huller Bitterer',
			'hallertaumittelfruh' : 'Hallertau Mittelfruh',
			'usfuggle' : 'US Fuggle',
			'crystal' : 'Crystal',
			'olympic' : 'Olympic',
			'northdown' : 'Northdown',
			'challenger' : 'Challenger',
			'galena' : 'Galena',
			'talisman' : 'Talisman',
			'hallertau' : 'Hallertau',
			'saaz' : 'Saaz',
			'yakimacluster' : 'Yakima Cluster',
			'domesichallertau' : 'Domesic Hallertau',
			'willamette' : 'Willamette',
			'spaltselect' : 'Spalt Select',
			'progress' : 'Progress',
			'admiral' : 'Admiral',
			'warrior' : 'Warrior',
			'columbus' : 'Columbus',
			'goldings' : 'Goldings',
			'northernbrewer' : 'Northern Brewer',
			'simcoe' : 'Simcoe',
			'ultra' : 'Ultra',
			'tomahawk' : 'Tomahawk',
			'bullion' : 'Bullion',
			'horizon' : 'Horizon',
			'comet' : 'Comet',
			'whitbreadgolding' : 'Whitbread Golding',
			'hersbrucker' : 'Hersbrucker',
			'aquila' : 'Aquila',
			'tettnanger' : 'Tettnanger',
			'golding' : 'Golding',
			'ahtanum' : 'Ahtanum',
			'styrianaurora' : 'Styrian Aurora',
			'strisselspalt' : 'Strisselspalt',
			'tettnang' : 'Tettnang',
			'prideofringwood' : 'Pride of Ringwood',
			'zeus' : 'Zeus',
			'bramlingcross' : 'Bramling Cross',
			'pacificgem' : 'Pacific Gem',
			'satus' : 'Satus',
			'mounthood' : 'Mount Hood',
			'target' : 'Target',
			'record' : 'Record',
			'vanguard' : 'Vanguard',
			'brewersgold' : 'Brewers Gold',
			'chinook' : 'Chinook',
			'wyetarget' : 'Wye Target',
			'zenith' : 'Zenith',
			'vangaurd' : 'Vangaurd',
			'cluster' : 'Cluster',
			'orion' : 'Orion',
			'centennial' : 'Centennial',
			'spalt' : 'Spalt*',
			'hallertauhersbrucker' : 'Hallertau Hersbrucker',
			'glacier' : 'Glacier',
			'summit' : 'Summit',
			'magnum' : 'Magnum',
			'sterling' : 'Sterling',
			'superalpha' : 'Super Alpha',
			'phoenix' : 'Phoenix',
			'sticklebract' : 'Sticklebract',
			'omega' : 'Omega',
			'tradition' : 'Tradition',
			'cascade' : 'Cascade',
			'mthood' : 'Mt. Hood',
			'lublin' : 'Lublin',
			'santiam' : 'Santiam',
		}


		#
		# Hop Substitution Chart
		# http://www.brew365.com/hop_substitution_chart.php
		# Not cleared for use
		self.hop_subs = {
			'perle' : ['Challenger', 'Northern Brewer'],
			'saaz' : ['Sladek', 'Lublin', 'Sterling', 'Ultra', 'Vangaurd'],
			'styrianaurora' : ['Northern Brewer'],
			'strisselspalt' : ['Mt. Hood', 'Crystal'],
			'progress' : ['Fuggles', 'E.K. Goldings'],
			'sterling' : ['Saaz', 'Lublin'],
			'columbus' : ['Magnum', 'Chinook', 'Northern Brewer', 'Warrior', 'Millenium', 'Bullion'],
			'eastkentgoldings' : ['Fuggle', 'Progress', 'First Gold'],
			'millenium' : ['Nugget', 'Columbus'],
			'mthood' : ['Hallertauer', 'Liberty', 'Crystal', 'Strisselspalt'],
			'styriangoldings' : ['Fuggle', 'Willamette'],
			'summit' : ['Amarillo', 'Cascade'],
			'newport' : ['Galena', 'Nugget', 'Fuggle', 'Magnum'],
			'willamette' : ['Styrian Golding', 'Target', 'Fuggle', 'Tettnanger', 'Glacier'],
			'chinook' : ['Brewers Gold', 'Columbus', 'Galena', 'Nugget', 'Northern Brewer', 'Eroica'],
			'ultra' : ['Liberty', 'Hallertau', 'Saaz'],
			'tettnanger' : ['Hallertau', 'Liberty', 'Fuggle'],
			'eroica' : ['Galena'],
			'northdown' : ['Admiral', 'Challenger'],
			'sladek' : ['Saaz', 'Lublin'],
			'cluster' : ['Galena', 'Eroica'],
			'firstgold' : ['E.K. Goldings'],
			'spalt' : ['Santiam', 'Liberty', 'Tettnanger', 'Hallertau'],
			'fuggle' : ['Willamette', 'Styrian Golding', 'Tettnanger', 'Newport'],
			'hallertau' : ['Liberty', 'Tettnanger', 'Mt. Hood', 'Vangaurd', 'Tradition'],
			'glacier' : ['Willamette', 'Fuggle', 'Tettnanger', 'Styrian Goldings'],
			'liberty' : ['Hallertau', 'Tettnanger', 'Mt. Hood', 'Crystal', 'Ultra'],
			'magnum' : ['Horizon', 'Newport'],
			'admiral' : ['Target', 'Northdown', 'Challenger'],
			'warrior' : ['Nugget', 'Columbus'],
			'ahtanum' : ['Amarillo', 'Centennial', 'Simcoe'],
			'amarillo' : ['Cascade', 'Centennial', 'Summit', 'Ahtanum'],
			'lublin' : ['Saaz', 'Sterling'],
			'tradition' : ['Hallertauer'],
			'target' : ['Nugget', 'Fuggle', 'WIllamette', 'Admiral'],
			'nugget' : ['Cluster', 'Galena', 'Brewers Gold', 'Warrior', 'Eroica', 'Target', 'Millenium'],
			'cascade' : ['Amarillo', 'Centennial', 'Summit'],
			'horizon' : ['Magnum'],
			'santiam' : ['Tettnanger', 'Spalt', 'Liberty', 'Hallertau'],
			'northernbrewer' : ['Nugget', 'Chinook', 'Columbus', 'Bullion', 'Perle', 'Styrian Aurora'],
			'crystal' : ['Mt. Hood', 'Liberty', 'Hallertauer', 'Tettnanger', 'Strisselspalt'],
			'vangaurd' : ['Saaz', 'Hallertauer'],
			'challenger' : ['Perle', 'Admiral'],
			'galena' : ['Brewers Gold', 'Nugget', 'Cluster', 'Chinook', 'Eroica', 'Newport'],
			'centennial' : ['Amarillo', 'Cascade', 'Columbus', 'Summit'],
			'bullion' : ['Columbus', 'Northern Brewer'],
			'brewersgold' : ['Bullion', 'Chinook', 'Galena', 'Nugget'],
		}

		self.hop_alphas = {
			'hullerbitterer' : 5.75,
			'perle' : 9,
			'yamhillgoldings' : 4,
			'prideofringwood' : 10,
			'hallertauhersbrucker' : 2.3,
			'glacier' : 5.5,
			'liberty' : 4,
			'hallertaumittelfruh' : 3.75,
			'pioneer' : 9,
			'superalpha' : 13,
			'progress' : 6.25,
			'magnum' : 14,
			'fuggles' : 4.8,
			'record' : 6.5,
			'saaz' : 3.8,
			'sterling' : 5.5,
			'warrior' : 16,
			'columbus' : 15,
			'phoenix' : 10,
			'cluster' : 6.5,
			'willamette' : 5.5,
			'zeus' : 15,
			'orion' : 7,
			'amarillo' : 9.5,
			'goldings' : 5,
			'lublin' : 4.5,
			'mounthood' : 5,
			'eastkentgoldings' : 5,
			'sticklebract' : 11.5,
			'brewersgold' : 9,
			'banner' : 10,
			'satus' : 13,
			'tettnanger' : 4.5,
			'millenium' : 15.5,
			'bramlingcross' : 6.5,
			'target' : 11.5,
			'nugget' : 13,
			'tomahawk' : 15,
			'eroica' : 12,
			'yakimacluster' : 7,
			'wyetarget' : 10,
			'herald' : 12,
			'cascade' : 6,
			'vanguard' : 5,
			'pacificgem' : 15,
			'bullion' : 7.5,
			'strisselspalt' : 3.5,
			'horizon' : 12.5,
			'talisman' : 8,
			'comet' : 10,
			'chinook' : 13,
			'ultra' : 4.5,
			'simcoe' : 13,
			'styriangoldings' : 5.5,
			'hersbrucker' : 4,
			'olympic' : 12,
			'aquila' : 7,
			'northernbrewer' : 8.5,
			'zenith' : 9,
			'superstyrians' : 9,
			'crystal' : 3,
			'santiam' : 6.5,
			'omega' : 10,
			'domesichallertau' : 3.9,
			'northdown' : 8.6,
			'challenger' : 8.5,
			'firstgold' : 7.5,
			'whitbreadgolding' : 6,
			'galena' : 13,
			'centennial' : 10.5,
			'kentgoldings' : 5,
			'yeoman' : 7.25,
			'newport' : 15.5,
			'spalt' : 4.5,
		}



		# Hop Typcial use
		# http://www.schiesshouse.com/hop_properties_chart.htm
		self.hop_styles = {
			'admiral' : ["Ale"],
			'amarillo' : ["Ale", "IPA"],
			'bramlingcross' : ["ESB", "bitter", "pale ale"],
			'brewersgold' : ["English ale"],
			'bullion' : ["IPA", "ESB", "stout"],
			'cascade' : ["Pale ale", "IPA", "porter", "barleywine"],
			'centennial' : ["All ale styles"],
			'challenger' : ["English-style ales", "porter", "stout", "ESB", "bitter"],
			'chinook' : ["Pale ale", "IPA", "stout", "porter", "lager"],
			'cluster' : ["Ale and lager (good aroma for ale", "good bittering for lager)"],
			'columbus' : ["IPA", "pale ale", "stout"],
			'crystal' : ["Lager", "pilsner", "ESB"],
			'eroica' : ["Wheat"],
			'firstgold' : ["Ale", "ESB"],
			'fuggle' : ["All English-style ales", "ESB", "bitter", "lager"],
			'galena' : ["Ale", "porter", "stout", "ESB", "bitter"],
			'golding' : ["Pale ale", "ESB", "all English-style beer"],
			'hallertauer' : ["Lager", "pilsner", "bock", "wheat"],
			'hersbrucker' : ["Lager", "pilsner", "bock", "wheat"],
			'horizon' : ["Ale", "lager"],
			'liberty' : ["Lager", "pilsner", "bock", "wheat"],
			'magnum' : ["All beers", "particularly lager", "pilsner", "stout"],
			'mounthood' : ["Lager", "pilsner", "bock", "wheat"],
			'northdown' : ["All ales", "porter"],
			'northernbrewer' : ["ESB", "bitter", "English pale ale", "porter", "California (steam) beer"],
			'northwest' : ["Ale", "porter", "stout", "ESB", "bitter"],
			'nugget' : ["Light lager"],
			'perle' : ["Pale ale", "porter", "lager"],
			'phoenix' : ["All ales"],
			'pioneer' : ["Ale", "ESB"],
			'polishlublin' : ["Pilsner"],
			'progress' : ["Ale", "bitter", "ESB", "porter"],
			'saaz' : ["Pilsner"],
			'santiam' : ["Lager", "American ale", "pilsner"],
			'spalt' : ["Lager"],
			'sterling' : ["Lager", "ale", "pilsner"],
			'target' : ["All ale and lager"],
			'tettnanger' : ["German ales and lagers", "American lagers", "wheat"],
			'tomahawk' : ["Ale"],
			'ultra' : ["Lager", "pilsner", "wheat", "finish hop in ales"],
			'warrior' : ["Ale", "stout"],
			'willamette' : ["Pale ale", "ESB", "bitter", "English-style ale", "porter", "stout"],
		}

		
		# Hop Descriptions
		# http://beeradvocate.com/beer/101/hops
		# Not cleared for use
		self.hop_descriptions = {
			'perle' : """Perle is an aroma-type cultivar, bred in 1978 in Germany from Northern Brewer. It is grown in Germany, Belgium and the U. S. A. Perle is a newer variety, originally from Germany but now grown quite successfully in the US. Perle is a medium alpha hop with a very clean, almost minty bitterness and pleasant aroma. (alpha acid: 7.0-9.5% / beta acid: 4.0-5.0%)""",
			'saaz' : """Saaz is the traditional noble hop for true pilsner beer. Saaz is famous for its spicy, clean bitterness. (average alpha acid: 3.0%)""",
			'liberty' : """Liberty is a triploid aroma-type cultivar, the result in 1983 of the colchicine induced tetrapcoid female cultivar Hallertau mf and a downy mildew resistant male, USDA 64035M. It is a half-sister to Ultra, Mt. Hood and Crystal. (alpha acid: 3.5-4.5% / beta acid: 3.0-3.5%)""",
			'magnum' : """Magnum is a bittering/aroma type cultivar, bred in 1980 at Huell, the German Hop Research Instititute, from the American variety Galena and the German male 75/5/3. (alpha acid: 10.0-12.6% / beta acid: 5.0-7.0%)""",
			'sterling' : """Sterling is an aroma cultivar, a diploid seedling made in 1990 with a 21522 female plant and a 21361 male plant. Its parentage is 1/2 Saazer, 1/4 Cascade, 1/8 64035M (unknown German aroma X open pollination),1/16 Brewers Gold, 1/32 Early Green, and 1/32 unknown. (alpha acid: 4.5-5.0% / beta acid: 5.0-6.0%)""",
			'warrior' : """Warrior is a bittering hop of a recent origin, bred by Yakima Chief Ranches. (alpha acid: 15.0-17.0% / beta acid: 4.5-5.5%)""",
			'columbus' : """This high alpha variety has a pungent aroma and clean bittering. Excellent for bitter ales and American IPA styles, and can be dramatic when dry hopped. (average alpha acid: 12%)""",
			'cluster' : """Cluster originated from mass selection of the Cluster hop, which is an old American cultivar. It is suggested that they arose from hybridization of varieties, imported by Dutch and English settlers and indigenous male hops. (alpha acid: 5.5-8.5% / beta acid: 4.5-5.5%)""",
			'amarillo' : """Amarillo is an aroma-type cultivar of recent origin, discovered and introduced by Virgil Gamache Farms Inc. (alpha acid: 8-11% / beta acid: 6-7% ) """,
			'satus' : """Satus is a bittering-type cultivar of recent origin. (alpha acid: 12.5-14.0% / beta acid: 8.5-9.0%)""",
			'simcoe' : """Simcoe is a bittering/aroma type cultivar bred by Yakima Chief Ranches. (alpha acid: 12.0-14.0% / beta acid: 4.0-5.0%)""",
			'mounthood' : """Mt. Hood is a triploid aroma-type cultivar, the 1983 result of a cross between the colchicine - induced tetraploid female Hallertau mf (USDA 21397) and the USDA 19058M, male plant. It is a half-sister to Ultra, Liberty and Crystal. An aromatic variety derived from Hallertau with a refined, spicy aroma and clean bittering. A good choice for lagers. (alpha acid: 4.0-6.0% / beta acid: 5.0-7.5%)""",
			'nugget' : """Nugget is a bittering-type cultivar, bred in 1970 from the USDA 65009 female plant and USDA 63015M. The lineage of Nugget is 5/8 Brewers Gold, 1/8 Early Green, 1/16 Canterbury Golding, 1/32 Bavarian and 5/32 unknown. Nugget is a great bittering hop with a heavy herbal aroma. (alpha acid: 12.5-14.5% / beta acid: 4.0-6.0%)""",
			'tomahawk' : """Tomahawk is a bittering hop of recent origin, bred by Charles Zimmermann. It is the first commercially grown 'Super Alpha' variety. In 1998 it contributed to 11% of the USA hop crop. (alpha acid: 14.0-18.0% / beta acid: 4.5-5.8%)""",
			'crystal' : """Crystal is a triploid aroma-type cultivar, released for commercial production in 1993. It originates from a seedling selection (No. 8309-37) made at Corvallis in 1983 between the colchicine - induced tetraploid 'Hallertau mf' (USDA 21397) and the diploid male downy mildew resistant aroma hop, USDA 21381M. Crystal is a half-sister of Mt. Hood and Liberty. (alpha acid: 4.0-6.0% / beta acid: 5.0-6.7%)""",
			'spaltselect' : """Spalt Select is an aroma- type cultivar, bred in Germany and released for cultivation in the late 1980's. It is grown in Germany in the Hallertau and Spalt areas and in the U.S.A. in Washington State. (alpha acid: 3.5-5.5% / beta acid: 3.0-4.5%)""",
			'tettnang' : """Tettnang is an aroma-type cultivar which originated in the Tettnang hop growing area of Germany as a land-race hop. It is grown in the U.S.A. in Oregon and Washington State.The original noble hop from the Tettnang region of Germany, ideal for your finest lagers and wheat beers. This limited availability hop has a fine, pure aroma, that is not present in United States grown Tettnanger. (alpha acid: 4.0-5.0% / beta acid: 3.5-4.5%)""",
			'willamette' : """Willamette is a triploid aroma-type hop, which originated in the mid 1970's and is a seedling of Fuggle. It is a very popular aroma hop, contributing in 1998 to 18% of the total USA hop crop.A variation on English Fuggle hops grown in Oregon and Washington. Willamette has a fragrant spicy woody aroma. An excellent American aromatic hops for ales and lagers. (alpha acid: 4.0-6.0% / beta acid: 3.5-4.5%)""",
			'horizon' : """Horizon is a high alpha-aroma cultivar, a diploid seedling result of a cross made in 1970 between the USDA 65009 female plant (with Brewers Gold and Early Green lineage) and the male plant 64035M. It was released as a commercial variety in 1998. (alpha acid: 10.2-16.5% / beta acid: 6.5-8.5%)""",
			'chinook' : """Chinook is a bittering variety with aroma characteristics released in May, 1985. It was bred by crossing a Petham Golding with the USDA 63012 male. A high alpha acid hop with a wonderful herbal, almost smoky character when used as an aromatic during the last few minutes of the boil when dry hoping. Excellent for hopping American-style Pale Ales, especially those brewed to higher gravities. (alpha acid: 12.0-14.0% / beta acid: 3.0-4.0%)""",
			'ultra' : """Ultra is a triploid aroma-type cultivar, originated in 1983 from a cross between the colchicine-induced tetraploid Hallertau mf (USDA 21397) and the diploid Saazer-derived male genotype (USDA 21237m). Ultra is the half-sister to Mt. Hood, Liberty and Crystal. Its genetic composition is 4/6 Hallertau mf, 1/6 Saazer, and 1/6 unknown. This cultivar was released for commercial production in March, 1995. (alpha acid: 4.5-5.0% / beta acid: 3.6-4.7%)""",
			'northernbrewer' : """Northern Brewer is a bittering-type cultivar, bred in 1934 in England from a Canterbury Golding female plant and the male plant OB21. Northern Brewer has been used in the breeding process of many newer varieties. This cultivar is grown in England, Belgium, Germany and the USA.A strong fragrant hop with a rich rough-hewn flavor and aroma, ideal for steam-style beers and ales. Northern Brewer has a unique mint-like evergreen flavor. (alpha acid: 8.0-10.0%/ beta acid: 3.0-5.0%)""",
			'cascade' : """Cascade is an aroma-type cultivar which originated as the first commercial hop from the USDA-ARS breeding program. It was bred in 1956 but not released for cultivation until 1972. It reached its peak in 1975 when it produced 13.3% of the total American crop. It was obtained by crossing an English Fuggle with a male plant, which originated from the Russian variety Serebrianka with a Fuggle male plant. 
A very popular U.S. variety, with a moderate bitterness level and fragrant, flowery aroma. Cascade is often used in highly hopped West Coast ales that have a citrus-floral hop character. (alpha acid: 4.5-6.0% / beta acid: 5.0-7.0% )""",
			'golding' : """Golding is a group of aroma-type cultivars originating in England. Over the decades, the group has been changed and widened. Mostly they have been named after villages in East Kent, (Petham, Rothersham, Canterbury, Eastwell) or hop farmers, who grew them (Amos's Early Bird, Cobbs).English Goldings grown in East Kent, are a premium hop, called East Kent Golding and should not be confused with U.K. Goldings, which are grown in other parts such as Kent, Worcestershire, Hampshire and Herefordshire. The cultivar grown in the USA (Oregon and Washington State) is a Canterbury Golding.
The premier English aroma hop. Superb in English-style ales, and lend a unique character to fine lagers as well. This hop has a unique spicy aroma and refined flavor. (alpha acid: 4.0-6.0% / beta acid: 2.0-3.0%)""",
			'vanguard' : """Vanguard is a diploid seedling made in 1982 between USDA 21285, which has Hallertau mf parentage and USDA 64037m. It was released for cultivation in 1997. (alpha acid: 5.0-6.0% / beta acid: 5.0-7.0%)""",
			'ahtanum' : """Ahtanum is an aroma-type cultivar bred by Yakima Chief Ranches. Its name is derived from the area near Yakima where the first hop farm was established in 1869 by Charles Carpenter. (alpha acid: 5.7-6.3% / beta acid: 5.0-6.5%)""",
			'galena' : """Galena is a bittering-type cultivar which was bred in 1968 from Brewers Gold and an open pollination, i.e. an unknown male plant. It was released for cultivation in 1978. Galena is the most "mellow" hop of the high-alpha varieties, and has replaced Cluster as the most widely grown US hop. The bitterness is clean and well balanced. Great general purpose bittering hop. (alpha acid: 12.5-14.0% / beta acid: 7.5-9.0%)""",
			'centennial' : """Centennial is an aroma-type cultivar, bred in 1974 and released in 1990. The genetic composition is 3/4 Brewers Gold, 3/32 Fuggle, 1/16 East Kent Golding, 1/32 Bavarian and 1/16 unknown. A relatively new hop on the market, this hop used to be called CFJ90. Described by some as a "Super Cascade" and we tend to agree, but it's not nearly as "citrusy". Some even use it for aroma as well as bittering. Bitterness is quite clean and can have floral notes depending on the boil time. (alpha acid: 9.5-11.5% / beta acid: 4.0-5.0%)""",
			'usfuggle' : """A mild-flavored English-style hop grown in Oregon, with a fragrant wood-like aroma. Milder in character than English Fuggles. This hop imparts a smooth, well rounded hop character. (average alpha acid: 3.9%)""",
			'fuggle' : """Fuggle is an aroma-type cultivar selected in England as a chance seedling in 1861. It reached its peak in the U.K. in 1949 when 78% of the English crops were grown as Fuggle. It is also marketed as Styrian (Savinja) Golding in the Slovenian Republic. In the USA it is grown in Oregon and Washington State. Superb in English-style ales, and lends a unique character not imparted by the more subtle American-grown Fuggles. (alpha acid: 3.8-5.5% / beta acid: 1.5-2.0%)""",
		}

"""
a=brewerslabEmbargoData()
import re
r = re.compile("[^a-z0-9]")

H={}
for x in a.hop_descriptions:
	henc = r.sub('', x.lower() )
	if not H.has_key( henc ):
		H[henc] = x

for x in a.hop_alphas:
	henc = r.sub('', x.lower() )
	if not H.has_key( henc ):
		H[henc] = x

for x in a.hop_subs:
	henc = r.sub('', x.lower() )
	if not H.has_key( henc ):
		H[henc] = x


print "\t\tself.hop_names = {"
for h in H:
	print "\t\t\t'%s' : '%s'," %(h,H[h])
print "\t\t}"	
		

print ""
print "\t\tself.hop_subs = {"
for x in a.hop_subs:
	henc = r.sub('', x.lower() )
	print "\t\t\t'%s' : %s," %(henc,a.hop_subs[x])
print "\t\t}"
	

print ""
print "\t\tself.hop_alphas = {"
for x in a.hop_alphas:
	henc = r.sub('', x.lower() )
	print "\t\t\t'%s' : %s," %(henc,a.hop_alphas[x])
print "\t\t}"
	
print ""
print "\t\tself.hop_descriptions = {"
for x in a.hop_descriptions:
	henc = r.sub('', x.lower() )
	print "\t\t\t'%s' : \"\"\"%s\"\"\"," %(henc,a.hop_descriptions[x])
print "\t\t}"




a= copy of malt chart from homebrew wiki
import re
r = re.compile("[^a-z0-9]")
dig=re.compile("[^0-9\.]")

print "			self.malt_names = {"
for x in a.split("\n"):
	y = x.split("\t")
	print "\t\t\t\t'%s' : '%s'," %(r.sub('', y[0].lower()),y[0])
print "}\n\n"

print "			self.malt_detail = {"
for x in a.split("\n"):
	y = x.split("\t")
	SRM=int(y[3])
	PERCENT=dig.sub('',y[2])
	MASHREQ=0
	AROMATIC=0
	BISCUIT=0
	BODY=0
	BURNT=0
	CARAMEL=0
	CHOCOLATE=0
	COFFEE=0
	GRAINY=0
	HEAD=0
	MALTY=0
	NUTTY=0
	ROASTED=0
	SMOKED=0
	SWEET=0
	TOASTED=0
	if len(y[4]):	MASHREQ=1
	if len(y[5]):	AROMATIC=1
	if len(y[6]):	BISCUIT=1
	if len(y[7]):	BODY=1
	if len(y[8]):	BURNT=1
	if len(y[9]):	CARAMEL=1
	if len(y[10]):	CHOCOLATE=1
	if len(y[11]):	COFFEE=1
	if len(y[12]):	GRAINY=1
	if len(y[13]):	HEAD=1
	if len(y[14]):	MALTY=1
	if len(y[15]):	NUTTY=1
	if len(y[16]):	ROASTED=1
	if len(y[17]):	SMOKED=1
	if len(y[18]):	SWEET=1
	if len(y[19]):	TOASTED=1	

	print "\t\t\t\t'%s' : (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)," %(r.sub('', y[0].lower()), PERCENT,SRM,MASHREQ,AROMATIC,BISCUIT,BODY,BURNT,CARAMEL,CHOCOLATE,COFFEE,GRAINY,HEAD,MALTY,NUTTY,ROASTED,SMOKED,SWEET,TOASTED)
print "}\n\n"


#	print NAME,PERCENT,SRM,"Mash",MASHREQ,"Aromatic",AROMATIC,"Biscuit",BISCUIT,"Body",BODY,"Burnt",BURNT,
#	print "Caramel",CARAMEL,"Chocolate",CHOCOLATE,"Coffee",COFFEE,"Grainy",GRAINY,"Head,",HEAD,
#	print "Malty",MALTY,"Nutty",NUTTY,"Roasted",ROASTED,"Smoked",SMOKED,"Sweet",SWEET,"Toasted",TOASTED

"""	
