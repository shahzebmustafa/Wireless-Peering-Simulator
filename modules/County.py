from shapely.geometry import Point, Polygon, mapping, asShape
from shapely.ops import cascaded_union
from area import area
from .BaseStation import BaseStation
import numpy as np
import math, geog
import json
# def areaFor2Points(p1, p2):
#     earthRadious = 3959
#     dlat = np.deg2rad(p2[1] - p1[1])
#     dlong = np.deg2rad(p2[0] - p1[0])
#     a = (np.sin(dlat / 2)) ** 2 + np.cos(np.deg2rad(p1[1])) * np.cos(np.deg2rad(p2[1])) * ((np.sin(dlong / 2)) ** 2)
#     b = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
#     b *= earthRadious
#     b /= 2

#     p = b*math.tan(math.radians(22.5))

#     return 2*(p*b)





class County(object):
    __slots__ = ['id', 'state', 'basestations', 'area', 'population', 'geometry', 'bounds','properties', 'pop_density', 'coverageArea']
    def __init__(self, state, countyID):
        self.id = countyID
        self.state = state
        self.basestations, self.geometry, properties = self.readCountyDataFromFile()
        self.bounds = asShape(self.geometry).bounds
        self.area = properties["CENSUSAREA"]
        self.population = properties["population"]
        self.pop_density = properties["pop_density"]
        self.coverageArea = self.getCoverageArea()


    def createBSs(self, bsInfoList):
        bsList = []
        for i,bs in enumerate(bsInfoList):
            bs["location"].reverse()
            bsList.append(BaseStation(tuple(bs["location"]), i, bs["network"], bs["radio"], self))
        return bsList

        
    def readCountyDataFromFile(self):
        import json
        carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
        bs_data = dict()
        for c in carriers:
            with open('Tower Data/States/{}/{}.json'.format(c,self.state.id)) as f:
                data = json.load(f)
                bs_data[c] = self.createBSs(data[self.id]["basestations"])
                

        return bs_data, data[self.id]["geometry"], data[self.id]["properties"]

    # def bsLocations(self, bsList):
    #     locations = []
    #     for bs in bsList:
    #         locations.append([bs.location[1],bs.location[0]])
    #     return locations


    def getCoverageArea(self):
        cArea = dict()
        covgPolygon = 0
        for k,basestations in self.basestations.items():

            circles = []
            cArea[k] = 0
            
            for bs in basestations:
                p = Point(bs.location)

                n_points = 20
                d = bs.range * 1609.34  # miles to meters
                angles = np.linspace(0, 360, n_points)
                polygon = geog.propagate(p, angles, d)
                circles.append(Polygon(polygon))
                

            covgPolygon = cascaded_union(circles)
            cArea[k] = min(area(mapping(covgPolygon))/2590000,self.area)
            # print("County:",self.id,k,"COVG:", cArea[k]/self.area, "BS:",len(basestations))
            # if self.id=='009':
            #     print(json.dumps(mapping(covgPolygon)))
                # input("Enter ")

        return cArea

