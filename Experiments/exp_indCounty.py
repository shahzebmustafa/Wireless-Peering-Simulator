if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from modules.State import State
from modules.Customer import Customer
from modules.start import start
from itertools import combinations
import json, math
# from dask.distributed import Client, progress
from count_bs import createBenefitCSV
from dask.diagnostics import ProgressBar
import logging

logger = logging.getLogger("distributed.utils_perf")
logger.setLevel(logging.ERROR)

logger = logging.getLogger("distributed.worker")
logger.setLevel(logging.ERROR)

def createCustomers(state, county, carriers=['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']):
    customers = []
    c_division = {}
    ID = 1
    towerCount = sum([len(v) for v in county.basestations.values()])
    if (towerCount == 0):
        return []


    for k,v in county.basestations.items():
        # c_division[k] = len(v)
        if k in carriers:
            c_division[k] = max(10,math.ceil(((county.population/1000.0)*(len(v)/towerCount))))


    for k,v in c_division.items():
        for i in range(0,v):
            c = Customer(ID, k, county, state)
            ID += 1
            customers.append(c)
    return customers



def run(state, client, cycleCount=100, metric="csat", carriers=['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']):
    
    carrier_combinations = combinations(carriers,2)
    parentState = State(state)

    for pair in carrier_combinations:
        if(pair[0]=="VERIZON" and pair[1]=="T_MOBILE"):
            continue
        print('\n',pair)
        benefit = {pair[0]: [], pair[1]: []}

        testStates = {"peering":[], "non_peering":[]}
        customers = {"peering":[], "non_peering":[]}

        for countyID,county in parentState.counties.items():

            testStates["non_peering"].append(State(id=state,counties={countyID:county}))
            customers["non_peering"].append(createCustomers(testStates["non_peering"][-1], county, pair))

            testStates["peering"].append(State(id=state,counties={countyID:county}))
            customers["peering"].append(createCustomers(testStates["peering"][-1], county, pair))

        with ProgressBar():
            no_peering_csats = client.map(start,*[testStates["non_peering"], 
                                                            customers["non_peering"]],
                                                            peering=False,)
            peering_csats = client.map(start,*[testStates["peering"], 
                                                        customers["peering"]],
                                                        peering=pair, 
                                                        forcePeering=True)
        # progress(no_peering_csats,peering_csats)

        no_peering_csats = client.gather(no_peering_csats)
        peering_csats = client.gather(peering_csats)

        # print(client.gather(no_peering_csats[-1][pair[0]][-1]))
        # print(client.gather(peering_csats[-1][pair[1]][-1]))

        ptr = 0
        for countyID,county in parentState.counties.items():

            before = [no_peering_csats[ptr][pair[0]][-1][metric],no_peering_csats[ptr][pair[1]][-1][metric]]
            after = [peering_csats[ptr][pair[0]][-1][metric],peering_csats[ptr][pair[1]][-1][metric]]

            ptr += 1

            benefit[pair[0]].append({
                "county":countyID,
                "benefit": after[0]-before[0],
                "before": before[0],
                "after": after[0],
                "peering":False

            })
            benefit[pair[1]].append({
                "county":countyID,
                "benefit": after[1]-before[1],
                "before": before[1],
                "after": after[1],
                "peering":False
            })

        # for i in range(0,len(customers)):
            # benefit[pair[0]].append({"county":county.id, "benefit": peering_csats[pair[0]][-1][metric]-no_peering_csats[pair[0]][-1][metric], "peering":False, "before":no_peering_csats[pair[0]][-1][metric], "after":peering_csats[pair[0]][-1][metric]})
            # benefit[pair[1]].append({"county":county.id, "benefit": peering_csats[pair[1]][-1][metric]-no_peering_csats[pair[1]][-1][metric], "peering":False, "before":no_peering_csats[pair[1]][-1][metric], "after":peering_csats[pair[1]][-1][metric]})
            
            # print(int((i/totalCounties)*100),"%",end='\r')

            # i += 1

        with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
            json.dump(benefit, f)


if __name__ == "__main__":

    run("48",client)
    createBenefitCSV("48")
    