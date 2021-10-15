import numpy

class BaseStation(object):
	__slots__ = ['county', 'location', 'ID', 'radio', 'speed', 'range', 'carrier', 'customers', 'agreements', 'roaming', 'cap']
	def __init__(self, location, ID, carrier, radio, county):
		
		self.county = county
		self.location = location
		self.ID = ID
		self.radio = radio
		self.speed = self.setInitialSpeed()
		self.range = self.setRange()
		self.carrier = carrier
		self.customers = []
		self.agreements = [self.carrier]
		self.roaming = []
		self.cap = 1

	def disconnect(self, customerID):

		for i, c in enumerate(self.customers):
			if c.id == customerID:
				c.peering = False
				c.roaming = False
				c.baseStation = False
				del self.customers[i]
				self.updateSpeed()					
				break

	def updateSpeed(self):
		cCount = max(0,len(self.customers)-self.cap)
		newSpeed = self.speed*(0.95**(cCount))
		# newSpeed = self.speed*1
		for c in self.customers:
			c.speed = newSpeed
			# c.speed = self.speed

	def newConnection(self, carrier, customer, justTrying=False):
##################################################################################################################
		# if justTrying:
		# 	cCount = max(0,len(self.customers)-19)
		# 	tPeeringSpeed = (self.speed*(0.95**(cCount)))/(max(2,self.speed))
			
		# 	tRoamingSpeed = 0.5/(max(2,self.speed))
		# 	return tPeeringSpeed/self.speed, tRoamingSpeed/self.speed, self.county.coverageArea[self.carrier]/self.county.area
##################################################################################################################
		if (customer.carrier in self.agreements):
			self.customers.append(customer)
			self.updateSpeed()
			if customer.carrier != self.carrier:
				# print(self.carrier, " giving service to ",customer.carrier)
				customer.peering = self.carrier


			return True
		elif (customer.carrier in self.roaming):
			customer.speed = 0.5
			customer.roaming = self.carrier
			return True
		else:
			return False


	
	# def distance(self, p1, p2):
	# 	return 1
	# 	earthRadious = 3959
	# 	dlat = numpy.deg2rad(p2[1] - p1[1])
	# 	dlong = numpy.deg2rad(p2[0] - p1[0])
	# 	a = (numpy.sin(dlat / 2)) ** 2 + numpy.cos(numpy.deg2rad(p1[1])) * numpy.cos(numpy.deg2rad(p2[1])) * ((numpy.sin(dlong / 2)) ** 2)
	# 	c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1 - a))
		
	# 	return c * earthRadious

	def setRange(self):
		r = 10
		if self.radio == "LTE":
			r = 3
		elif self.radio == "CDMA":
			r = 5
		elif self.radio == "UMTS":
			r = 6
		return r

	def setInitialSpeed(self):
# 		gsm: 10mi, 0.5mb
# umts: 10mi, 2mb
# cdma: 15mi, 5mb
# lte: 5mi, 20mb
		speed = 0.5
		if self.radio == "LTE":
			speed = 20
		elif self.radio == "CDMA":
			speed = 5
		elif self.radio == "UMTS":
			speed = 2.5
		return speed
