import random
from shapely.geometry import Point, asShape
import numpy, copy
import cProfile
import pstats
from haversine import haversine_vector

def random_county_within_state(state, ownCounty):
	rCounty = random.choice(list(state.counties.values()))
	
	return rCounty

class Customer(object):
	__slots__ = ['id', 'location', 'carrier', 'baseStation', 'signal', 'speed', 'CSAT', 'county', 'state', 'coverage', 'trip', 'peering','roaming']
	def __init__(self, id, carrier, county, state):
		self.id = id
		self.location = []
		self.carrier = carrier
		self.baseStation = False
		self.signal = 1
		self.speed = 1
		self.CSAT = {"speed": 1, "signal":1, "coverage":1, "csat": 1, "weight":1}
##############################################################################################################		
		# self.CSAT["peering"] = {"speed": 1, "signal":1, "coverage":1, "csat": 1, "weight":1}
		# self.CSAT["roaming"] = {"speed": 1, "signal":1, "coverage":1, "csat": 1, "weight":1}
##############################################################################################################
		self.county = county
		self.state = state
		self.coverage = 1
		self.trip = [0,False]
		self.peering = False
		self.roaming = False


	

	def trySharing(self, others):
		
		for bs in others:

			if bs["bs"].newConnection(self.carrier, self):
		
				self.baseStation = bs["bs"]
				self.setSignalStrength(bs["d"])
				self.setSpeed()
				self.setCoverage()
				# print("here")
				return
		

		self.baseStation = False
		self.signal = 0
		self.coverage = 0
		self.speed = 0

##############################################################################################################
		# if(len(others)>0):
		# 	tPeeringSpeed, tRoamingSpeed, tCoverage =others[0]["bs"].newConnection(self.carrier, self, True)
		# 	tDist = others[0]["d"]
		# 	signal = 1/ (max(1,tDist/2.0) **2)
		# 	self.setPotentialCSAT(tPeeringSpeed, tRoamingSpeed, signal, signal, tCoverage, tCoverage)
		# else:
		# 	self.setPotentialCSAT(0, 0, 0, 0, 0, 0)
##############################################################################################################

	def getConnection(self):
		if self.baseStation:
			self.baseStation.disconnect(self.id)

		closestBSs = self.getClosestBaseStation()
		# print([(bs["carrier"],bs["d"]) for bs in closestBSs])
		
		for bs in closestBSs:
			# if bs["bs"]:
			# 	print(bs["d"],bs["bs"].range)
				# print("Checking {}-{} at {}".format(bs["bs"].carrier, self.carrier, self.location))
			if bs["bs"] and bs["bs"].newConnection(self.carrier, self):
				self.baseStation = bs["bs"]
				self.setSignalStrength(bs["d"])
				self.setSpeed()
				self.setCoverage()

				if (bs["d"] >= bs["bs"].range):

					self.speed = 0.25
				# print("CONNECTED!",bs["d"],"Speed:",self.speed,"Covg:",self.coverage,"Signal:",self.signal)

				# print("got it!", self.speed, self.coverage, self.signal)
				# print("My Carrier: {}, got connection from {}".format(self.carrier,bs["carrier"]))
				# print("{} connections, {} radio, {} speed, {} coverage, {} distance".format(len(bs["bs"].customers), bs["bs"].radio, self.speed, self.coverage, bs["d"]))
				# for tbs in closestBSs:
				# 	if tbs["carrier"] == self.carrier and tbs["bs"]:
				# 		print("My carrier: {} connections, {} radio, {} speed, {} coverage, {} distance".format(len(tbs["bs"].customers), tbs["bs"].radio, "-", self.county.coverageArea[self.carrier]/self.county.area, tbs["d"]))
				# 		break
				# print(self.carrier, bs["bs"].carrier, closestBSs)
				# print("--------")
				break
##############################################################################################################
			# if len(others) > 0:
			# 	tPeeringSpeed, tRoamingSpeed, tCoverage =others[0]["bs"].newConnection(self.carrier, self, True)
			# 	tDist = others[0]["d"]
			# 	signal = 1/ (max(1,tDist/2.0) **2)
			# 	# print(max(tPeeringSpeed,self.speed), self.speed, max(signal,self.signal), self.signal, max(tCoverage,self.coverage), self.coverage)
			# 	self.setPotentialCSAT(max(tPeeringSpeed,self.speed), self.speed, max(signal,self.signal), self.signal, max(tCoverage,self.coverage), self.coverage)
			# else:
			# 	self.setPotentialCSAT(self.speed, self.speed, self.signal, self.signal, self.coverage, self.coverage)
##############################################################################################################				
		# else:
		# 	self.trySharing(others)
		if not self.baseStation:
			# print("No connection")
			self.signal = 0
			self.coverage = 0
			self.speed = 0
		
		# print("UPDATING")
		self.updateCSAT()

	def setSpeed(self):
		self.speed = self.speed/max(2,self.baseStation.speed)


	def distance(self, cLoc, bsLoc):
		if bsLoc:
			return haversine_vector([cLoc]*len(bsLoc), bsLoc, 'mi')
			# print(ds)
			# return ds
		else:
			return []
		# return 1
		# earthRadius = 3959
		# dlat = numpy.deg2rad(p2[1] - p1[1])
		# dlong = numpy.deg2rad(p2[0] - p1[0])
		# a = (numpy.sin(dlat / 2)) ** 2 + numpy.cos(numpy.deg2rad(p1[1])) * numpy.cos(numpy.deg2rad(p2[1])) * ((numpy.sin(dlong / 2)) ** 2)
		# c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1 - a))
		
		# return c * earthRadius

	def setSignalStrength(self, dist):
		# print("DIST: ",dist)
		dist = max(1,dist/2.0)
		self.signal = 1/(dist**2)

	def setCoverage(self):
		if self.peering:
			self.coverage = max((self.county.coverageArea[self.peering]/self.county.area),(self.county.coverageArea[self.carrier]/self.county.area))

		elif self.roaming:
			self.coverage = self.county.coverageArea[self.roaming]/self.county.area
		else:
			self.coverage = self.county.coverageArea[self.carrier]/self.county.area
			# print(self.county.coverageArea)
			# print("{}: {}/{}={}".format(self.county.id,self.county.coverageArea[self.carrier],self.county.area, self.coverage))

	def getClosestBaseStation(self):
		
		allBSs = self.county.basestations
		# print("My County: {}, my Carrier: {}, my BS: {}".format(self.county.id, self.carrier, len([b.ID for b in self.county.basestations[self.carrier]])))

		result = {"T_MOBILE": {"bs":None, "d": 1000}, "AT_T": {"bs":None, "d": 1000}, "VERIZON": {"bs":None, "d": 1000}, "SPRINT": {"bs":None, "d": 1000}}

		for carrier, bss in allBSs.items():

			d = 1000
			# print(carrier)
			ds = self.distance(self.location,[bs.location for bs in bss])
			# print(ds)
			for i,bs in enumerate(bss):
				# print(ds[i] , bs.range)
				# print(self.trip, bs.county.id)
				# print(self.county.id)
				# print(self.location , bs.location)

				# print(self.county.id, bs.county.id)
				# print(bs.location)
				if ((ds[i] <= bs.range) or (ds[i] <= 10) ) and (ds[i] < d):
					d = ds[i]
					result[carrier]["bs"] = bs
					result[carrier]["d"] = d

		tempResult = []
		
		# IF MY CARRIER AND OTHER CARRIER ARE EQUALLY FAR AWAY, PREFER MY CARRIER:
		result[self.carrier]["d"] = max(0,result[self.carrier]["d"]-0.01)

		for carrier, bs in result.items():
			tempResult.append({"carrier":carrier,"bs":bs["bs"], "d":bs["d"]})

		
		# if (result[self.carrier]["d"] == tempResult[0]["d"]) and (self.carrier != tempResult[0]["carrier"]):


		

		result = sorted(tempResult, key = lambda i: i['d'])
		
		# print(tempResult)
		# import sys
		# sys.exit(1)
		return result
		# myBS = result.pop(self.carrier)
		# others = list(result.values())
##################################################################################################################		
		# others = sorted(others, key = lambda i: i['d'])
##################################################################################################################
		# return myBS, others
		



		# d = float('inf')
		# rBS = None
		
		# for bs in bss:
		# 	bsRange = bs.range
		# 	d_ = self.distance(self.location, bs.location)
		# 	if (d_ < d) and (d_ <= bs.range):
		# 		d = d_ 
		# 		rBS = bs
		# 	if d <= 2.0:
		# 		return rBS,d

		
		# others = []

		# # if (rBS == None) or (d > rBS.range):
		# 	# print(rBS,d,rBS.range)
		# bss = self.county.basestations
		# for k,v in bss.items():
		# 	rBS_ = False
		# 	for bs in v:
		# 		bsRange = bs.range
		# 		minD = float('inf')
		# 		d_ = self.distance(self.location, bs.location)
		# 		if (d_ <= bsRange) and (d_ < minD):
					
		# 			# print("Self Carrier: {}, Roaming Carrier: {}".format(self.carrier, k),bsRange)
		# 			rBS_ = bs
		# 			minD = d_
		# 	if rBS_:
		# 		others.append({"bs":rBS_,"d":minD})
		# return {"bs":rBS, "d":d}, sorted(others, key = lambda i: i['d'])
		# # else:
		# # 	return {"bs":rBS, "d":d}, others




	def setLocation(self, loc, county, state):
		if county and state:
			# print("Setting county:",county.id)
			self.county = county
			self.state = state
			# print("Set!!!!!! :",self.county.id)
		self.location = loc
		

	def random_point_within_county(self, county):
		poly = asShape(county.geometry)
		# min_x, min_y, max_x, max_y = poly.bounds
		min_x, min_y, max_x, max_y = county.bounds

		points = []

		while len(points) < 1:
			random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
			# points.append(random_point)
			if (random_point.within(poly)):
				points.append(random_point)


		# print([points[0].x, points[0].y])
		return [points[0].y, points[0].x]
	
	def updateCSAT(self):

		
		# print("CSAT({} in {}): Speed; {}, Coverage: {}, Signal: {}".format(self.carrier, self.county.id, self.speed, self.coverage, self.signal))
		
		newCSAT = (self.coverage * self.speed * self.signal) ** (1. /3)
		self.CSAT["csat"] = ((self.CSAT["csat"]*self.CSAT["weight"]) + newCSAT) / (self.CSAT["weight"]+1)
		self.CSAT["speed"] = ((self.CSAT["speed"]*self.CSAT["weight"]) + self.speed) / (self.CSAT["weight"]+1)
		self.CSAT["coverage"] = ((self.CSAT["coverage"]*self.CSAT["weight"]) + self.coverage) / (self.CSAT["weight"]+1)
		self.CSAT["signal"] = ((self.CSAT["signal"]*self.CSAT["weight"]) + self.signal) / (self.CSAT["weight"]+1)
		
		self.CSAT["weight"] += 1
		

	def setPotentialCSAT(self,tPeeringSpeed, tRoamingSpeed, tPeeringSignal, tRoamingSignal, tPeeringCoverage, tRoamingCoverage):
		
		# signal = 1/ (max(1,tDist/2.0) **2)
		peeringCSAT = (tPeeringCoverage * tPeeringSpeed * tPeeringSignal) ** (1. /3)
		roamingCSAT = (tRoamingCoverage * tRoamingSpeed * tRoamingSignal) ** (1. /3)


		self.CSAT["peering"]["csat"] = ((self.CSAT["peering"]["csat"]*self.CSAT["peering"]["weight"]) + peeringCSAT) / (self.CSAT["peering"]["weight"]+1)
		self.CSAT["peering"]["speed"] = ((self.CSAT["peering"]["speed"]*self.CSAT["peering"]["weight"]) + tPeeringSpeed) / (self.CSAT["peering"]["weight"]+1)
		self.CSAT["peering"]["coverage"] = ((self.CSAT["peering"]["coverage"]*self.CSAT["peering"]["weight"]) + tPeeringCoverage) / (self.CSAT["peering"]["weight"]+1)
		self.CSAT["peering"]["signal"] = ((self.CSAT["peering"]["signal"]*self.CSAT["peering"]["weight"]) + tPeeringSignal) / (self.CSAT["peering"]["weight"]+1)
		
		self.CSAT["peering"]["weight"] += 1


		self.CSAT["roaming"]["csat"] = ((self.CSAT["roaming"]["csat"]*self.CSAT["roaming"]["weight"]) + roamingCSAT) / (self.CSAT["roaming"]["weight"]+1)
		self.CSAT["roaming"]["speed"] = ((self.CSAT["roaming"]["speed"]*self.CSAT["roaming"]["weight"]) + tRoamingSpeed) / (self.CSAT["roaming"]["weight"]+1)
		self.CSAT["roaming"]["coverage"] = ((self.CSAT["roaming"]["coverage"]*self.CSAT["roaming"]["weight"]) + tRoamingCoverage) / (self.CSAT["roaming"]["weight"]+1)
		self.CSAT["roaming"]["signal"] = ((self.CSAT["roaming"]["signal"]*self.CSAT["roaming"]["weight"]) + tRoamingSignal) / (self.CSAT["roaming"]["weight"]+1)
		# self.CSAT["roaming"]["coverage"] = copy.deepcopy(self.CSAT["peering"]["coverage"])
		# self.CSAT["roaming"]["signal"] = copy.deepcopy(self.CSAT["peering"]["signal"])
		# self.CSAT["roaming"]["coverage"] = ((self.CSAT["roaming"]["coverage"]*self.CSAT["roaming"]["weight"]) + self.coverage) / (self.CSAT["roaming"]["weight"]+1)
		# self.CSAT["roaming"]["signal"] = ((self.CSAT["roaming"]["signal"]*self.CSAT["roaming"]["weight"]) + max(self.signal,signal)) / (self.CSAT["roaming"]["weight"]+1)
		


		self.CSAT["roaming"]["weight"] += 1
	

	def move(self):
		# profile = cProfile.Profile()
		# profile.enable()
		# print("BEFORE",self.CSAT)

		
		m = random.uniform(0, 100)
		county = None

		if m < 10 and (self.trip[0] == 0) and (not self.trip[1]):
			
			self.trip = [int(random.uniform(0, 10)),self.county.id]
			
			county = random_county_within_state(self.state, self.county)
			# print("Trip: {} to {}".format(self.county.id,county.id))
			
			m = self.random_point_within_county(county)
			
		elif self.trip[0] == 0 and self.trip[1]:
			# print("Returning: {} to {}".format(self.county.id,self.trip[1]))
			county = self.state.counties[self.trip[1]]
			m = self.random_point_within_county(self.state.counties[self.trip[1]])
			
			self.trip = [0,False]
			
		else:
			
			m = self.random_point_within_county(self.county)
			self.trip[0] = max(self.trip[0]-1,0)

		######################################################################
		# DEBUG PRINTS
		# print("Customer {} moved to ({},{})".format(self.id, m[0], m[1]))
		######################################################################
		
		self.setLocation(m, county, self.state)
		# print(self.county.id)
		self.getConnection()

		# print(self.CSAT)
		
		# profile.disable()
		# ps = pstats.Stats(profile)
		# ps.print_stats()