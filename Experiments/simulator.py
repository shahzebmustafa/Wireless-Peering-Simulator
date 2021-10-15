from State import State
from Customer import Customer
from statistics import mean
import sys, json
import matplotlib.pyplot as plt
from itertools import combinations 


def initialize(stateID):

    customers = []
    ID = 0
    testState = State(stateID)
    for county in testState.counties.values():
        c_division = {}
        towerCount = sum([len(v) for k,v in county.basestations.items()])
        if (towerCount == 0):
            continue
        
        # countyPop = min(1000,int(county.population/100))
        countyPop = min(1000,county.pop_density)
        countyPop = max(4,countyPop)
        for k,v in county.basestations.items():
            c_division[k] = int(countyPop * len(v)/towerCount)
        for k,v in c_division.items():
            for i in range(0,v):
                c = Customer(ID, k, county, testState)
                ID += 1
                customers.append(c)
    
    return customers, testState





def start(state, customers, peering=False, roaming=False):
    csats = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    csats_ = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    
    resetCustomerCSAT(customers)
    if(peering):
        enablePeering(state, peering[0],peering[1])
    elif(roaming):
        enableRoaming(state, roaming[0],roaming[1])

    for j in range(0,100):
        for i,user in enumerate(customers):

            user.move()         
        for user in customers:
            csats_["AVG"].append(user.CSAT["csat"])
            csats_[user.carrier].append(user.CSAT["csat"])
        
        for k,v in csats_.items():
            csats[k].append(mean(v))
            
            
        print(j+1,end='\r')
    return csats




def acceptablePeering(peeringCounties, c1, c2):
    peeringCounties_ = {c1:[], c2:[]}
    pop = {c1:0, c2:0}
    larger = c1
    smaller = c2
    pop[c1] = sum([c.population for c in peeringCounties[c1]])
    pop[c2] = sum([c.population for c in peeringCounties[c2]])

    if pop[c1] < pop[c2]:
        larger = c2
        smaller = c1
    
    peeringCounties_[smaller] = peeringCounties[smaller]
    tpop = 0
    for county in peeringCounties[larger]:
        if tpop < pop[smaller]:
            peeringCounties_[larger].append(county)
            tpop = tpop + county.population
        
    return peeringCounties_



def enablePeering(state, c1=None, c2=None):
    peeringCounties = {c1:[], c2:[]}

    for county in state.counties.values():
        c1Coverage = county.coverageArea[c1]/county.area
        c2Coverage = county.coverageArea[c2]/county.area
        if (county.pop_density < 85) and ((c1Coverage<=0.2) ^ (c2Coverage<=0.2)):
            if c1Coverage <= 0.2:
                peeringCounties[c2].append(county)
            else:
                peeringCounties[c1].append(county)
    
    peeringCounties = acceptablePeering(peeringCounties, c1, c2)
    
    for county in peeringCounties[c1]:
        for bs in county.basestations[c1]:
            bs.agreements.append(c2)
            
    for county in peeringCounties[c2]:
        for bs in county.basestations[c2]:
            bs.agreements.append(c1)

        

def enableRoaming(state, c1, c2):
    roamingCounties = {c1:[], c2:[]}

    for county in state.counties.values():
        c1Coverage = county.coverageArea[c1]/county.area
        c2Coverage = county.coverageArea[c2]/county.area
        if (county.pop_density < 85) and ((c1Coverage==0) ^ (c2Coverage==0)):
            if c1Coverage == 0:
                roamingCounties[c2].append(county)
            else:
                roamingCounties[c1].append(county)
    
    for county in roamingCounties[c1]:
        for bs in county.basestations[c1]:
            bs.roaming.append(c2)
            
    for county in roamingCounties[c2]:
        for bs in county.basestations[c2]:
            bs.roaming.append(c1)




def resetCustomerCSAT(customers):
    
    for c in customers:
        c.CSAT["csat"] = 1



def getAvgCSAT(customers, carrier):
    avg = []
    for c in customers:
        if c.carrier == carrier:
            avg.append(c.CSAT["csat"])
    return round(sum(avg)/len(avg),2)


################################### STARTING EXPERIMENTS ###################################
stateID = "48"
customers,state = initialize(stateID)




########################### WITHOUT PEERING ###########################
def start_without_peering(state, customers):
    no_peering_csats = start(state, customers)

    with open("./Tower Data/Results/no_peering_csats.json","w") as f:
        json.dump(no_peering_csats, f)

    plt.plot(range(0,100),no_peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,100),no_peering_csats["SPRINT"], label="SPRINT")
    plt.plot(range(0,100),no_peering_csats["AT_T"], label="AT_T")
    plt.plot(range(0,100),no_peering_csats["VERIZON"], label="VERIZON")
    plt.plot(range(0,100),no_peering_csats["T_MOBILE"], label="T_MOBILE")
    plt.ylim([0,1])
    plt.legend()
    plt.title("Average CSAT without peering")
    plt.savefig("Tower Data/Results/Figs/no_peering.pdf")

    return no_peering_csats
########################### WITH PEERING ###########################

def start_with_peering(state, customers, pair, no_peering_csats):
    # carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    # peering_combinations = combinations(carriers,2)


    # for pair in peering_combinations:
        
    peering_csats = start(state, customers, peering=pair)

    with open('Tower Data/Results/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
        json.dump(peering_csats, f)


    print("Average CSATs with peering ({}, {}):".format(pair[0],pair[1]))
    print("{}: \t{}".format(pair[0],getAvgCSAT(customers,pair[0])))
    print("{}: \t{}\n\n".format(pair[1],getAvgCSAT(customers,pair[1])))


#     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,100),peering_csats[pair[0]], label=pair[0], color='r')
    plt.plot(range(0,100),peering_csats[pair[1]], label=pair[1], color='b')
    plt.plot(range(0,100),no_peering_csats[pair[0]], "-.", color='r' )
    plt.plot(range(0,100),no_peering_csats[pair[1]], "-.", color='b')
    plt.ylim([0,1])
    plt.legend()
    plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
    plt.savefig("Tower Data/Results/Figs/peering_{}_{}.pdf".format(pair[0],pair[1]))




########################### WITH ROAMING ###########################

def start_with_roaming(state, customers, pair, no_peering_csats):
    # carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    # roaming_combinations = combinations(carriers,2)


    # for pair in roaming_combinations:
        
    roaming_csats = start(state, customers, roaming=pair)

    with open('Tower Data/Results/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
        json.dump(roaming_csats, f)


    print("Average CSATs with peering ({}, {}):".format(pair[0],pair[1]))
    print("{}: \t{}".format(pair[0],getAvgCSAT(customers,pair[0])))
    print("{}: \t{}\n\n".format(pair[1],getAvgCSAT(customers,pair[1])))


#     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,100),roaming_csats[pair[0]], label=pair[0], color='r')
    plt.plot(range(0,100),roaming_csats[pair[1]], label=pair[1], color='b')
    plt.plot(range(0,100),no_peering_csats[pair[0]], "-.", color='r' )
    plt.plot(range(0,100),no_peering_csats[pair[1]], "-.", color='b')
    plt.ylim([0,1])
    plt.legend()
    plt.title("Average CSAT with roaming ({},{})".format(pair[0],pair[1]))
    plt.savefig("Tower Data/Results/Figs/roaming_{}_{}.pdf".format(pair[0],pair[1]))

    


if __name__ == "__main__":
    stateID = sys.argv[1]
    _r_p_n = sys.argv[2]
    c1 = c2 = None
    if _r_p_n != "-n" and _r_p_n != "-a":
        c1 = sys.argv[3]
        c2 = sys.argv[4]

    customers,state = initialize(stateID)
    print("Initialized {} counties.".format())

    if _r_p_n == "-n":
        start_without_peering(state, customers)
    elif _r_p_n == "-p":
        # no_peering_csats = {}
        # with open("./Tower Data/Results/no_peering_csats.json",'r') as f:
        #     no_peering_csats = json.load(f)
        no_peering_csats = start_without_peering(state, customers)
        start_with_peering(state, customers, [c1,c2], no_peering_csats)
    elif _r_p_n == "-r":
        # no_peering_csats = {}
        # with open("./Tower Data/Results/no_peering_csats.json",'r') as f:
        #     no_peering_csats = json.load(f)
        no_peering_csats = start_without_peering(state, customers)
        start_with_roaming(state, customers, [c1,c2], no_peering_csats)
    elif _r_p_n == "-a":
        print("No Peering Progess:")
        no_peering_csats = start_without_peering(state, customers)

        carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
        combs = combinations(carriers,2)

        for pair in combs:
            
            print("Peering Progress:")
            start_with_peering(state, customers, pair, no_peering_csats)
            print("Roaming Progress")
            start_with_roaming(state, customers, pair, no_peering_csats)
    





    




















# def initialize(stateID):

#     customers = []
#     ID = 0
#     testState = State(stateID)

#     for county in testState.counties.values():
#         # print("County ID {}, Area {}".format(county.id, county.area))
#         # c_count = max(4,county.pop_density)
#         c_division = {}
#         towerCount = sum([len(v) for k,v in county.basestations.items()])
#         for k,v in county.basestations.items():
#             if len(v)/towerCount > 0 and len(v)/towerCount < 1:
#                 c_division[k] = 1
#             else:
#                 c_division[k] = len(v)//towerCount
        
#         for k,v in c_division.items():
#             for i in range(0,v):
#                 c = Customer(ID, k, county, testState)
#                 ID += 1
#                 customers.append(c)

#     return customers


# def start(stateID, peering=False):

#     customers = initialize(stateID)

#     if(peering):
#         raise NotImplementedError
#     else:
#         for j in range(0,10):
#             for i,user in enumerate(customers):

#                 user.move()
#                 print((i/len(customers))*100, end='\r')
#             print(j,sum([user.CSAT["csat"] for user in customers])/len(customers))


# if __name__ == "__main__":
#     start(sys.argv[1])