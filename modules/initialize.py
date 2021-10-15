#!/wpeering/bin/python

from .State import State
from .Customer import Customer
from .BSGraph import drawBSGraphs

def initialize(stateID, sampleSize=False):
    print("Initializing Customers and State")
    # drawBSGraphs(stateID)
    # return
    customers = []
    ID = 0
    testState = State(stateID)

    statePopulation = sum([c.population for c in testState.counties.values()])
    for county in testState.counties.values():
        c_division = {}
        towerCount = sum([len(v) for v in county.basestations.values()])
        if (towerCount == 0):
            continue
        countyPop = 0
        if sampleSize:
            # print(sampleSize)
            countyPop = max(10, sampleSize*(county.population/statePopulation))
        else:
            countyPop = max(10, county.population/1000)
        
        for k,v in county.basestations.items():
            c_division[k] = int(countyPop*(len(v)/towerCount))
#             c_division[k] = len(v)
        
        for k,v in c_division.items():

            for i in range(0,v):
                c = Customer(ID, k, county, testState)
                ID += 1
                customers.append(c)

    drawBSGraphs(testState)
    return customers, testState