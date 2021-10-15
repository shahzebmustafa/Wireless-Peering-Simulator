from modules.State import State
from modules.Customer import Customer
from modules.start import start
from itertools import combinations
import json, math
from os.path import exists

# from count_bs import createBenefitCSV


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



def indCountyBenefits(state, carrier_combinations, cycleCount=100, metric="csat"):

    for pair in carrier_combinations:
        if exists("./Results/Experiments/County Gain/{}_{}.json".format(pair[0],pair[1])):
            continue
        benefit = {pair[0]: [], pair[1]: []}

        # testStates = {"peering":[], "non_peering":[]}
        customers = {"peering":[], "non_peering":[]}
        no_peering_csats = []
        peering_csats = []

        for countyID,county in state.counties.items():
            
            peeringState = State(id=state.id, counties = {countyID:county})
            peeringCustomers = createCustomers(peeringState, county, pair)
            no_peering_csats.append(start( state = peeringState, customers = peeringCustomers ) )
            
            notPeeringState = State(id=state.id, counties = {countyID:county})
            notPeeringCustomers = createCustomers(notPeeringState, county, pair)
            peering_csats.append(start( notPeeringState, customers = notPeeringCustomers, peering = pair, forcePeering = True ))


        #     testStates["non_peering"].append(State(id=state.id,counties={countyID:county}))
        #     customers["non_peering"].append(createCustomers(testStates["non_peering"][-1], county, pair))

        #     testStates["peering"].append(State(id=state.id,counties={countyID:county}))
        #     customers["peering"].append(createCustomers(testStates["peering"][-1], county, pair))

        # with ProgressBar():
        #     no_peering_csats = client.map(start,*[testStates["non_peering"], 
        #                                                     customers["non_peering"]],
        #                                                     peering=False,)
        #     peering_csats = client.map(start,*[testStates["peering"], 
        #                                                 customers["peering"]],
        #                                                 peering=pair, 
        #                                                 forcePeering=True)

        # no_peering_csats = client.gather(no_peering_csats)
        # peering_csats = client.gather(peering_csats)

        ptr = 0
        for countyID,county in state.counties.items():

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

        with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
            json.dump(benefit, f)

if __name__ == "__main__":

    run("48")
    # createBenefitCSV("48")
    