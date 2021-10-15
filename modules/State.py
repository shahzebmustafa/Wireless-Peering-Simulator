#!/wpeering/bin/python

import json
from .County import County
from collections import defaultdict


class State(object):
	__slots__ = ['id', 'counties', 'ncf','allCounties']
	def __init__(self, id, counties=None):
		self.id = id
		if counties:
			self.counties = counties
		else:
			self.counties = self.getAllCounties()

##############################################################################################################
		# self.counties = {}
		# self.allCounties = self.getAllCounties()
##############################################################################################################		

	def getAllCounties(self):
		data = {}
		myCounties = {}
		with open('Tower Data/county-boundaries.json') as f:
			data = json.load(f)["features"]
		
		i = 30
		for county in data:
			
			if (county["properties"]["STATE"] == self.id) and i > 0:
				i -= 1
			# if (county["properties"]["STATE"] == self.id):
				myCounties[county["properties"]["COUNTY"]] = County(self, county["properties"]["COUNTY"])
				

		return myCounties

	def getAllBS(self):
		data = []
		for county in self.counties.values():
			data.append(county.basestations)

		BSdata = defaultdict(list)
		for countyData in data:
			for carrier, basestations in countyData.items():
				BSdata[carrier] += basestations

		return BSdata
		