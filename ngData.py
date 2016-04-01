
import re
import sys
import json
import _mysql	


class db:

	def __init__(self):
		self.query=""
		self.dbg=0
		self.entity=None


		self._entity=0		# not sure abou thtis

		# looking to use this a shim to avoid having to put in mysql.
		# this class itself was a shim around Gql language
		self._gProcesses=[]
		self._gSuppliers=[]
		self._gCompileText=[]
		self._gContributions=[]
		self._gWidgets=[]
		self._gProcess=[]
		self._gEquipment=[]
		self._gPurchases=[]
		self._gField=[]
		self._gBrewlogStep=[]
		self._gBrewlogs=[]
		self._gBrewlogStock=[]
		self._gAuthorisedUsers=[]
		self._gItems=[]
		self._gIngredients=[]
		self._gRecipes=[]
		self._gRecipeStats=[]
		self._gCalclogs=[]
		self._gLocations=[]
		self._gBeerStock=[]
		self._gBrewery=[]

		# give quick access to entitiy.. this might be hard to manage
		# so maybe we won't end up using it
		self._idxgProcesses={}
		self._idxgSuppliers={}
		self._idxgCompileText={}
		self._idxgContributions={}
		self._idxgWidgets={}
		self._idxgProcess={}
		self._idxgEquipment={}
		self._idxgPurchases={}
		self._idxgField={}
		self._idxgBrewlogStep={}
		self._idxgBrewlogs={}
		self._idxgBrewlogStock={}
		self._idxgAuthorisedUsers={}
		self._idxgItems={}
		self._idxgIngredients={}
		self._idxgRecipes={}
		self._idxgRecipeStats={}
		self._idxgCalclogs={}
		self._idxgLocations={}
		self._idxgBeerStock={}
		self._idxgBrewery={}


	def briefDebugStandaloneDatastore(self):
		print "gProcesses",len(self._gProcesses)
		print "gSuppliers",len(self._gSuppliers)
		print "gCompileText",len(self._gCompileText)
		print "gContributiosn",len(self._gContributions)
		print "gWidgets",len(self._gWidgets)
		print "gProcess",len(self._gProcess)
		print "gEquipment",len(self._gEquipment)
		print "gPurchases",len(self._gPurchases)
		print "gField",len(self._gField)
		print "gBrewlogStep",len(self._gBrewlogStep)
		print "gBrewlogs",len(self._gBrewlogs)
		print "gBrewlogStock",len(self._gBrewlogStock)
		print "gAuthorisedUsers",len(self._gAuthorisedUsers)
		print "gItems",len(self._gItems)
		print "gIngredients",len(self._gIngredients)
		print "gRecipes",len(self._gRecipes)
		print "gRecipeStats",len(self._gRecipeStats)
		print "gCalclogs",len(self._gCalclogs)
		print "gBrewery",len(self._gCalclogs)
		print "entity",self._entity	

	def get(self,query):
		table = query.split(" ")[3]
		g=None
		if table == "gProcesses":	g = gProcesses()
		if table == "gSuppliers":	g = gSuppliers()
		if table == "gCompileText":	g = gCompileText()
		if table == "gContributions":	g = gContributions()
		if table == "gWidgets":	g=gWidgets()
		if table == "gProcess":	g=gProcess()
		if table == "gEquipment":	g=gEquipment()
		if table == "gPurchases":	g=gPurchases()
		if table == "gField":	g=gField()
		if table == "gBrewlogStep":	g=gBrewlogStep()
		if table == "gBrewlogs":	g=gBrewlogs()
		if table == "gBrewlogStock":	g=gBrewlogStock()
		if table == "gAuthorisedUsers":	g=gAuthorisedUsers()
		if table == "gItems":	g=gItems()
		if table == "gIngredients":	g=gIngredients()
		if table == "gRecipes":	g=gRecipes()
		if table == "gRecipeStats":	g=gRecipeStats()
		if table == "gCalclogs":	g=gCalclogs()
		if table == "gLocation":	g=gLocations()
		if table == "gBeerStock":	g=gBeerStock()
		if table == "gBrewery":	g=gBrewery()

		if not g:
			print "ERROR: table %s not supported" %(table)
			sys.exit(0)

		return g


	
	def delete(self):
		query="DELETE FROM %s WHERE entity = %s" %(self.tableName, self.entity)
		mysql=self.connect()
		if self.dbg > 0:	sys.stderr.write("Delete: %s\n" %(query))
		if mysql:
			self.con.query(query)
		self=None
		
#		print "TODO: need to test if delete with mysql-less-shim works!"
		# think we probably should remove us from the list,
		# or maybe set entity to -1

	def brief(self):
		sys.stderr.write("%s" %(self.entity))
		if self.__dict__.has_key("recipe"):
			sys.stderr.write(" %s" %(self.recipe))
		if self.__dict__.has_key("recipename"):
			sys.stderr.write(" %s" %(self.recipename))
		if self.__dict__.has_key("ingredient"):
			sys.stderr.write(" %s" %(self.ingredient))
		sys.stderr.write("\n")



	def connect(self):
		try:
			self.con = _mysql.connect('localhost', 'brewerslab','beer','brewerslab')
			return True
		except:
			return False

	def fetch(self, numResults=1):
		mysql = self.connect()
		if mysql:
			# if using
			if self.dbg > 0:	sys.stderr.write("Fetch: %s\n" %(numResults))
			query="%s LIMIT 0,%s" %(self.query,numResults)
			ourResults=[]
			if self.dbg > 0:	sys.stderr.write("MYSQL: %s\n" %(query))
		
			#sys.stderr.write(query+"\n")
			self.con.query( query)

			result = self.con.use_result()
			row = result.fetch_row()
			while row:

				g=self.get(query)
				if self.dbg > 4:	sys.stderr.write("ROW: %s\n" %(row))
				g.populate( row )
				ourResults.append(g)

				row = result.fetch_row()


		if not mysql:
			tableName = self.query.split("FROM ")[1].split(" WHERE")[0]
			# not going to win any prizes for efficiency, but would rather take 5 minutes
			# and not have to keep re-writing things..... double shims dont' come for free

			# set a blank set of results
			ourResults=[]
			ourDict=self.__dict__["_%s" %(tableName) ]
			for candidate in ourDict:
				if self.dbg:	print candidate,"<<<<<<<candidate",candidate.entity
#


				valIndex=None
				valComparison=None
				valMatch=True
				valVariable=None
				c = len(self.argAssignments) -1 
				while c >= 0:
					# this differs from what we have in GqlQuery()
					# in GqlQuery() we use c>0. I think this is because of
					# ana ssumption that owner will be added in.
					# 
					# this must work differently because we can't pop
					# as the list is by reference not by value

					if self.argAssignments[c].count(":") == 1:
						valIndex=self.argAssignments[c]
					elif self.argAssignments[c].count("="):
						valComparison=self.argAssignments[c]
					elif self.argAssignments[c].count("AND"):
						AND="IMPLICT"
					elif self.argAssignments[c].count("OR"):
						print "OR arguments cannot be supported now"
						sys.exit(9999)
					elif self.argAssignments[c].count(">"):
						valComparison=self.argAssignments[c]
					elif self.argAssignments[c].count(">="):
						valComparison=self.argAssignments[c]
					elif self.argAssignments[c].count("<="):
						valComparison=self.argAssignments[c]
					elif self.argAssignments[c].count("<"):
						valComparison=self.argAssignments[c]
					else:
						valVariable=self.argAssignments[c]
					c=c -1
		
					if valIndex and valComparison and valVariable:	
						if self.dbg: print "\t(",valIndex,")",self.queryargs[ int(valIndex[1:])-1 ], valComparison,"(",valVariable,")",candidate.__dict__[ valVariable ]
#						print "currently",valMatch
						
						if valComparison == "=":
							if not candidate.__dict__[ valVariable ] == self.queryargs[int(valIndex[1:])-1 ]:	valMatch=False
						elif valComparison == ">":	## assumption we will convert to floats
							if not float(candidate.__dict__[ valVariable ]) > float(self.queryargs[int(valIndex[1:])-1 ]):	valMatch=False
	
						elif valComparison == ">=":	## assumption we will convert to floats
							if not float(candidate.__dict__[ valVariable ]) > float(self.queryargs[int(valIndex[1:])-1 ]):	valMatch=False
						elif valComparison == "<=":	## assumption we will convert to floats
							if not float(candidate.__dict__[ valVariable ]) > float(self.queryargs[int(valIndex[1:])-1 ]):	valMatch=False
						elif valComparison == "<":	## assumption we will convert to floats
							if not float(candidate.__dict__[ valVariable ]) > float(self.queryargs[int(valIndex[1:])-1 ]):	valMatch=False
						
						valIndex=None
						valComparison=None
						valVariable=None
				if valMatch and candidate.entity > 0:
					ourResults.append( candidate )


		return ourResults



	def GqlQuery(self, query, *queryargs):
		# Queries need to be well formed:
		#   ' :n'   not ': n'
		

		# 
		# another constraint here, is that selective SELECTS's aren't implemented.
		# furthermore, the start of the query must be well formed
		# it must be "SELECT * FROM <<<>>>>> WHERE"
		#
		
		if self.dbg > 0:	sys.stderr.write("Query: %s\n" %(query))		
		# need to handle arguments
		g = self.get(query)
		ar=0
		if len(queryargs) > 0:
			argAssignments=query.split(" ORDER ")[0].split("WHERE ")[1].split(" ")
			self.argAssignments=query.split(" ORDER ")[0].split("WHERE ")[1].split(" ")
			if self.dbg > 1:	sys.stderr.write("pre-argargumnets: %s\n" %(argAssignments))
			c = len(argAssignments) -1 


			# There is probably an assumption built in here that the first 
			# argument for the query is *always* owner.
			# in fetch() we've used c >= 0 as it seems to make more sense
			while c > 0:
				if argAssignments[c].count(":") == 1:
					argAssignments.pop(c)
				elif argAssignments[c].count("="):
					argAssignments.pop(c)
				elif argAssignments[c].count("AND"):
					argAssignments.pop(c)
				elif argAssignments[c].count("OR"):
					argAssignments.pop(c)
					print "OR arguments cannot be supported now"
					sys.exit(9999)
				elif argAssignments[c].count(">"):
					argAssignments.pop(c)
				elif argAssignments[c].count("<"):
					argAssignments.pop(c)
				elif argAssignments[c].count(">="):
					argAssignments.pop(c)
				elif argAssignments[c].count("<="):
					argAssignments.pop(c)
				c=c -1
			
			if self.dbg > 0:	sys.stderr.write("post-argargumnets: %s\n" %(argAssignments))

		# queryargs <---- this gives us the avlues for our query	
		self.queryargs=queryargs		# we need this later in our shim
		for queryArg in queryargs:
			ar=ar+1
			argn = re.compile('\s').sub('',argAssignments[ ar-1 ])
			
			if g.types[argn] == "char":
				query =re.compile(" :%s" %(ar)).sub("'%s'" %(queryargs[ar-1]), query)
			else:
				query =re.compile(" :%s" %(ar)).sub("%s" %(queryargs[ar-1]),query)


		if len(queryargs) > 0 and self.dbg >0 :	sys.stderr.write("QUERY: %s\n" %(query))
		self.query=query
#		sys.stderr.write("QUERY: %s\n" %(query))
		return self


		
	def put(self):
		# if we have mysql then we need to do a persitent sql query
		# if we don't have mysql then we do everything in memory and can quit.
		mysql = self.connect()


		if mysql:
			
			if self.entity:
				if self.dbg > 0:	sys.stderr.write("DB Update required %s\n" %(self.entity))
				query = self.updateSql()
			else:
				if self.dbg > 0:	sys.stderr.write("DB Insert required\n")
				if self.dbg > 0:	sys.stderr.write(" %s\n" %(self.tableName))
				query = self.insertSql()
			if self.dbg > 0:	sys.stderr.write("%s\n" %(query))
			self.con.query(query)



		if not mysql:

			if not self.entity:
				"""
				print "need to think about entity -insert"
				print "how do we get a unique number"	
				print "and how to get our parent object"
				print "parent object is a  more fundamental problem to solve"
				print "then entities will be easy"
				print self
				print self.db
				print self.db.entity				
				print self.tableName			
				"""
				self.db._entity=self.db._entity+1
				self.entity=self.db._entity
#				print "putting entity >>>>>>",self.entity
				self.db.__dict__["_%s" %(self.tableName) ].append( self )


			# Note: because we are in memory we don't actually need to do anything to get an update		
#			if self.entity:
##				print selif
##				print "need to think about -update"
#			print self.tableName
#			print self
#			sys.exit(42)

	def toString(self):
		print self,self.entity
		for x in self.types:
			if not x == "entity":
				print " ",x,self.__dict__[x]



class gProcesses(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.owner=""
		self.process=""
		self.con=None
		self.types = {
			'owner' : 'char',
			'process' : 'char',
			'entity' : 'numeric',
		}
		self.tableName="gProcesses"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gProcesses VALUES (null,'%s','%s');\n" %(self.owner,self.process)	

	def updateSql(self):
		return "UPDATE gProcesses SET owner = '%s', process = '%s' WHERE entity = %s ;\n" %(self.owner,self.process,self.entity)	
		

	def populate(self,row):
		((self.entity,self.owner,self.process),)=row
		


class gBrewery(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.breweryname=""
		self.brewerytwitter=""
		self.overheadperlitre=0.00
		self.cost=0.00;
		self.litres=0.00;
		self.equipcost=0.00;
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'breweryname' : 'char',
			'overheadperlitre' : 'numeric',
			'brewerytwitter' : 'char',
			'cost': 'numeric',
			'litres':'numeric',
			'equipcost':'numeric',
		}
		self.tableName="gBrewery"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gBrewery VALUES (null, '%s', '%s',%s, '%s',%s,'%s',%s,%s,%s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.breweryname) ,self.overheadperlitre, _mysql.escape_string(self.brewerytwitter),self.cost,self.litres,self.equipcost )

	def updateSql(self):
		return "UPDATE gBrewery SET  owner = '%s', breweryname  = '%s', overheadperlitre=%s,brewerytwitter = '%s', cost=%s, litres=%s, equipcost=%s WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.breweryname), self.overheadperlitre, _mysql.escape_string(self.brewerytwitter), self.cost,self.litres,self.equipcost, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.breweryname, overheadperlitre,self.brewerytwitter,cost,litres,equipcost ),)=row
		self.overheadperlitre=float(overheadperlitre)
		self.litres=float(litres)
		self.cost=float(cost)
		self.equipcost=float(equipcost)


class gSuppliers(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.supplier=""
		self.supplierName=""
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'supplier' : 'char',
			'supplierName' : 'char',
		}
		self.tableName="gSuppliers"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gSuppliers VALUES (null, '%s', '%s', '%s');" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.supplier) , _mysql.escape_string(self.supplierName) )

	def updateSql(self):
		return "UPDATE gSuppliers SET  owner = '%s', supplier = '%s', supplierName = '%s' WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.supplier), _mysql.escape_string(self.supplierName), self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.supplier, self.supplierName),)=row




class gCompileText(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.process=""
		self.activityNum=0
		self.stepNum=0
		self.subStepNum=0
		self.toReplace=[]
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'stepNum' : 'numeric',
			'entity' : 'numeric',
			'subStepNum' : 'numeric',
			'entity' : 'numeric',
			'toReplace' : 'list',
		}
		self.tableName="gCompileText"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gCompileText VALUES (null, '%s', '%s', %s, %s, %s, '%s');" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.process) , self.activityNum , self.stepNum , self.subStepNum , _mysql.escape_string( json.dumps(self.toReplace)) )

	def updateSql(self):
		return "UPDATE gCompileText SET  owner = '%s', process = '%s', activityNum = %s, stepNum = %s, subStepNum = %s, toReplace = '%s' WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.process), self.activityNum, self.stepNum, self.subStepNum, _mysql.escape_string(json.dumps( self.toReplace)), self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.process, self.activityNum, self.stepNum, self.subStepNum, self.toReplace),)=row

		for x in self.types:
			if self.types[x] == "list":
				if len(self.__dict__[x]) > 2:
					self.__dict__[x]  = json.loads( self.__dict__[x])
				else:
					self.__dict__[x] = []




class gCalclogs(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.recipe=""
		self.brewlog=""
		self.calclog=""
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'recipe' : 'char',
			'brewlog': 'char',
			'calclog' : 'char',
		}
		self.tableName="gCalclogs"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gCalclogs VALUES (null, '%s', '%s','%s','%s');" %(_mysql.escape_string(self.owner),_mysql.escape_string(self.recipe),_mysql.escape_string(self.brewlog),_mysql.escape_string(self.calclog))

	def updateSql(self):
		return "UPDATE gCalclogs SET  owner = '%s', recipe='%s', brewlog='%s',calclog = '%s' WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.recipe),_mysql.escape_string(self.brewlog), _mysql.escape_string(self.calclog), self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.recipe,self.brewlog,self.calclog),)=row





class gContributions(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.recipeName=""
		self.ingredientType=""
		self.ingredient=""
		self.hopAddAt=0.00
		self.ibu=0.00
		self.srm=0.00
		self.gravity=0.00
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'recipeName' : 'char',
			'entity' : 'numeric',
			'ingredientType' : 'char',
			'entity' : 'numeric',
			'ingredient' : 'char',
			'entity' : 'numeric',
			'hopAddAt' : 'numeric',
			'entity' : 'numeric',
			'ibu' : 'numeric',
			'entity' : 'numeric',
			'srm' : 'numeric',
			'entity' : 'numeric',
			'gravity' : 'numeric',
		}
		self.tableName="gContributions"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gContributions VALUES (null, '%s', '%s', '%s', '%s', %s, %s, %s, %s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.recipeName) , _mysql.escape_string(self.ingredientType) , _mysql.escape_string(self.ingredient) , self.hopAddAt , self.ibu , self.srm , self.gravity )

	def updateSql(self):
		return "UPDATE gContributions SET  owner = '%s', recipeName = '%s', ingredientType = '%s', ingredient = '%s', hopAddAt = %s, ibu = %s, srm = %s, gravity = %s WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.recipeName), _mysql.escape_string(self.ingredientType), _mysql.escape_string(self.ingredient), self.hopAddAt, self.ibu, self.srm, self.gravity, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.recipeName, self.ingredientType, self.ingredient, hopAddAt, ibu, srm, gravity),)=row
		self.hopAddAt=float(hopAddAt)
		self.ibu=float(ibu)
		self.srm=float(srm)
		self.gravity=float(gravity)


class gWidgets(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.process=""
		self.activityNum=0
		self.stepNum=0
		self.widgetName=""
		self.widget=""
		self.widgetValues=[]
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'stepNum' : 'numeric',
			'entity' : 'numeric',
			'widgetName' : 'char',
			'entity' : 'numeric',
			'widget' : 'char',
			'entity' : 'numeric',
			'widgetValues' : 'list',
		}
		self.tableName="gWidgets"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gWidgets VALUES (null, '%s', '%s', %s, %s, '%s', '%s', '%s');" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.process) , self.activityNum , self.stepNum , _mysql.escape_string(self.widgetName) , _mysql.escape_string(self.widget) , _mysql.escape_string( json.dumps(self.widgetValues)) )

	def updateSql(self):
		return "UPDATE gWidgets SET  owner = '%s', process = '%s', activityNum = %s, stepNum = %s, widgetName = '%s', widget = '%s', widgetValues = '%s' WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.process), self.activityNum, self.stepNum, _mysql.escape_string(self.widgetName), _mysql.escape_string(self.widget), _mysql.escape_string(json.dumps( self.widgetValues)), self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.process, self.activityNum, self.stepNum, self.widgetName, self.widget, self.widgetValues),)=row
		for x in self.types:
			if self.types[x] == "list":
				if len(self.__dict__[x]) > 2:
					self.__dict__[x]  = json.loads( self.__dict__[x])
				else:
					self.__dict__[x] = []


class gProcess(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.process=""
		self.stepName=""
		self.stepTitle=""
		self.activityNum=0
		self.stepNum=0
		self.subStepNum=0
		self.text=""
		self.attention=""
		self.timerName=""
		self.timerTime=0
		self.fixed_boil_off=0.00
		self.fixed_cool_off=0.00
		self.percentage_boil_off=0.00
		self.percentage_cool_off=0.00
		self.auto=""
		self.needToComplete=0
		self.compileStep=0
		self.img=[]
		self.conditional=[]
		self.numSubSteps=0
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'stepName' : 'char',
			'entity' : 'numeric',
			'stepTitle' : 'char',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'stepNum' : 'numeric',
			'entity' : 'numeric',
			'subStepNum' : 'numeric',
			'entity' : 'numeric',
			'text' : 'char',
			'entity' : 'numeric',
			'img' : 'list',
			'entity' : 'numeric',
			'attention' : 'char',
			'entity' : 'numeric',
			'timerName' : 'char',
			'entity' : 'numeric',
			'timerTime' : 'numeric',
			'entity' : 'numeric',
			'fixed_boil_off' : 'numeric',
			'entity' : 'numeric',
			'fixed_cool_off' : 'numeric',
			'entity' : 'numeric',
			'percentage_boil_off' : 'numeric',
			'entity' : 'numeric',
			'percentage_cool_off' : 'numeric',
			'entity' : 'numeric',
			'auto' : 'char',
			'entity' : 'numeric',
			'needToComplete' : 'numeric',
			'entity' : 'numeric',
			'compileStep' : 'numeric',
			'entity' : 'numeric',
			'conditional' : 'list',
			'numSubSteps':'numeric',
		}
		self.tableName="gProcess"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value





	def insertSql(self):
		if self.needToComplete:
			needToComplete=1
		else:
			needToComplete=0
		if self.compileStep:
			compileStep=1
		else:
			compileStep=0

		return "INSERT INTO gProcess VALUES (null, '%s', '%s', '%s', '%s', %s, %s, %s, '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, '%s', %s, %s, '%s',%s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.process) , _mysql.escape_string(self.stepName) , _mysql.escape_string(self.stepTitle) , self.activityNum , self.stepNum , self.subStepNum , _mysql.escape_string(self.text) , _mysql.escape_string( json.dumps(self.img)) , _mysql.escape_string(self.attention) , _mysql.escape_string(self.timerName) , self.timerTime , self.fixed_boil_off , self.fixed_cool_off , self.percentage_boil_off , self.percentage_cool_off , _mysql.escape_string(self.auto) , needToComplete , compileStep , _mysql.escape_string( json.dumps(self.conditional)),self.numSubSteps )

	def updateSql(self):
		if self.needToComplete:
			needToComplete=1
		else:
			needToComplete=0
		if self.compileStep:
			compileStep=1
		else:
			compileStep=0
		return "UPDATE gProcess SET  owner = '%s', process = '%s', stepName = '%s', stepTitle = '%s', activityNum = %s, stepNum = %s, subStepNum = %s, text = '%s', img = '%s', attention = '%s', timerName = '%s', timerTime = %s, fixed_boil_off = %s, fixed_cool_off = %s, percentage_boil_off = %s, percentage_cool_off = %s, auto = '%s', needToComplete = %s, compileStep = %s, conditional = '%s',numSubSteps=%s WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.process), _mysql.escape_string(self.stepName), _mysql.escape_string(self.stepTitle), self.activityNum, self.stepNum, self.subStepNum, _mysql.escape_string(self.text), _mysql.escape_string(json.dumps( self.img)), _mysql.escape_string(self.attention), _mysql.escape_string(self.timerName), self.timerTime, self.fixed_boil_off, self.fixed_cool_off, self.percentage_boil_off, self.percentage_cool_off, _mysql.escape_string(self.auto), needToComplete, compileStep, _mysql.escape_string(json.dumps( self.conditional)), self.numSubSteps,self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.process, self.stepName, self.stepTitle, self.activityNum, self.stepNum, self.subStepNum, self.text, self.img, self.attention, self.timerName, self.timerTime, fixed_boil_off, fixed_cool_off, percentage_boil_off, percentage_cool_off, self.auto, needToComplete, compileStep, self.conditional,self.numSubSteps),)=row
		for x in self.types:
			if self.types[x] == "list":
				if len(self.__dict__[x] ) > 2:
					self.__dict__[x]  = json.loads( self.__dict__[x])
				else:
					self.__dict__[x]  = []

		self.fixed_boil_off=float(fixed_boil_off)
		self.fixed_cool_off=float(fixed_cool_off)
		self.percentage_boil_off=float(percentage_boil_off)
		self.percentage_cool_off=float(percentage_cool_off)

		if int(needToComplete) == 1:
			self.needToComplete=True
		else:
			self.needToComplete=False
		if int(compileStep)  == 1:
			self.compileStep=True
		else:
			self.compileStep=False


		if not self.conditional:	self.conditional=[]
		if not self.img:	self.img=[]
		if not self.auto:	self.auto=""
		if not self.stepTitle:	self.stepTitle=""
		
class gEquipment(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.process=""
		self.name=""
		self.equipment=""
		self.dead_space=0.00
		self.activityNum=0
		self.heatPower=0.00
		self.volume=0.00
		self.mustSterilise=0
		self.boilVolume=0.00
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'name' : 'char',
			'entity' : 'numeric',
			'equipment' : 'char',
			'entity' : 'numeric',
			'dead_space' : 'numeric',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'heatPower' : 'numeric',
			'entity' : 'numeric',
			'volume' : 'numeric',
			'entity' : 'numeric',
			'mustSterilise' : 'numeric',
			'entity' : 'numeric',
			'boilVolume' : 'numeric',
		}
		self.tableName="gEquipment"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		if self.mustSterilise:
			mustSterilise=1
		else:
			mustSterilise=0
		return "INSERT INTO gEquipment VALUES (null, '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.process) , _mysql.escape_string(self.name) , _mysql.escape_string(self.equipment) , self.dead_space , self.activityNum , self.heatPower , self.volume , mustSterilise , self.boilVolume )

	def updateSql(self):
		if self.mustSterilise:
			mustSterilise=1
		else:
			mustSterilise=0
		return "UPDATE gEquipment SET  owner = '%s', process = '%s', name = '%s', equipment = '%s', dead_space = %s, activityNum = %s, heatPower = %s, volume = %s, mustSterilise = %s, boilVolume = %s WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.process), _mysql.escape_string(self.name), _mysql.escape_string(self.equipment), self.dead_space, self.activityNum, self.heatPower, self.volume, mustSterilise, self.boilVolume, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.process, self.name, self.equipment, dead_space, self.activityNum, heatPower, volume, mustSterilise, boilVolume),)=row
		self.dead_space=float(dead_space)
		self.heatPower=float(heatPower)
		self.volume=float(volume)
		self.boilVolume=float(boilVolume)
		
		if int(mustSterilise) == 1:
			self.mustSterilise=True
		else:
			self.mustSterilise=False



class gPurchases(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.storecategory=""
		self.storeitem=""
		self.itemcategory=""
		self.itemsubcategory=""
		self.purchaseQty=0.00
		self.qty=0.00
		self.originalQty=0.00
		self.qtyMultiple=0.00
		self.wastageFixed=0.00
		self.purchaseDate=0
		self.bestBeforeEnd=0
		self.supplier=""
		self.purchaseCost=0.00
		self.stocktag=""
		self.hopActualAlpha=0.00
		self.unit=""
		self.volume=0.00
		self.willNotExpire=0
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'storecategory' : 'char',
			'entity' : 'numeric',
			'storeitem' : 'char',
			'entity' : 'numeric',
			'itemcategory' : 'char',
			'entity' : 'numeric',
			'itemsubcategory' : 'char',
			'entity' : 'numeric',
			'purchaseQty' : 'numeric',
			'entity' : 'numeric',
			'qty' : 'numeric',
			'entity' : 'numeric',
			'originalQty' : 'numeric',
			'entity' : 'numeric',
			'qtyMultiple' : 'numeric',
			'entity' : 'numeric',
			'wastageFixed' : 'numeric',
			'entity' : 'numeric',
			'purchaseDate' : 'numeric',
			'entity' : 'numeric',
			'bestBeforeEnd' : 'numeric',
			'entity' : 'numeric',
			'supplier' : 'char',
			'entity' : 'numeric',
			'purchaseCost' : 'numeric',
			'entity' : 'numeric',
			'stocktag' : 'char',
			'entity' : 'numeric',
			'hopActualAlpha' : 'numeric',
			'entity' : 'numeric',
			'unit' : 'char',
			'entity' : 'numeric',
			'volume' : 'numeric',
			'entity' : 'numeric',
			'willNotExpire' : 'numeric',
		}
		self.tableName="gPurchases"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value


	def insertSql(self):
		if self.willNotExpire:
			willNotExpire=1
		else:
			willNotExpire=0
		return "INSERT INTO gPurchases VALUES (null, '%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, '%s', %s, '%s', %s, '%s', %s, %s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.storecategory) , _mysql.escape_string(self.storeitem) , _mysql.escape_string(self.itemcategory) , _mysql.escape_string(self.itemsubcategory) , self.purchaseQty , self.qty , self.originalQty , self.qtyMultiple , self.wastageFixed , self.purchaseDate , self.bestBeforeEnd , _mysql.escape_string(self.supplier) , self.purchaseCost , _mysql.escape_string(self.stocktag) , self.hopActualAlpha , _mysql.escape_string(self.unit) , self.volume , willNotExpire )

	def updateSql(self):
		if self.willNotExpire:
			willNotExpire=1
		else:
			willNotExpire=0
		return "UPDATE gPurchases SET  owner = '%s', storecategory = '%s', storeitem = '%s', itemcategory = '%s', itemsubcategory = '%s', purchaseQty = %s, qty = %s, originalQty = %s, qtyMultiple = %s, wastageFixed = %s, purchaseDate = %s, bestBeforeEnd = %s, supplier = '%s', purchaseCost = %s, stocktag = '%s', hopActualAlpha = %s, unit = '%s', volume = %s, willNotExpire = %s WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.storecategory), _mysql.escape_string(self.storeitem), _mysql.escape_string(self.itemcategory), _mysql.escape_string(self.itemsubcategory), self.purchaseQty, self.qty, self.originalQty, self.qtyMultiple, self.wastageFixed, self.purchaseDate, self.bestBeforeEnd, _mysql.escape_string(self.supplier), self.purchaseCost, _mysql.escape_string(self.stocktag), self.hopActualAlpha, _mysql.escape_string(self.unit), self.volume, willNotExpire, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.storecategory, self.storeitem, self.itemcategory, self.itemsubcategory, purchaseQty, qty, originalQty, qtyMultiple, wastageFixed, self.purchaseDate, self.bestBeforeEnd, self.supplier, purchaseCost, self.stocktag, hopActualAlpha, self.unit, volume, willNotExpire),)=row

		self.purchaseQty=float(purchaseQty)
		self.qty=float(qty)
		self.originalQty=float(originalQty)
		self.qtyMultiple=float(qtyMultiple)
		self.wastageFixed=float(wastageFixed)
		self.purchaseCost=float(purchaseCost)
		self.hopActualAlpha=float(hopActualAlpha)
		self.volume=float(volume)
	

		if int(willNotExpire) == 1:
			self.willNotExpire=True
		else:
			self.willNotExpire=False


class gField(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.stepNum=0
		self.activityNum=0
		self.process=""
		self.brewlog=""
		self.recipe=""
		self.fieldLabel=""
		self.fieldKey=""
		self.fieldVal=""
		self.fieldWidget=""
		self.fieldTimestamp=0
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'stepNum' : 'numeric',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'brewlog' : 'char',
			'entity' : 'numeric',
			'recipe' : 'char',
			'entity' : 'numeric',
			'fieldLabel' : 'char',
			'entity' : 'numeric',
			'fieldKey' : 'char',
			'entity' : 'numeric',
			'fieldVal' : 'char',
			'entity' : 'numeric',
			'fieldWidget' : 'char',
			'entity' : 'numeric',
			'fieldTimestamp' : 'numeric',
		}
		self.tableName="gField"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		return "INSERT INTO gField VALUES (null, '%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s);" %( _mysql.escape_string(self.owner) , self.stepNum , self.activityNum , _mysql.escape_string(self.process) , _mysql.escape_string(self.brewlog) , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.fieldLabel) , _mysql.escape_string(self.fieldKey) , _mysql.escape_string(self.fieldVal) , _mysql.escape_string(self.fieldWidget) , self.fieldTimestamp )

	def updateSql(self):
		return "UPDATE gField SET  owner = '%s', stepNum = %s, activityNum = %s, process = '%s', brewlog = '%s', recipe = '%s', fieldLabel = '%s', fieldKey = '%s', fieldVal = '%s', fieldWidget = '%s', fieldTimestamp = %s WHERE entity = %s " %( _mysql.escape_string(self.owner), self.stepNum, self.activityNum, _mysql.escape_string(self.process), _mysql.escape_string(self.brewlog), _mysql.escape_string(self.recipe), _mysql.escape_string(self.fieldLabel), _mysql.escape_string(self.fieldKey), _mysql.escape_string(self.fieldVal), _mysql.escape_string(self.fieldWidget), self.fieldTimestamp, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.stepNum, self.activityNum, self.process, self.brewlog, self.recipe, self.fieldLabel, self.fieldKey, self.fieldVal, self.fieldWidget, self.fieldTimestamp),)=row



class gBrewlogStep(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.brewlog=""
		self.owner=""
		self.activityNum=0
		self.stepNum=0
		self.subStepNum=0
		self.sortIndex=0
		self.recipe=""
		self.stepName=""
		self.completed=0
		self.stepStartTime=0
		self.stepEndTime=0
		self.needToComplete=0
		self.subStepsCompleted=0
		self.compileStep=0
		self.conditional=""
		self.timerName=""
		self.timerTime=0
		self.numSubSteps=0
		self.types = {
			'entity' : 'numeric',
			'brewlog' : 'char',
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'stepNum' : 'numeric',
			'entity' : 'numeric',
			'subStepNum' : 'numeric',
			'entity' : 'numeric',
			'sortIndex' : 'numeric',
			'entity' : 'numeric',
			'recipe' : 'char',
			'entity' : 'numeric',
			'stepName' : 'char',
			'entity' : 'numeric',
			'completed' : 'numeric',
			'entity' : 'numeric',
			'stepStartTime' : 'numeric',
			'entity' : 'numeric',
			'stepEndTime' : 'numeric',
			'entity' : 'numeric',
			'needToComplete' : 'numeric',
			'entity' : 'numeric',
			'subStepsCompleted' : 'numeric',
			'entity' : 'numeric',
			'compileStep' : 'numeric',
			'entity' : 'numeric',
			'conditional' : 'char',
			'entity' : 'numeric',
			'timerName' : 'char',
			'entity' : 'numeric',
			'timerTime' : 'numeric',
			'numSubSteps' : 'numeric',
		}
		self.tableName="gBrewlogStep"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		if self.completed:
			completed=1
		else:	
			completed=0
		if self.needToComplete:
			needToComplete=1
		else:
			needToComplete=0
		if self.subStepsCompleted:
			subStepsCompleted=1
		else:
			subStepsCompleted=0
		if self.compileStep:
			compileStep=1
		else:
			compileStep=0
		if not self.brewlog:	self.brewlog=""
		return "INSERT INTO gBrewlogStep VALUES (null, '%s', '%s', %s, %s, %s, %s, '%s', '%s', %s, %s, %s, %s, %s, %s, '%s', '%s', %s,%s);" %( _mysql.escape_string(self.brewlog) , _mysql.escape_string(self.owner) , self.activityNum , self.stepNum , self.subStepNum , self.sortIndex , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.stepName) , completed , self.stepStartTime , self.stepEndTime , needToComplete , subStepsCompleted , compileStep , _mysql.escape_string(self.conditional) , _mysql.escape_string(self.timerName) , self.timerTime ,self.numSubSteps)

	def updateSql(self):
		if self.completed:
			completed=1
		else:	
			completed=0
		if self.needToComplete:
			needToComplete=1
		else:
			needToComplete=0
		if self.subStepsCompleted:
			subStepsCompleted=1
		else:
			subStepsCompleted=0
		if self.compileStep:
			compileStep=1
		else:
			compileStep=0
		if not self.brewlog:	self.brewlog=""
		return "UPDATE gBrewlogStep SET  brewlog = '%s', owner = '%s', activityNum = %s, stepNum = %s, subStepNum = %s, sortIndex = %s, recipe = '%s', stepName = '%s', completed = %s, stepStartTime = %s, stepEndTime = %s, needToComplete = %s, subStepsCompleted = %s, compileStep = %s, conditional = '%s', timerName = '%s', timerTime = %s, numSubSteps =%s WHERE entity = %s " %( _mysql.escape_string(self.brewlog), _mysql.escape_string(self.owner), self.activityNum, self.stepNum, self.subStepNum, self.sortIndex, _mysql.escape_string(self.recipe), _mysql.escape_string(self.stepName), completed, self.stepStartTime, self.stepEndTime, needToComplete, subStepsCompleted, compileStep, _mysql.escape_string(self.conditional), _mysql.escape_string(self.timerName), self.timerTime,self.numSubSteps, self.entity)


	def populate(self,row):
		(( self.entity , self.brewlog, self.owner, self.activityNum, self.stepNum, self.subStepNum, self.sortIndex, self.recipe, self.stepName, completed, self.stepStartTime, self.stepEndTime, needToComplete, subStepsCompleted, compileStep, self.conditional, self.timerName, self.timerTime,self.numSubSteps),)=row
		if int(completed) ==1:
			self.completed=True
		else:	
			self.completed=False
		if int(needToComplete) ==1:
			self.needToComplete=True
		else:
			self.needToComplete=False
		if int(subStepsCompleted) == 1:
			self.subStepsCompleted=True
		else:
			self.subStepsCompleted=False
		if int(compileStep) == 1:
			self.compileStep=True
		else:
			self.compileStep=False


class gBrewlogs(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.brewlog=""
		self.recipe=""
		self.owner=""
		self.brewhash=""
		self.realrecipe=""
		self.boilVolume=0.00
		self.process=""
		self.largeImage=""
		self.smallImage=""
		self.brewdate=0
		self.brewdate2=0
		self.bottledate=0
		self.types = {
			'entity' : 'numeric',
			'brewlog' : 'char',
			'entity' : 'numeric',
			'recipe' : 'char',
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'brewhash' : 'char',
			'entity' : 'numeric',
			'realrecipe' : 'char',
			'entity' : 'numeric',
			'boilVolume' : 'numeric',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'largeImage' : 'char',
			'entity' : 'numeric',
			'smallImage' : 'char',
			'entity' : 'numeric',
			'brewdate' : 'numeric',
			'entity' : 'numeric',
			'brewdate2' : 'numeric',
			'entity' : 'numeric',
			'bottledate' : 'numeric',
		}
		self.tableName="gBrewlog"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
#| entity | owner            | brewlog    | recipe           | brewhash                                                             | realrecipe            | boilVolume | process   | largeImage | smallImage | brewdate | brewdate2 | bottledate |


		return "INSERT INTO gBrewlogs VALUES (null, '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', %s, %s, %s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.brewlog) , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.brewhash) , _mysql.escape_string(self.realrecipe) , self.boilVolume , _mysql.escape_string(self.process) , _mysql.escape_string(self.largeImage) , _mysql.escape_string(self.smallImage) , self.brewdate , self.brewdate2 , self.bottledate )

	def updateSql(self):
		return "UPDATE gBrewlogs SET  brewlog = '%s', recipe = '%s', owner = '%s', brewhash = '%s', realrecipe = '%s', boilVolume = %s, process = '%s', largeImage = '%s', smallImage = '%s', brewdate = %s, brewdate2 = %s, bottledate = %s WHERE entity = %s " %( _mysql.escape_string(self.brewlog), _mysql.escape_string(self.recipe), _mysql.escape_string(self.owner), _mysql.escape_string(self.brewhash), _mysql.escape_string(self.realrecipe), self.boilVolume, _mysql.escape_string(self.process), _mysql.escape_string(self.largeImage), _mysql.escape_string(self.smallImage), self.brewdate, self.brewdate2, self.bottledate, self.entity)


	def populate(self,row):
		(( self.entity , self.owner,self.brewlog, self.recipe, self.brewhash, self.realrecipe, boilVolume, self.process, self.largeImage, self.smallImage, self.brewdate, self.brewdate2, self.bottledate),)=row


		self.boilVolume=float(boilVolume)


class gBrewlogStock(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.brewlog=""
		self.recipe=""
		self.owner=""
		self.unit=""
		self.storecategory=""
		self.activityNum=0
		self.stock=""
		self.qty=0.00
		self.cost=0.00
		self.subcategory=""
		self.costrefund=0
		self.stocktag=""
		self.types = {
			'entity' : 'numeric',
			'brewlog' : 'char',
			'entity' : 'numeric',
			'recipe' : 'char',
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'unit' : 'char',
			'entity' : 'numeric',
			'storecategory' : 'char',
			'entity' : 'numeric',
			'activityNum' : 'numeric',
			'entity' : 'numeric',
			'stock' : 'char',
			'entity' : 'numeric',
			'qty' : 'numeric',
			'entity' : 'numeric',
			'cost' : 'numeric',
			'entity' : 'numeric',
			'subcategory' : 'char',
			'entity' : 'numeric',
			'costrefund' : 'numeric',
			'entity' : 'numeric',
			'stocktag' : 'char',
		}
		self.tableName="gBrewlogStock"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		if self.costrefund: 
			costrefund=1
		else:
			costrefund=0

		return "INSERT INTO gBrewlogStock VALUES (null, '%s', '%s', '%s', '%s', '%s', %s, '%s', %s, %s, '%s', %s, '%s');" %( _mysql.escape_string(self.brewlog) , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.owner) , _mysql.escape_string(self.unit) , _mysql.escape_string(self.storecategory) , self.activityNum , _mysql.escape_string(self.stock) , self.qty , self.cost , _mysql.escape_string(self.subcategory) , costrefund , _mysql.escape_string(self.stocktag) )

	def updateSql(self):
		if self.costrefund: 
			costrefund=1
		else:
			costrefund=0
		return "UPDATE gBrewlogStock SET  brewlog = '%s', recipe = '%s', owner = '%s', unit = '%s', storecategory = '%s', activityNum = %s, stock = '%s', qty = %s, cost = %s, subcategory = '%s', costrefund = %s, stocktag = '%s' WHERE entity = %s " %( _mysql.escape_string(self.brewlog), _mysql.escape_string(self.recipe), _mysql.escape_string(self.owner), _mysql.escape_string(self.unit), _mysql.escape_string(self.storecategory), self.activityNum, _mysql.escape_string(self.stock), self.qty, self.cost, _mysql.escape_string(self.subcategory), costrefund, _mysql.escape_string(self.stocktag), self.entity)


	def populate(self,row):
		(( self.entity , self.brewlog, self.recipe, self.owner, self.unit, self.storecategory, self.activityNum, self.stock, qty, cost, self.subcategory,costrefund, self.stocktag),)=row

		self.qty=float(qty)
		self.cost=float(cost)
		

		if int(costrefund) == 1: 
			self.costrefund=True
		else:
			self.costrefund=False


class gBeerStock(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.brewlog=""
		self.recipe=""
		self.stocktype=""
		self.location=""
		self.qty=0
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'brewlog' : 'char',
			'recipe' : 'char',
			'stocktype' : 'char',
			'location' : 'char',
			'qty' : 'numeric',
		}

		self.tableName="gBeerStock"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

		
		
	def insertSql(self):
		return "INSERT INTO gBeerStock VALUES (null, 'test@example.com', '%s', '%s', '%s','%s',%s);" %( _mysql.escape_string(self.brewlog) , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.stocktype) , _mysql.escape_string(self.location) , self.qty)

	def updateSql(self):
		return "UPDATE gBeerStock SET brewlog ='%s', recipe= '%s', stocktype ='%s', location='%s', qty =%s WHERE entity=%s " %( _mysql.escape_string(self.brewlog) , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.stocktype) , _mysql.escape_string(self.location ), self.qty, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.brewlog,self.recipe, self.stocktype, self.location,self.qty),)=row



class gAuthorisedUsers(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.authCookie=""
		self.authEmail=""
		self.authHash=""
		self.deviceId=""
		self.types = {
			'entity' : 'numeric',
			'authCookie' : 'char',
			'entity' : 'numeric',
			'authEmail' : 'char',
			'entity' : 'numeric',
			'authHash' : 'char',
			'entity' : 'numeric',
			'deviceId' : 'char',
		}

		self.tableName="gAuthorisedUsers"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

		
		
	def insertSql(self):
		return "INSERT INTO gAuthorisedUsers VALUES (null, '%s', '%s', '%s', '%s');" %( _mysql.escape_string(self.authCookie) , _mysql.escape_string(self.authEmail) , _mysql.escape_string(self.authHash) , _mysql.escape_string(self.deviceId) )

	def updateSql(self):
		return "UPDATE gAuthorisedUsers SET  authCookie = '%s', authEmail = '%s', authHash = '%s', deviceId = '%s' WHERE entity = %s " %( _mysql.escape_string(self.authCookie), _mysql.escape_string(self.authEmail), _mysql.escape_string(self.authHash), _mysql.escape_string(self.deviceId), self.entity)


	def populate(self,row):
		(( self.entity , self.authCookie, self.authEmail, self.authHash, self.deviceId),)=row



class gItems(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.majorcategory=""
		self.category=""
		self.subcategory=""
		self.name=""
		self.idx=""
		self.qtyMultiple=0.00
		self.unit=""
		self.colour=0.00
		self.aromatic=0
		self.biscuit=0
		self.body=0
		self.burnt=0
		self.caramel=0
		self.chocolate=0
		self.coffee=0
		self.grainy=0
		self.malty=0
		self.head=0
		self.nutty=0
		self.roasted=0
		self.smoked=0
		self.sweet=0
		self.toasted=0
		self.ppg=0.00
		self.hwe=0.00
		self.extract=0.00
		self.mustMash=0
		self.isAdjunct=0
		self.hopAlpha=0.00
		self.hopForm=""
		self.hopUse=""
		self.hopAddAt=0.00
		self.attenuation=0.00
		self.dosage=0.00
		self.wastageFixed=0.00
		self.styles=""
		self.description=""
		self.caprequired=0
		self.co2required=0
		self.isGrain=0
		self.fullvolume=0.00
		self.volume=0.00
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'majorcategory' : 'char',
			'entity' : 'numeric',
			'category' : 'char',
			'entity' : 'numeric',
			'subcategory' : 'char',
			'entity' : 'numeric',
			'name' : 'char',
			'entity' : 'numeric',
			'idx' : 'char',
			'entity' : 'numeric',
			'qtyMultiple' : 'numeric',
			'entity' : 'numeric',
			'unit' : 'char',
			'entity' : 'numeric',
			'colour' : 'numeric',
			'entity' : 'numeric',
			'aromatic' : 'numeric',
			'entity' : 'numeric',
			'biscuit' : 'numeric',
			'entity' : 'numeric',
			'body' : 'numeric',
			'entity' : 'numeric',
			'burnt' : 'numeric',
			'entity' : 'numeric',
			'caramel' : 'numeric',
			'entity' : 'numeric',
			'chocolate' : 'numeric',
			'entity' : 'numeric',
			'coffee' : 'numeric',
			'entity' : 'numeric',
			'grainy' : 'numeric',
			'entity' : 'numeric',
			'malty' : 'numeric',
			'entity' : 'numeric',
			'head' : 'numeric',
			'entity' : 'numeric',
			'nutty' : 'numeric',
			'entity' : 'numeric',
			'roasted' : 'numeric',
			'entity' : 'numeric',
			'smoked' : 'numeric',
			'entity' : 'numeric',
			'sweet' : 'numeric',
			'entity' : 'numeric',
			'toasted' : 'numeric',
			'entity' : 'numeric',
			'ppg' : 'numeric',
			'entity' : 'numeric',
			'hwe' : 'numeric',
			'entity' : 'numeric',
			'extract' : 'numeric',
			'entity' : 'numeric',
			'mustMash' : 'numeric',
			'entity' : 'numeric',
			'isAdjunct' : 'numeric',
			'entity' : 'numeric',
			'hopAlpha' : 'numeric',
			'entity' : 'numeric',
			'hopForm' : 'char',
			'entity' : 'numeric',
			'hopUse' : 'char',
			'entity' : 'numeric',
			'hopAddAt' : 'numeric',
			'entity' : 'numeric',
			'attenuation' : 'numeric',
			'entity' : 'numeric',
			'dosage' : 'numeric',
			'entity' : 'numeric',
			'wastageFixed' : 'numeric',
			'entity' : 'numeric',
			'styles' : 'char',
			'entity' : 'numeric',
			'description' : 'char',
			'entity' : 'numeric',
			'caprequired' : 'numeric',
			'entity' : 'numeric',
			'co2required' : 'numeric',
			'entity' : 'numeric',
			'isGrain' : 'numeric',
			'entity' : 'numeric',
			'fullvolume' : 'numeric',
			'entity' : 'numeric',
			'volume' : 'numeric',
		}
		self.tableName="gItems"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		if self.aromatic:
			aromatic=1
		else:
			aromatic=0
		if self.biscuit:
			biscuit=1
		else:
			biscuit=0
		if self.body:
			body=1
		else:
			body=0
		if self.burnt:
			burnt=1
		else:
			burnt=0
		if self.caramel:
			caramel=1
		else:
			caramel=0
		if self.chocolate:
			chocolate=1
		else:
			chocolate=0
		if self.coffee:
			coffee=1
		else:
			coffee=0
		if self.grainy:
			grainy=1
		else:
			grainy=0
		if self.malty:
			malty=1
		else:
			malty=0
		if self.head:
			head=1
		else:
			head=0
		if self.nutty:
			nutty=1
		else:
			nutty=0
		if self.roasted:
			roasted=1
		else:
			roasted=0
		if self.smoked:
			smoked=1
		else:
			smoked=0
		if self.sweet:
			sweet=1
		else:	
			sweet=0
		if self.toasted:
			toasted=1
		else:
			toasted=0
		if self.mustMash:
			mustMash=1
		else:
			mustMash=0
		if self.isAdjunct:
			isAdjunct=1
		else:
			isAdjunct=0
		if self.caprequired:
			caprequired=1
		else:
			caprequired=0
		if self.co2required:
			co2required=1
		else:	
			co2required=0
		if self.isGrain:
			isGrain=1
		else:
			isGrain=0

		return "INSERT INTO gItems VALUES (null, '%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', %s, %s, %s, %s, '%s', '%s', %s, %s, %s, %s, %s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.majorcategory) , _mysql.escape_string(self.category) , _mysql.escape_string(self.subcategory) , _mysql.escape_string(self.name) , _mysql.escape_string(self.idx) , self.qtyMultiple , _mysql.escape_string(self.unit) , self.colour , aromatic , biscuit , body , burnt ,caramel , chocolate , coffee , grainy , malty , head ,nutty , roasted , smoked , sweet , toasted , self.ppg , self.hwe , self.extract , mustMash , isAdjunct , self.hopAlpha , _mysql.escape_string(self.hopForm) , _mysql.escape_string(self.hopUse) , self.hopAddAt , self.attenuation , self.dosage , self.wastageFixed , _mysql.escape_string(self.styles) , _mysql.escape_string(self.description) ,caprequired , co2required , isGrain , self.fullvolume , self.volume )

	def updateSql(self):
		if self.aromatic:
			aromatic=1
		else:
			aromatic=0
		if self.biscuit:
			biscuit=1
		else:
			biscuit=0
		if self.body:
			body=1
		else:
			body=0
		if self.burnt:
			burnt=1
		else:
			burnt=0
		if self.caramel:
			caramel=1
		else:
			caramel=0
		if self.chocolate:
			chocolate=1
		else:
			chocolate=0
		if self.coffee:
			coffee=1
		else:
			coffee=0
		if self.grainy:
			grainy=1
		else:
			grainy=0
		if self.malty:
			malty=1
		else:
			malty=0
		if self.head:
			head=1
		else:
			head=0
		if self.nutty:
			nutty=1
		else:
			nutty=0
		if self.roasted:
			roasted=1
		else:
			roasted=0
		if self.smoked:
			smoked=1
		else:
			smoked=0
		if self.sweet:
			sweet=1
		else:	
			sweet=0
		if self.toasted:
			toasted=1
		else:
			toasted=0
		if self.mustMash:
			mustMash=1
		else:
			mustMash=0
		if self.isAdjunct:
			isAdjunct=1
		else:
			isAdjunct=0
		if self.caprequired:
			caprequired=1
		else:
			caprequired=0
		if self.co2required:
			co2required=1
		else:	
			co2required=0
		if self.isGrain:
			isGrain=1
		else:
			isGrain=0
		return "UPDATE gItems SET  owner = '%s', majorcategory = '%s', category = '%s', subcategory = '%s', name = '%s', idx = '%s', qtyMultiple = %s, unit = '%s', colour = %s, aromatic = %s, biscuit = %s, body = %s, burnt = %s, caramel = %s, chocolate = %s, coffee = %s, grainy = %s, malty = %s, head = %s, nutty = %s, roasted = %s, smoked = %s, sweet = %s, toasted = %s, ppg = %s, hwe = %s, extract = %s, mustMash = %s, isAdjunct = %s, hopAlpha = %s, hopForm = '%s', hopUse = '%s', hopAddAt = %s, attenuation = %s, dosage = %s, wastageFixed = %s, styles = '%s', description = '%s', caprequired = %s, co2required = %s, isGrain = %s, fullvolume = %s, volume = %s WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.majorcategory), _mysql.escape_string(self.category), _mysql.escape_string(self.subcategory), _mysql.escape_string(self.name), _mysql.escape_string(self.idx), self.qtyMultiple, _mysql.escape_string(self.unit), self.colour, aromatic, biscuit, body, burnt, caramel, chocolate, coffee, grainy, malty, head, nutty, roasted, smoked, sweet, toasted, self.ppg, self.hwe, self.extract, mustMash, isAdjunct, self.hopAlpha, _mysql.escape_string(self.hopForm), _mysql.escape_string(self.hopUse), self.hopAddAt, self.attenuation, self.dosage, self.wastageFixed, _mysql.escape_string(self.styles), _mysql.escape_string(self.description), caprequired, co2required, isGrain, self.fullvolume, self.volume, self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.majorcategory, self.category, self.subcategory, self.name, self.idx, qtyMultiple, self.unit, colour, aromatic, biscuit, body,burnt, caramel, chocolate, coffee, grainy, malty, head, nutty, roasted, smoked, sweet, toasted, ppg, hwe, extract, mustMash, isAdjunct, hopAlpha, self.hopForm, self.hopUse, hopAddAt, attenuation, dosage, wastageFixed, self.styles, self.description, caprequired, co2required, isGrain, fullvolume, volume),)=row


		self.qtyMultiple=float(qtyMultiple)
		self.colour=float(colour)
		self.ppg=float(ppg)
		self.hwe=float(hwe)
		self.extract=float(extract)	
		self.hopAlpha=float(hopAlpha)
		self.hopAddAt=float(hopAddAt)
		self.attenuation=float(attenuation)
		self.dosage=float(dosage)
		self.wastageFixed=float(wastageFixed)
		self.fullvolume=float(fullvolume)
		self.volume=float(volume)


		if int(aromatic) == 1:
			self.aromatic=True
		else:
			self.aromatic=False
		if int(biscuit) == 1:
			self.biscuit=True
		else:
			self.biscuit=False
		if int(body) == 1:
			self.body=True
		else:
			self.body=False
		if int(burnt) == 1:
			self.burnt=True
		else:
			self.burnt=False
		if int(caramel) == 1:
			self.caramel=True
		else:
			self.caramel=False
		if int(chocolate) == 1:
			self.chocolate=True
		else:
			self.chocolate=False
		if int(coffee) == 1:
			self.coffee=True
		else:
			self.coffee=False
		if int(grainy) == 1:
			self.grainy=True
		else:
			self.grainy=False
		if int(malty) == 1:
			self.malty=True
		else:
			self.malty=False
		if int(head) == 1:
			self.head=True
		else:
			self.head=False
		if int(nutty) == 1:
			self.nutty=True
		else:
			self.nutty=False
		if int(roasted) == 1:
			self.roasted=True
		else:
			self.roasted=False
		if int(smoked) == 1:
			self.smoked=True
		else:
			self.smoked=False
		if int(sweet) == 1:
			self.sweet=True
		else:	
			self.sweet=False
		if int(toasted) == 1:
			self.toasted=True
		else:
			self.toasted=False
		if int(mustMash) == 1:
			self.mustMash=True
		else:
			self.mustMash=False
		if int(isAdjunct) == 1:
			self.isAdjunct=True
		else:
			self.isAdjunct=False
		if int(caprequired) == 1:
			self.caprequired=True
		else:
			self.caprequired=False
		if int(co2required) == 1:
			self.co2required=True
		else:	
			self.co2required=False
		if int(isGrain)  == 1:
			self.isGrain=True
		else:
			self.isGrain=False


class gIngredients(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.recipename=""
		self.atten=0.00
		self.qty=0.00
		self.originalqty=0.00
		self.ingredient=""
		self.ingredientType=""
		self.isAdjunct=0
		self.isPrimingFalvouring=0
		self.mustMash=0
		self.isGrain=0
		self.hwe=0.00
		self.extract=0.00
		self.unit=""
		self.hopAlpha=0.00
		self.hopForm=""
		self.hopUse=""
		self.hopAddAt=0.00
		self.colour=0.00
		self.processIngredient=0
		self.processConsumable=0
		self.process=""
		self.category=""
		self.types = {
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'recipename' : 'char',
			'entity' : 'numeric',
			'atten' : 'numeric',
			'entity' : 'numeric',
			'qty' : 'numeric',
			'entity' : 'numeric',
			'originalqty' : 'numeric',
			'entity' : 'numeric',
			'ingredient' : 'char',
			'entity' : 'numeric',
			'ingredientType' : 'char',
			'entity' : 'numeric',
			'isAdjunct' : 'numeric',
			'entity' : 'numeric',
			'isPrimingFalvouring' : 'numeric',
			'entity' : 'numeric',
			'mustMash' : 'numeric',
			'entity' : 'numeric',
			'isGrain' : 'numeric',
			'entity' : 'numeric',
			'hwe' : 'numeric',
			'entity' : 'numeric',
			'extract' : 'numeric',
			'entity' : 'numeric',
			'unit' : 'char',
			'entity' : 'numeric',
			'hopAlpha' : 'numeric',
			'entity' : 'numeric',
			'hopForm' : 'char',
			'entity' : 'numeric',
			'hopUse' : 'char',
			'entity' : 'numeric',
			'hopAddAt' : 'numeric',
			'entity' : 'numeric',
			'colour' : 'numeric',
			'entity' : 'numeric',
			'processIngredient' : 'numeric',
			'entity' : 'numeric',
			'processConsumable' : 'numeric',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'category' : 'char',
		}
		self.tableName="gIngredients"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):

		if self.isAdjunct:
			isAdjunct=1
		else:
			isAdjunct=0
		
		if self.isPrimingFalvouring:
			isPrimingFalvouring=1
		else:
			isPrimingFalvouring=0
		if self.mustMash:
			mustMash=1
		else:
			mustMash=0
		if self.isGrain:
			isGrain=1
		else:
			isGrain=0
		if self.processIngredient:	
			processIngredient=1
		else:
			processIngredient=0
		if self.processConsumable:
			processConsumable=1
		else:
			processConsumable=0

		return "INSERT INTO gIngredients VALUES (null, '%s', '%s', %s, %s, %s, '%s', '%s', %s, %s, %s, %s, %s, %s, '%s', %s, '%s', '%s', %s, %s, %s, %s, '%s', '%s');" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.recipename) , self.atten , self.qty , self.originalqty , _mysql.escape_string(self.ingredient) , _mysql.escape_string(self.ingredientType) , isAdjunct ,isPrimingFalvouring , mustMash , isGrain , self.hwe , self.extract , _mysql.escape_string(self.unit) , self.hopAlpha , _mysql.escape_string(self.hopForm) , _mysql.escape_string(self.hopUse) , self.hopAddAt , self.colour , processIngredient , processConsumable , _mysql.escape_string(self.process) , _mysql.escape_string(self.category) )

	def updateSql(self):

		if self.isAdjunct:
			isAdjunct=1
		else:
			isAdjunct=0
		
		if self.isPrimingFalvouring:
			isPrimingFalvouring=1
		else:
			isPrimingFalvouring=0
		if self.mustMash:
			mustMash=1
		else:
			mustMash=0
		if self.isGrain:
			isGrain=1
		else:
			isGrain=0
		if self.processIngredient:	
			processIngredient=1
		else:
			processIngredient=0
		if self.processConsumable:
			processConsumable=1
		else:
			processConsumable=0
		return "UPDATE gIngredients SET  owner = '%s', recipename = '%s', atten = %s, qty = %s, originalqty = %s, ingredient = '%s', ingredientType = '%s', isAdjunct = %s, isPrimingFalvouring = %s, mustMash = %s, isGrain = %s, hwe = %s, extract = %s, unit = '%s', hopAlpha = %s, hopForm = '%s', hopUse = '%s', hopAddAt = %s, colour = %s, processIngredient = %s, processConsumable = %s, process = '%s', category = '%s' WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.recipename), self.atten, self.qty, self.originalqty, _mysql.escape_string(self.ingredient), _mysql.escape_string(self.ingredientType), isAdjunct, isPrimingFalvouring, mustMash, isGrain, self.hwe, self.extract, _mysql.escape_string(self.unit), self.hopAlpha, _mysql.escape_string(self.hopForm), _mysql.escape_string(self.hopUse), self.hopAddAt, self.colour, processIngredient, processConsumable, _mysql.escape_string(self.process), _mysql.escape_string(self.category), self.entity)


	def populate(self,row):
#		if self.dbg > 0:
#			sys.stderr.write( "%s" %(row))
#			sys.stderr.write("\n")
		(( self.entity , self.owner, self.recipename, atten, qty, originalqty, self.ingredient, self.ingredientType, isAdjunct, isPrimingFalvouring, mustMash, isGrain, hwe, extract, self.unit, hopAlpha, self.hopForm, self.hopUse, hopAddAt, colour, processIngredient, processConsumable, self.process, self.category),)=row

#
#INSERT INTO gIngredients VALUES (null ,'test@example.com' ,'Pure Gold Goose' ,0.0 ,4781.0 ,4781.0 ,'Maris Otter' ,'fermentables' ,
#
##isAdjunct0 ,0 ,1 ,
#isGrain1 ,315.648 ,82.2 ,'gm' ,0.0 ,'' ,'' ,0.0 ,5.91 ,0 ,0 ,'' ,'' );

		self.atten=float(atten)
		self.qty=float(qty)
		self.originalqty=float(originalqty)
		self.hwe=float(hwe)
		self.extract=float(extract)
		self.hopAlpha=float(hopAlpha)
		self.hopAddAt=float(hopAddAt)
		self.colour=float(colour)

		if int(isAdjunct) == 1:
			self.isAdjunct=True
		else:
			self.isAdjunct=False
		
		if int(isPrimingFalvouring) == 1:
			self.isPrimingFalvouring=True
		else:
			self.isPrimingFalvouring=False
		if int(mustMash) == 1:
			self.mustMash=True
		else:
			self.mustMash=False
		if int(isGrain) == 1:
			self.isGrain=True
		else:
			self.isGrain=False		
		if int(processIngredient) == 1:	
			self.processIngredient=True
		else:
			self.processIngredient=False
		if int(processConsumable) == 1:
			self.processConsumable=True
		else:
			self.processConsumable=False



class gRecipes(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.recipename=""
		self.owner=""
		self.stylenumber=""
		self.styleletter=""
		self.styleversion=""
		self.batch_size_required=0
		self.credit=""
		self.description=""
		self.mash_efficiency=0.00
		self.estimated_abv=0.00
		self.estimated_ebc=0.00
		self.estimated_fg=0.00
		self.estimated_ibu=0.00
		self.estimated_og=0.00
		self.estimated_srm=0.00
		self.forcedstyle=""
		self.process=""
		self.recipe_type=""
		self.postBoilTopup=0.00
		self.spargeWater=0.00
		self.mashWater=0.00
		self.boilVolume=0.00
		self.totalWater=0.00
		self.totalGrain=0.00
		self.totalAdjuncts=0.00
		self.totalHops=0.00
		self.mash_grain_ratio=0.00
		self.target_mash_temp=0.00
		self.initial_grain_temp=0.00
		self.target_mash_temp_tweak=0.00
		self.priming_sugar_qty=0.00
		self.tap_mash_water=0
		self.tap_sparge_water=0
		self.alkalinity=0
		self.fermTemp=0
		self.fermLowTemp=0
		self.fermHighTemp=0
		self.calculationOutstanding=0
		self.types = {
			'entity' : 'numeric',
			'recipename' : 'char',
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'stylenumber' : 'char',
			'entity' : 'numeric',
			'styleletter' : 'char',
			'entity' : 'numeric',
			'styleversion' : 'char',
			'entity' : 'numeric',
			'batch_size_required' : 'numeric',
			'entity' : 'numeric',
			'credit' : 'char',
			'entity' : 'numeric',
			'description' : 'char',
			'entity' : 'numeric',
			'mash_efficiency' : 'numeric',
			'entity' : 'numeric',
			'estimated_abv' : 'numeric',
			'entity' : 'numeric',
			'estimated_ebc' : 'numeric',
			'entity' : 'numeric',
			'estimated_fg' : 'numeric',
			'entity' : 'numeric',
			'estimated_ibu' : 'numeric',
			'entity' : 'numeric',
			'estimated_og' : 'numeric',
			'entity' : 'numeric',
			'estimated_srm' : 'numeric',
			'entity' : 'numeric',
			'forcedstyle' : 'char',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'recipe_type' : 'char',
			'entity' : 'numeric',
			'postBoilTopup' : 'numeric',
			'entity' : 'numeric',
			'spargeWater' : 'numeric',
			'entity' : 'numeric',
			'mashWater' : 'numeric',
			'entity' : 'numeric',
			'boilVolume' : 'numeric',
			'entity' : 'numeric',
			'totalWater' : 'numeric',
			'entity' : 'numeric',
			'totalGrain' : 'numeric',
			'entity' : 'numeric',
			'totalAdjuncts' : 'numeric',
			'entity' : 'numeric',
			'totalHops' : 'numeric',
			'entity' : 'numeric',
			'mash_grain_ratio' : 'numeric',
			'entity' : 'numeric',
			'target_mash_temp' : 'numeric',
			'entity' : 'numeric',
			'initial_grain_temp' : 'numeric',
			'entity' : 'numeric',
			'target_mash_temp_tweak' : 'numeric',
			'entity' : 'numeric',
			'priming_sugar_qty' : 'numeric',
			'entity' : 'numeric',
			'tap_mash_water' : 'numeric',
			'entity' : 'numeric',
			'tap_sparge_water' : 'numeric',
			'entity' : 'numeric',
			'alkalinity':'numeric',
			'fermTemp':'numeric',
			'fermLowTemp':'numeric',
			'fermHighTemp':'numeric',
			'calculationOutstanding' : 'numeric',
		}
		self.tableName="gRecipes"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		if self.tap_mash_water:
			tap_mash_water=1
		else:
			tap_mash_water=0
		if self.tap_sparge_water:
			tap_sparge_water=1
		else:
			tap_sparge_water=0
		if self.calculationOutstanding:
			calculationOutstanding=1
		else:
			calculationOutstanding=0
		return "INSERT INTO gRecipes VALUES (null, '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s);" %( _mysql.escape_string(self.recipename) , _mysql.escape_string(self.owner) , _mysql.escape_string(self.stylenumber) , _mysql.escape_string(self.styleletter) , _mysql.escape_string(self.styleversion) , self.batch_size_required , _mysql.escape_string(self.credit) , _mysql.escape_string(self.description) , self.mash_efficiency , self.estimated_abv , self.estimated_ebc , self.estimated_fg , self.estimated_ibu , self.estimated_og , self.estimated_srm , _mysql.escape_string(self.forcedstyle) , _mysql.escape_string(self.process) , _mysql.escape_string(self.recipe_type) , self.postBoilTopup , self.spargeWater , self.mashWater , self.boilVolume , self.totalWater , self.totalGrain , self.totalAdjuncts , self.totalHops , self.mash_grain_ratio , self.target_mash_temp , self.initial_grain_temp , self.target_mash_temp_tweak , self.priming_sugar_qty , tap_mash_water , tap_sparge_water ,calculationOutstanding,self.alkalinity,float(self.fermTemp),float(self.fermLowTemp),float(self.fermHighTemp))

	def updateSql(self):
		if self.tap_mash_water:
			tap_mash_water=1
		else:
			tap_mash_water=0
		if self.tap_sparge_water:
			tap_sparge_water=1
		else:
			tap_sparge_water=0
		if self.calculationOutstanding:
			calculationOutstanding=1
		else:
			calculationOutstanding=0
		return "UPDATE gRecipes SET  recipename = '%s', owner = '%s', stylenumber = '%s', styleletter = '%s', styleversion = '%s', batch_size_required = %s, credit = '%s', description = '%s', mash_efficiency = %s, estimated_abv = %s, estimated_ebc = %s, estimated_fg = %s, estimated_ibu = %s, estimated_og = %s, estimated_srm = %s, forcedstyle = '%s', process = '%s', recipe_type = '%s', postBoilTopup = %s, spargeWater = %s, mashWater = %s, boilVolume = %s, totalWater = %s, totalGrain = %s, totalAdjuncts = %s, totalHops = %s, mash_grain_ratio = %s, target_mash_temp = %s, initial_grain_temp = %s, target_mash_temp_tweak = %s, priming_sugar_qty = %s, tap_mash_water = %s, tap_sparge_water = %s, calculationOutstanding = %s, alkalinity = %s, fermTemp = %s,fermLowTemp=%s, fermHighTemp =%s WHERE entity = %s " %( _mysql.escape_string(self.recipename), _mysql.escape_string(self.owner), _mysql.escape_string(self.stylenumber), _mysql.escape_string(self.styleletter), _mysql.escape_string(self.styleversion), self.batch_size_required, _mysql.escape_string(self.credit), _mysql.escape_string(self.description), self.mash_efficiency, self.estimated_abv, self.estimated_ebc, self.estimated_fg, self.estimated_ibu, self.estimated_og, self.estimated_srm, _mysql.escape_string(self.forcedstyle), _mysql.escape_string(self.process), _mysql.escape_string(self.recipe_type), self.postBoilTopup, self.spargeWater, self.mashWater, self.boilVolume, self.totalWater, self.totalGrain, self.totalAdjuncts, self.totalHops, self.mash_grain_ratio, self.target_mash_temp, self.initial_grain_temp, self.target_mash_temp_tweak, self.priming_sugar_qty, tap_mash_water, tap_sparge_water, calculationOutstanding, self.alkalinity, float(self.fermTemp),float(self.fermLowTemp),float(self.fermHighTemp),self.entity)


	def populate(self,row):
		(( self.entity , self.recipename, self.owner, self.stylenumber, self.styleletter, self.styleversion, batch_size_required, self.credit, self.description, mash_efficiency,estimated_abv, estimated_ebc, estimated_fg, estimated_ibu, estimated_og, estimated_srm, self.forcedstyle, self.process, self.recipe_type, postBoilTopup, spargeWater, mashWater, boilVolume, totalWater, totalGrain, totalAdjuncts, totalHops, mash_grain_ratio, target_mash_temp, initial_grain_temp, target_mash_temp_tweak, priming_sugar_qty, tap_mash_water, tap_sparge_water, calculationOutstanding,self.alkalinity,fermTemp,fermLowTemp,fermHighTemp),)=row

		self.mash_efficiency=float(mash_efficiency)
		self.estimated_abv=float(estimated_abv)
		self.estimated_ebc=float(estimated_ebc)
		self.estimated_fg=float(estimated_fg)
		self.estimated_ibu=float(estimated_ibu)
		self.estimated_og=float(estimated_og)
		self.estiamted_srm=float(estimated_srm)
		self.postBoilTopup=float(postBoilTopup)
		self.spargeWater=float(spargeWater)
		self.mashWater=float(mashWater)
		self.boilVolume=float(boilVolume)
		self.totalWater=float(totalWater)
		self.totalGrain=float(totalGrain)
		self.totalAdjuncts=float(totalAdjuncts)
		self.totalHops=float(totalHops)
		self.mash_grain_ratio=float(mash_grain_ratio)
		self.target_mash_temp=float(target_mash_temp)
		self.initial_grain_temp=float(initial_grain_temp)
		self.target_mash_temp_tweak=float(target_mash_temp_tweak)
		self.priming_sugar_qty=float(priming_sugar_qty)
		self.batch_size_required=float(batch_size_required)


		if int(tap_mash_water) == 1:
			self.tap_mash_water=True
		else:
			self.tap_mash_water=False
		if int(tap_sparge_water) == 1:
			self.tap_sparge_water=True
		else:
			self.tap_sparge_water=False
		if int(calculationOutstanding) == 1:
			self.calculationOutstanding=True
		else:
			self.calculationOutstanding=False
		self.fermTemp=float(fermTemp)
		self.fermLowTemp=float(fermLowTemp)
		self.fermHighTemp=float(fermHighTemp)


	
class gRecipeStats(db):


	def __init__(self,**kwargs):
		self.dbg=0
		self.entity=None
		self.con=None
		self.owner=""
		self.recipe=""
		self.process=""
		self.postboil_precool_og=0.00
		self.pretopup_estimated_gravity_grain=0.00
		self.sparge_temp=0.00
		self.pretopup_post_mash_og=0.00
		self.strike_temp=0.00
		self.primingwater=0.00
		self.sparge_water=0.00
		self.target_mash_temp=0.00
		self.precoolfvvolume=0.00
		self.pre_boil_gravity=0.00
		self.primingsugarqty=0.00
		self.num_crown_caps=0.00
		self.estimated_og=0.00
		self.estimated_ibu=0.00
		self.primingsugartotal=0.00
		self.strike_temp_5=0.00
		self.mash_liquid=0.00
		self.sparge_heating_time=0.00
		self.boil_vol=0.00
		self.mash_liquid_6=0.00
		self.topupvol=0.00
		self.extendedboil=0
		self.estimated_fg=0.00
		self.estimated_abv=0.00
		self.total_water=0.00
		self.grain_weight=0.00
		self.nongrain_weight=0.00
		self.hops_weight=0.00
		self.bottles_required=0.00
		self.kettle1volume=0.00
		self.kettle2volume=0.00
		self.kettle3volume=0.00
		self.kettle1kettle2volume=0.00
		self.kettle1kettle2kettle3volume=0.00
		self.kettle1evaporation=0.00
		self.kettle2evaporation=0.00
		self.kettle3evaporation=0.00
		self.kettle1preboilgravity=0.00
		self.kettle2preboilgravity=0.00
		self.kettle3preboilgravity=0.00
		self.postboilprecoolgravity=0.00
		self.preboil_gravity=0.00
		self.minikegqty=0.00
		self.polypinqty=0.00
		self.batchsize=0.00
		self.brewlog=""
		self.dryhop=0
		self.types = {
			'batchsize' : 'numeric',
			'entity' : 'numeric',
			'owner' : 'char',
			'entity' : 'numeric',
			'recipe' : 'char',
			'entity' : 'numeric',
			'process' : 'char',
			'entity' : 'numeric',
			'postboil_precool_og' : 'numeric',
			'entity' : 'numeric',
			'pretopup_estimated_gravity_grain' : 'numeric',
			'entity' : 'numeric',
			'sparge_temp' : 'numeric',
			'entity' : 'numeric',
			'pretopup_post_mash_og' : 'numeric',
			'entity' : 'numeric',
			'strike_temp' : 'numeric',
			'entity' : 'numeric',
			'primingwater' : 'numeric',
			'entity' : 'numeric',
			'sparge_water' : 'numeric',
			'entity' : 'numeric',
			'target_mash_temp' : 'numeric',
			'entity' : 'numeric',
			'precoolfvvolume' : 'numeric',
			'entity' : 'numeric',
			'pre_boil_gravity' : 'numeric',
			'entity' : 'numeric',
			'primingsugarqty' : 'numeric',
			'entity' : 'numeric',
			'num_crown_caps' : 'numeric',
			'entity' : 'numeric',
			'estimated_og' : 'numeric',
			'entity' : 'numeric',
			'estimated_ibu' : 'numeric',
			'entity' : 'numeric',
			'primingsugartotal' : 'numeric',
			'entity' : 'numeric',
			'strike_temp_5' : 'numeric',
			'entity' : 'numeric',
			'mash_liquid' : 'numeric',
			'entity' : 'numeric',
			'sparge_heating_time' : 'numeric',
			'entity' : 'numeric',
			'boil_vol' : 'numeric',
			'entity' : 'numeric',
			'mash_liquid_6' : 'numeric',
			'entity' : 'numeric',
			'topupvol' : 'numeric',
			'entity' : 'numeric',
			'extendedboil' : 'numeric',
			'entity' : 'numeric',
			'estimated_fg' : 'numeric',
			'entity' : 'numeric',
			'estimated_abv' : 'numeric',
			'entity' : 'numeric',
			'total_water' : 'numeric',
			'entity' : 'numeric',
			'grain_weight' : 'numeric',
			'entity' : 'numeric',
			'nongrain_weight' : 'numeric',
			'entity' : 'numeric',
			'hops_weight' : 'numeric',
			'entity' : 'numeric',
			'bottles_required' : 'numeric',
			'entity' : 'numeric',
			'kettle1volume' : 'numeric',
			'entity' : 'numeric',
			'kettle2volume' : 'numeric',
			'entity' : 'numeric',
			'kettle3volume' : 'numeric',
			'entity' : 'numeric',
			'kettle1kettle2volume' : 'numeric',
			'entity' : 'numeric',
			'kettle1kettle2kettle3volume' : 'numeric',
			'entity' : 'numeric',
			'kettle1evaporation' : 'numeric',
			'entity' : 'numeric',
			'kettle2evaporation' : 'numeric',
			'entity' : 'numeric',
			'kettle3evaporation' : 'numeric',
			'entity' : 'numeric',
			'kettle1preboilgravity' : 'numeric',
			'entity' : 'numeric',
			'kettle2preboilgravity' : 'numeric',
			'entity' : 'numeric',
			'kettle3preboilgravity' : 'numeric',
			'entity' : 'numeric',
			'postboilprecoolgravity' : 'numeric',
			'entity' : 'numeric',
			'preboil_gravity' : 'numeric',
			'entity' : 'numeric',
			'minikegqty' : 'numeric',
			'entity' : 'numeric',
			'polypinqty' : 'numeric',
			'brewlog' : 'char',
			'dryhop':'numeric',
		}
		self.tableName="gRecipeStats"
		for key, value in kwargs.iteritems():
			self.__dict__[key]=value

	def insertSql(self):
		"""
		sys.stderr.write(" %s \n" %( _mysql.escape_string(self.recipe) ))
		sys.stderr.write(" %s \n" %( _mysql.escape_string(self.process) ))
		sys.stderr.write(" %s \n" %( self.postboil_precool_og ))
		sys.stderr.write(" %s \n" %( self.pretopup_estimated_gravity_grain ))
		sys.stderr.write(" %s \n" %( self.sparge_temp ))
		sys.stderr.write(" %s \n" %( self.pretopup_post_mash_og ))
		sys.stderr.write(" %s \n" %( self.strike_temp ))
		sys.stderr.write(" %s \n" %( self.primingwater ))
		sys.stderr.write(" %s \n" %( self.sparge_water ))
		sys.stderr.write(" %s \n" %( self.target_mash_temp ))
		sys.stderr.write(" %s \n" %( self.precoolfvvolume ))
		sys.stderr.write(" %s \n" %( self.pre_boil_gravity ))
		sys.stderr.write(" %s \n" %( self.primingsugarqty ))
		sys.stderr.write(" %s \n" %( self.num_crown_caps ))
		sys.stderr.write(" %s \n" %( self.estimated_og ))
		sys.stderr.write(" %s \n" %( self.estimated_ibu ))
		sys.stderr.write(" %s \n" %( self.primingsugartotal ))
		sys.stderr.write(" %s \n" %( self.strike_temp_5 ))
		sys.stderr.write(" %s \n" %( self.mash_liquid ))
		sys.stderr.write(" %s \n" %( self.sparge_heating_time ))
		sys.stderr.write(" %s \n" %( self.boil_vol ))
		sys.stderr.write(" %s \n" %( self.mash_liquid_6 ))
		sys.stderr.write(" %s \n" %( self.topupvol ))
		sys.stderr.write(" %s \n" %( self.extendedboil ))
		sys.stderr.write(" %s \n" %( self.estimated_fg ))
		sys.stderr.write(" %s \n" %( self.estimated_abv ))
		sys.stderr.write(" %s \n" %( self.total_water ))
		sys.stderr.write(" %s \n" %( self.grain_weight ))
		sys.stderr.write(" %s \n" %( self.nongrain_weight ))
		sys.stderr.write(" %s \n" %( self.hops_weight ))
		sys.stderr.write(" %s \n" %( self.bottles_required ))
		sys.stderr.write(" %s \n" %( self.kettle1volume ))
		sys.stderr.write(" %s \n" %( self.kettle2volume ))
		sys.stderr.write(" %s \n" %( self.kettle3volume ))
		sys.stderr.write(" %s \n" %( self.kettle1kettle2volume ))
		sys.stderr.write(" %s \n" %( self.kettle1kettle2kettle3volume ))
		sys.stderr.write(" %s \n" %( self.kettle1evaporation ))
		sys.stderr.write(" %s \n" %( self.kettle2evaporation ))
		sys.stderr.write(" %s \n" %( self.kettle3evaporation ))
		sys.stderr.write(" %s \n" %( self.kettle1preboilgravity ))
		sys.stderr.write(" %s \n" %( self.kettle2preboilgravity ))
		sys.stderr.write(" %s \n" %( self.kettle3preboilgravity ))
		sys.stderr.write(" %s \n" %( self.postboilprecoolgravity ))
		sys.stderr.write(" %s \n" %( self.preboil_gravity ))
		sys.stderr.write(" %s \n" %( self.minikegqty ))
		sys.stderr.write(" %s \n" %( self.polypinqty))
		sys.stderr.write(" %s \n" %(self.batchsize ))
		sys.stderr.write("(BREWLOG\n")
		sys.stderr.write(" %s \n" %( _mysql.escape_string(self.brewlog)))
		sys.stderr.write(" %s \n" %(self.dryhop))
		"""
		return "INSERT INTO gRecipeStats VALUES (null, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,'%s',%s);" %( _mysql.escape_string(self.owner) , _mysql.escape_string(self.recipe) , _mysql.escape_string(self.process) , self.postboil_precool_og , self.pretopup_estimated_gravity_grain , self.sparge_temp , self.pretopup_post_mash_og , self.strike_temp , self.primingwater , self.sparge_water , self.target_mash_temp , self.precoolfvvolume , self.pre_boil_gravity , self.primingsugarqty , self.num_crown_caps , self.estimated_og , self.estimated_ibu , self.primingsugartotal , self.strike_temp_5 , self.mash_liquid , self.sparge_heating_time , self.boil_vol , self.mash_liquid_6 , self.topupvol , self.extendedboil , self.estimated_fg , self.estimated_abv , self.total_water , self.grain_weight , self.nongrain_weight , self.hops_weight , self.bottles_required , self.kettle1volume , self.kettle2volume , self.kettle3volume , self.kettle1kettle2volume , self.kettle1kettle2kettle3volume , self.kettle1evaporation , self.kettle2evaporation , self.kettle3evaporation , self.kettle1preboilgravity , self.kettle2preboilgravity , self.kettle3preboilgravity , self.postboilprecoolgravity , self.preboil_gravity , self.minikegqty , self.polypinqty,self.batchsize , _mysql.escape_string(self.brewlog),self.dryhop)

	def updateSql(self):
		return "UPDATE gRecipeStats SET  owner = '%s', recipe = '%s', process = '%s', postboil_precool_og = %s, pretopup_estimated_gravity_grain = %s, sparge_temp = %s, pretopup_post_mash_og = %s, strike_temp = %s, primingwater = %s, sparge_water = %s, target_mash_temp = %s, precoolfvvolume = %s, pre_boil_gravity = %s, primingsugarqty = %s, num_crown_caps = %s, estimated_og = %s, estimated_ibu = %s, primingsugartotal = %s, strike_temp_5 = %s, mash_liquid = %s, sparge_heating_time = %s, boil_vol = %s, mash_liquid_6 = %s, topupvol = %s, extendedboil = %s, estimated_fg = %s, estimated_abv = %s, total_water = %s, grain_weight = %s, nongrain_weight = %s, hops_weight = %s, bottles_required = %s, kettle1volume = %s, kettle2volume = %s, kettle3volume = %s, kettle1kettle2volume = %s, kettle1kettle2kettle3volume = %s, kettle1evaporation = %s, kettle2evaporation = %s, kettle3evaporation = %s, kettle1preboilgravity = %s, kettle2preboilgravity = %s, kettle3preboilgravity = %s, postboilprecoolgravity = %s, preboil_gravity = %s, minikegqty = %s, polypinqty = %s, batchsize=%s, brewlog = '%s'  WHERE entity = %s " %( _mysql.escape_string(self.owner), _mysql.escape_string(self.recipe), _mysql.escape_string(self.process), self.postboil_precool_og, self.pretopup_estimated_gravity_grain, self.sparge_temp, self.pretopup_post_mash_og, self.strike_temp, self.primingwater, self.sparge_water, self.target_mash_temp, self.precoolfvvolume, self.pre_boil_gravity, self.primingsugarqty, self.num_crown_caps, self.estimated_og, self.estimated_ibu, self.primingsugartotal, self.strike_temp_5, self.mash_liquid, self.sparge_heating_time, self.boil_vol, self.mash_liquid_6, self.topupvol, self.extendedboil, self.estimated_fg, self.estimated_abv, self.total_water, self.grain_weight, self.nongrain_weight, self.hops_weight, self.bottles_required, self.kettle1volume, self.kettle2volume, self.kettle3volume, self.kettle1kettle2volume, self.kettle1kettle2kettle3volume, self.kettle1evaporation, self.kettle2evaporation, self.kettle3evaporation, self.kettle1preboilgravity, self.kettle2preboilgravity, self.kettle3preboilgravity, self.postboilprecoolgravity, self.preboil_gravity, self.minikegqty, self.polypinqty, self.batchsize,_mysql.escape_string(self.brewlog),self.entity)


	def populate(self,row):
		(( self.entity , self.owner, self.recipe, self.process, postboil_precool_og, pretopup_estimated_gravity_grain, sparge_temp, pretopup_post_mash_og, strike_temp, primingwater, sparge_water, target_mash_temp, precoolfvvolume, pre_boil_gravity, primingsugarqty, num_crown_caps, estimated_og, estimated_ibu, primingsugartotal, strike_temp_5, mash_liquid, sparge_heating_time, boil_vol, mash_liquid_6, topupvol, extendedboil, estimated_fg, estimated_abv, total_water, grain_weight, nongrain_weight, hops_weight, bottles_required, kettle1volume, kettle2volume, kettle3volume, kettle1kettle2volume, kettle1kettle2kettle3volume, kettle1evaporation, kettle2evaporation, kettle3evaporation, kettle1preboilgravity, kettle2preboilgravity,kettle3preboilgravity, postboilprecoolgravity, preboil_gravity, minikegqty, polypinqty,batchsize,self.brewlog,dryhop),)=row


		self.postboil_precool_og=float(postboil_precool_og)
		self.pretopup_estimated_gravity_grain=float(pretopup_estimated_gravity_grain)
		self.sparge_temp=float(sparge_temp)
		self.pretopup_post_mash_og=float(pretopup_post_mash_og)
		self.strike_temp=float(strike_temp)
		self.primingwater=float(primingwater)
		self.sparge_water=float(sparge_water)
		self.target_mash_temp=float(target_mash_temp)
		self.precoolfvvolume=float(precoolfvvolume)
		self.pre_boil_gravity=float(pre_boil_gravity)
		self.primingsugarqty=float(primingsugarqty)
		self.num_crown_caps=float(num_crown_caps)
		self.estimated_og=float(estimated_og)
		self.estimated_ibu=float(estimated_ibu)
		self.primingsugartotal=float(primingsugartotal)
		self.strike_temp_5=float(strike_temp_5)
		self.mash_liquid=float(mash_liquid)
		self.mash_liquid_6=float(mash_liquid_6)
		self.sparge_heating_time=float(sparge_heating_time)
		self.boil_vol=float(boil_vol)
		self.topupvol=float(topupvol)
		self.estimated_fg=float(estimated_fg)
		self.estimated_abv=float(estimated_abv)
		self.total_water=float(total_water)
		self.grain_weight=float(grain_weight)
		self.nongrain_weight=float(nongrain_weight)
		self.hops_weight=float(hops_weight)
		self.bottles_required=float(bottles_required)
		self.kettle1volume=float(kettle1volume)
		self.kettle2volume=float(kettle2volume)
		self.kettle3volume=float(kettle3volume)
		self.kettle1kettle2volume=float(kettle1kettle2volume)
		self.kettle1kettle2kettle3volume=float(kettle1kettle2kettle3volume)
		self.kettle1preboilgravity=float(kettle1preboilgravity)
		self.kettle2preboilgravity=float(kettle2preboilgravity)
		self.kettle3preboilgravity=float(kettle3preboilgravity)
		self.postboilprecoolgravity=float(postboilprecoolgravity)
		self.preboil_gravity=float(preboil_gravity)
		self.minikegqty=float(minikegqty)
		self.polypinqty=float(polypinqty)
		self.batchsize=float(batchsize)
		self.dryhop=int(dryhop)
		self.kettle1evaporation=float(kettle1evaporation)	
		if int(extendedboil) == 1:
			self.extendedBoil=True
		else:
			self.extendedBoil=False

if __name__ == '__main__':
	allowChanges=0

	results=db().GqlQuery("SELECT * FROM gBrewlogStep WHERE activityNum > -1").fetch(234234)
	for r in results:
		print r
	print len(results)


	sys.exit(0)
	gAuthorisedUsers(authCookie="tetet").put()
	results=db().GqlQuery("SELECT * FROM gAuthorisedUsers WHERE authCookie = :1",'tetet')
	x=results.fetch(5)
	print x[0].toString()
	x[0].delete()
	print x[0]
	
	sys.exit(0)
	results= db().GqlQuery("SELECT * FROM gProcesses")
	for r in results.fetch(54355):
		if allowChanges:
			r.owner="deleted"
			r.put()

	if allowChanges:
		g=gProcesses()
		g.owner="donotuse"
		g.process="ABC"		
		g.put()

	results=db().GqlQuery("SELECT * FROM gSuppliers WHERE owner = :1 ", 'test@example.com')
	for r in results.fetch(234234):
		print r.toString()

	results=db().GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2","test@example.com","15AG10i11")
	for r in results.fetch(234):
		print r.toString()

	results=db().GqlQuery("SELECT * FROM gContributions")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gWidgets")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gProcess")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gEquipment")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gPurchases")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gField")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gBrewlogStep")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gBrewlogs")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gBrewlogStock")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gAuthorisedUsers")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gItems")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gIngredients")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gRecipes")
	for r in results.fetch(234):
		print r.toString()
	results=db().GqlQuery("SELECT * FROM gRecipeStats")
	for r in results.fetch(234):
		print r.toString()

