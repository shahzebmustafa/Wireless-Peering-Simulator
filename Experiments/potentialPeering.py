from State import State
from Customer import Customer
from statistics import mean
import sys, json, math
import matplotlib.pyplot as plt
from itertools import combinations 
import matplotlib

font = {'family' : 'sans-serif',
        'weight' : 'light',
        'size'   : 12}
matplotlib.rc('font', **font)

def initialize(stateID):

    customers = []
    ID = 0
    testState = State(stateID)

    sampleSize = 10000
    statePopulation = sum([c.population for c in testState.counties.values()])
    for county in testState.counties.values():


        c_division = {}
        towerCount = sum([len(v) for v in county.basestations.values()])
        if (towerCount == 0):
            continue
        
        countyPop = max(100, sampleSize*(county.population/statePopulation))
        
        for k,v in county.basestations.items():
            c_division[k] = int(countyPop*(len(v)/towerCount))
        
        for k,v in c_division.items():

            for i in range(0,v):
                c = Customer(ID, k, county, testState)
                ID += 1
                customers.append(c)
    
    return customers, testState


def start(state=None, customers=[], cycleCount=100):
    
    csats = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    csats_ = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    csats["peering"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    csats["roaming"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}

    csats_["peering"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    csats_["roaming"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    
    resetCustomerCSAT(customers)

    for j in range(0,cycleCount):
        for user in customers:

            user.move()

        for user in customers:
            customerCSAT = {"csat":user.CSAT["csat"], "speed":user.CSAT["speed"], "signal":user.CSAT["signal"], "coverage":user.CSAT["coverage"]}
            csats_["AVG"].append(customerCSAT)
            csats_[user.carrier].append(customerCSAT)
            
            customerCSAT = {"csat":user.CSAT["peering"]["csat"], "speed":user.CSAT["peering"]["speed"], "signal":user.CSAT["peering"]["signal"], "coverage":user.CSAT["peering"]["coverage"]}
            csats_["peering"]["AVG"].append(customerCSAT)
            csats_["peering"][user.carrier].append(customerCSAT)

            customerCSAT = {"csat":user.CSAT["roaming"]["csat"], "speed":user.CSAT["roaming"]["speed"], "signal":user.CSAT["roaming"]["signal"], "coverage":user.CSAT["roaming"]["coverage"]}
            csats_["roaming"]["AVG"].append(customerCSAT)
            csats_["roaming"][user.carrier].append(customerCSAT)

        for k,v in csats_.items():
            if (k != "peering") and (k != "roaming"):
                avgCSAT = {"csat":mean([u["csat"] for u in v]), "speed":mean([u["speed"] for u in v]), "signal":mean([u["signal"] for u in v]), "coverage":mean([u["coverage"] for u in v])}
                csats[k].append(avgCSAT)
                
                avgCSAT = {"csat":mean([u["csat"] for u in csats_["peering"][k]]), "speed":mean([u["speed"] for u in csats_["peering"][k]]), "signal":mean([u["signal"] for u in csats_["peering"][k]]), "coverage":mean([u["coverage"] for u in csats_["peering"][k]])}
                csats["peering"][k].append(avgCSAT)

                avgCSAT = {"csat":mean([u["csat"] for u in csats_["roaming"][k]]), "speed":mean([u["speed"] for u in csats_["roaming"][k]]), "signal":mean([u["signal"] for u in csats_["roaming"][k]]), "coverage":mean([u["coverage"] for u in csats_["roaming"][k]])}
                csats["roaming"][k].append(avgCSAT)

        print(j+1,end='\r')

#     print("Total CSATs: \n    SPRINT: {}\n    VERIZON: {}\n    T-MOBILE: {}\n    AT&T: {}".format(mean(csats["SPRINT"]), mean(csats["VERIZON"]), mean(csats["T_MOBILE"]), mean(csats["AT_T"])))

    return csats


def resetCustomerCSAT(customers):
    
    for c in customers:
        c.CSAT["csat"] = 1
        c.CSAT["weight"] = 1
        c.CSAT["speed"] = 1
        c.CSAT["coverage"] = 1
        c.CSAT["signal"] = 1



if __name__ == "__main__":

    stateID = "48"
    customers,state = initialize(stateID)
    cycleCount = 100
    print("Sample Size: ",len(customers))
    potential_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)
    metric = "csat"

    with open("./Tower Data/Results/potential_peering_csats.json","w") as f:
        json.dump(potential_peering_csats, f)

    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    # colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}

    for c in carriers:
        plt.plot(range(0,cycleCount),[csat[metric] for csat in potential_peering_csats[c]] ,label="Independent", color='k', linewidth=3)
        plt.plot(range(0,cycleCount),[csat[metric] for csat in potential_peering_csats["peering"][c]], '--' ,label="Peering", color='dodgerblue', linewidth=3)
        plt.plot(range(0,cycleCount),[csat[metric] for csat in potential_peering_csats["roaming"][c]], '--' ,label="Roaming", color='orange', linewidth=3)
        plt.title("Peering vs. Roaming - {}".format(c))
        plt.legend()
        plt.ylabel("Customer Satisfaction (CSAT)")
        plt.xlabel("Cycle")
        
        plt.savefig("./Tower Data/Results/Figs/potential_{}.pdf".format(c))