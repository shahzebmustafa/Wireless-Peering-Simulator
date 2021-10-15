# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%

from modules.State import State
from modules.Customer import Customer
from statistics import mean
import sys, json, math
import matplotlib.pyplot as plt
from itertools import combinations
import cProfile
import pstats


# %%
def initialize(stateID, sampleSize=5000):

    customers = []
    ID = 0
    testState = State(stateID)

    statePopulation = sum([c.population for c in testState.counties.values()])
    for county in testState.counties.values():
        c_division = {}
        towerCount = sum([len(v) for v in county.basestations.values()])
        if (towerCount == 0):
            continue
        countyPop = max(100, sampleSize*(county.population/statePopulation))
        
        for k,v in county.basestations.items():
#             c_division[k] = int(countyPop*(len(v)/towerCount))
            c_division[k] = len(v)
        
        for k,v in c_division.items():

            for i in range(0,v):
                c = Customer(ID, k, county, testState)
                ID += 1
                customers.append(c)
    
    print(len(customers))
    return customers, testState


# %%

def start(state=None, customers=[], peering=False, roaming=False, cycleCount=100, single=False):
#     print(peering)
    
    csats = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
    csats_ = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
##################################################################################################################
#     csats["peering"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
#     csats["roaming"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}

#     csats_["peering"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
#     csats_["roaming"] = {"AVG":[], "T_MOBILE":[], "AT_T":[], "VERIZON":[], "SPRINT":[]}
##################################################################################################################    
    
    resetCustomerCSAT(customers)
    if(single):
        enablePeering_(state, peering[0],peering[1])
    elif(peering):
        enablePeering(state, peering[0],peering[1])
    elif(roaming):
        enableRoaming(state, roaming[0],roaming[1])

    metric = "csat"
##################################################################################################################
    # profile = cProfile.Profile()
    # profile.enable()
##################################################################################################################
    for j in range(0,cycleCount):
        for i,user in enumerate(customers):

            user.move()

        for user in customers:
            customerCSAT = {"csat":user.CSAT["csat"], "speed":user.CSAT["speed"], "signal":user.CSAT["signal"], "coverage":user.CSAT["coverage"]}
            csats_["AVG"].append(customerCSAT)
            csats_[user.carrier].append(customerCSAT)
##################################################################################################################            
#             customerCSAT = {"csat":user.CSAT["peering"]["csat"], "speed":user.CSAT["peering"]["speed"], "signal":user.CSAT["peering"]["signal"], "coverage":user.CSAT["peering"]["coverage"]}
#             csats_["peering"]["AVG"].append(customerCSAT)
#             csats_["peering"][user.carrier].append(customerCSAT)

#             customerCSAT = {"csat":user.CSAT["roaming"]["csat"], "speed":user.CSAT["roaming"]["speed"], "signal":user.CSAT["roaming"]["signal"], "coverage":user.CSAT["roaming"]["coverage"]}
#             csats_["roaming"]["AVG"].append(customerCSAT)
#             csats_["roaming"][user.carrier].append(customerCSAT)
##################################################################################################################        
        for k,v in csats_.items():
            if (k != "peering") and (k != "roaming"):
                try:
                    avgCSAT = {"csat":mean([u["csat"] for u in v]), "speed":mean([u["speed"] for u in v]), "signal":mean([u["signal"] for u in v]), "coverage":mean([u["coverage"] for u in v])}
                    csats[k].append(avgCSAT)
                except:
                    avgCSAT = {"csat":0, "speed":0, "signal":0, "coverage":0}
                    csats[k].append(avgCSAT)
##################################################################################################################                
#                 avgCSAT = {"csat":mean([u["csat"] for u in csats_["peering"][k]]), "speed":mean([u["speed"] for u in csats_["peering"][k]]), "signal":mean([u["signal"] for u in csats_["peering"][k]]), "coverage":mean([u["coverage"] for u in csats_["peering"][k]])}
#                 csats["peering"][k].append(avgCSAT)

#                 avgCSAT = {"csat":mean([u["csat"] for u in csats_["roaming"][k]]), "speed":mean([u["speed"] for u in csats_["roaming"][k]]), "signal":mean([u["signal"] for u in csats_["roaming"][k]]), "coverage":mean([u["coverage"] for u in csats_["roaming"][k]])}
#                 csats["roaming"][k].append(avgCSAT)
##################################################################################################################       
        # print(j+1,end='\r')

##################################################################################################################
    # profile.disable()
    # ps = pstats.Stats(profile)
    # ps.print_stats()
##################################################################################################################        

#     print("Total CSATs: \n    SPRINT: {}\n    VERIZON: {}\n    T-MOBILE: {}\n    AT&T: {}".format(mean(csats["SPRINT"]), mean(csats["VERIZON"]), mean(csats["T_MOBILE"]), mean(csats["AT_T"])))

    return csats


# %%
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



# def enablePeering(state, c1=None, c2=None):

#     peeringCounties = {c1:[], c2:[]}

#     for county in state.counties.values():

#         c1Coverage = county.coverageArea[c1]/county.area
#         c2Coverage = county.coverageArea[c2]/county.area

#         if (county.pop_density < 85) and (((c1Coverage<0.1) ^ (c2Coverage<0.1)) or ((c1Coverage<0.0) ^ (c2Coverage<0.0))):

    
#             if c1Coverage < c2Coverage:
#                 peeringCounties[c2].append(county)
#             else:
#                 peeringCounties[c1].append(county)

    
#     peeringCounties = acceptablePeering(peeringCounties, c1, c2)
    
#     for county in peeringCounties[c1]:
#         for bs in county.basestations[c1]:
#             bs.agreements.append(c2)
            
#     for county in peeringCounties[c2]:
#         for bs in county.basestations[c2]:
#             bs.agreements.append(c1)
def enablePeering(state, c1=None, c2=None):


    for county in state.counties.values():

        if (county.pop_density <= 200):
            for bs in county.basestations[c1]:
                bs.agreements.append(c2)

            for bs in county.basestations[c2]:
                bs.agreements.append(c1)


def enablePeering_(state, c1=None, c2=None):
    
    for county in state.counties.values():
        
        for bs in county.basestations[c1]:
            bs.agreements.append(c2)
            
        for bs in county.basestations[c2]:
            bs.agreements.append(c1)


# %%
def enableRoaming(state, c1, c2):

    roamingCounties = {c1:[], c2:[]}

    for county in state.counties.values():
        c1Coverage = county.coverageArea[c1]/county.area
        c2Coverage = county.coverageArea[c2]/county.area
        if (county.pop_density < 85) and ((c1Coverage==0) ^ (c2Coverage==0)):
#             print("Peering Possible")
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


# %%
def resetCustomerCSAT(customers):
    
    for c in customers:
        c.CSAT["csat"] = 1
        c.CSAT["weight"] = 1
        c.CSAT["speed"] = 1
        c.CSAT["coverage"] = 1
        c.CSAT["signal"] = 1


# %%
def getAvgCSAT(customers, carrier):
    avg = []
    for c in customers:
        if c.carrier == carrier:
            avg.append(c.CSAT["csat"])
    return round(sum(avg)/len(avg),2)


# %%
stateID = "48"
customers,state = initialize(stateID, 1000)


# %%

# import time
# s = time.time()
@profile
def profiler():
    print("No Peering.")

    cycleCount = 100
    metric = "csat"
    no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)
    colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}
    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']


    with open("./Tower Data/Results/no_peering_csats.json","w") as f:
        json.dump(no_peering_csats, f)


    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats["AVG"]],'--', label = "Average")
    for c in ['VERIZON']:
        
        # plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[c]], label=c, color=colors[c])
        plt.plot(range(0,cycleCount),[csat['speed'] for csat in no_peering_csats[c]], label=c+'_speed')
        plt.plot(range(0,cycleCount),[csat['coverage'] for csat in no_peering_csats[c]], label=c+'_cov')
        plt.plot(range(0,cycleCount),[csat['signal'] for csat in no_peering_csats[c]], label=c+'sig')
        

    plt.legend()
    plt.title("Average CSAT without peering")
    plt.savefig("Tower Data/Results/Figs/no_peering.pdf")
    plt.show()
# print(time.time()-s)
profiler()


# %%
get_ipython().system('python -m memory_profiler memory.py')


# %%

carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
# carriers = ['AT_T', 'VERIZON']
peering_combinations = combinations(carriers,2)
cycleCount = 100
metric="coverage"

for pair in peering_combinations:
    
    peering_csats = start(state=state, customers=customers, peering=pair, cycleCount=cycleCount)

    with open('Tower Data/Results/peering_{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
        json.dump(peering_csats, f)


    print("Average CSATs with peering ({}, {}):".format(pair[0],pair[1]))
    print("{}: \t{}".format(pair[0],getAvgCSAT(customers,pair[0])))
    print("{}: \t{}\n\n".format(pair[1],getAvgCSAT(customers,pair[1])))


#     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[0]]], label=pair[0], color='r')
    plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[1]]], label=pair[1], color='b')
    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[0]]], "-.", color='r' )
    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[1]]], "-.", color='b')
#     plt.ylim([0,1])
    plt.legend()
    plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
    plt.savefig("Tower Data/Results/Figs/peering_{}_{}.pdf".format(pair[0],pair[1]))
    plt.show()
    # break


# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%


# %% [markdown]
# # ----------------

# %%
stateID = "48"
customers,state = initialize(stateID)
cycleCount = 100
print("Sample Size: ",len(customers))
potential_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)
metric = "csat"

with open("./Tower Data/Results/potential_peering_csats.json","w") as f:
    json.dump(potential_peering_csats, f)
    
font = {'family' : 'sans-serif',
        'weight' : 'light',
        'size'   : 12}
import matplotlib
matplotlib.rc('font', **font)

carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}

for c in carriers:
    plt.plot(range(0,cycleCount),[csat[metric] for csat in potential_peering_csats[c]] ,label="Independent", color='k', linewidth=3)
    plt.plot(range(0,cycleCount),[csat[metric] for csat in potential_peering_csats["peering"][c]], '--' ,label="Peering", color='dodgerblue', linewidth=3)
    plt.plot(range(0,cycleCount),[csat[metric] for csat in potential_peering_csats["roaming"][c]], '--' ,label="Roaming", color='orange', linewidth=3)
    plt.title("Peering vs. Roaming - {}".format(c))
    plt.legend()
    plt.ylabel("Customer Satisfaction (CSAT)")
    plt.xlabel("Movement")
    
    plt.savefig("./Tower Data/Results/Figs/potential_{}.pdf".format(c))
    plt.show()


# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%
def createCustomers(state, county):
    customers = []
    c_division = {}
    ID = 1
    towerCount = sum([len(v) for v in county.basestations.values()])
    if (towerCount == 0):
        return []


    for k,v in county.basestations.items():
        c_division[k] = len(v)

    for k,v in c_division.items():
        for i in range(0,v):
            c = Customer(ID, k, county, state)
            ID += 1
            customers.append(c)
    return customers


# %%
stateID = "48"
state = State(stateID)


# %%

carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
carrier_combinations = combinations(carriers,2)
cycleCount = 100
metric = "csat"
# i = 5
totalCounties = len(list(state.allCounties.keys()))
for pair in carrier_combinations:
    if set(pair) != set(("VERIZON","AT_T")):
        print('\n',pair)
        benefit = {pair[0]: [], pair[1]: []}
        i = 1
        for county in state.allCounties.values():

            state.counties = {county.id:county}


            customers = createCustomers(state, county)

            no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)
    #         print('\n')
            peering_csats = start(state=state, customers=customers, peering=pair, cycleCount=cycleCount, single=True)

            benefit[pair[0]].append({"county":county.id, "benefit": peering_csats[pair[0]][-1][metric]-no_peering_csats[pair[0]][-1][metric], "peering":False})
            benefit[pair[1]].append({"county":county.id, "benefit": peering_csats[pair[1]][-1][metric]-no_peering_csats[pair[1]][-1][metric], "peering":False})
            print(int((i/totalCounties)*100),"%",end='\r')
            i += 1
    #         i -= 1
    #         if not i:
    #             break        

        with open('Tower Data/Results/benefit_{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
            json.dump(benefit, f)
    #     break


# %%
def plotCummGraph(cBenefitsA, cBenefitsB, contracts, pair):
    x = [0]
    x_ = [len(c) for c in contracts]
    for point in x_:
        x.append(x[-1]+point)
    print(x)
    plt.plot(x, cBenefitsA, label=pair[0], linewidth=3)
    plt.plot(x, cBenefitsB, label=pair[1], linewidth=3)
#     plt.xticks(range(0,x[-1]+1))
    plt.ylabel("Cummulative CSAT")
    plt.xlabel("Peering Counties")
    plt.legend()
    plt.title("Peering Location CSAT ({}, {})".format(pair[0],pair[1]))
    plt.savefig("Tower Data/Results/Benefits/benefit_{}_{}.pdf".format(pair[0],pair[1]))
    plt.show()


# %%
def setPeeringTrue(lst, county):
    for item in lst:
        if item["county"] == county:
            item["peering"] = True
            return item["benefit"]


# %%
import matplotlib

font = {'family' : 'sans-serif',
        'weight' : 'light',
        'size'   : 12}
matplotlib.rc('font', **font)

carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
carrier_combinations = combinations(carriers,2)

for pair in carrier_combinations:
    
    benefits = {}
    with open('Tower Data/Results/Benefits/benefit_{}_{}.json'.format(pair[0],pair[1])) as f:
        
        benefits = json.load(f)
        
    
    benefits[pair[0]] = sorted(benefits[pair[0]], key = lambda i: i['benefit'], reverse=True)
    benefits[pair[1]] = sorted(benefits[pair[1]], key = lambda i: i['benefit'], reverse=True)
    
    i = 0
    j = 0
    cBenefitsA = [0]
    cBenefitsB = [0]
    contracts = []
    
    while i<len(benefits[pair[0]]) and j <len(benefits[pair[1]]):
        
        agreementCounties = []
        while i < len(benefits[pair[0]]) and benefits[pair[0]][i]['peering'] :
            i += 1
        
        if i >= len(benefits[pair[0]]):
            break
        agreementCounties.append(benefits[pair[0]][i]['county'])
        benefits[pair[0]][i]['peering'] = True
        aGain = benefits[pair[0]][i]['benefit']
        bGain = setPeeringTrue(benefits[pair[1]], benefits[pair[0]][i]['county'])
#         print("{} choosing {} county for {} gain.".format(pair[0], benefits[pair[0]][i]['county'], aGain))
#         print("{} has to peer in {} county for {} gain".format(pair[1], benefits[pair[0]][i]['county'], bGain))
#         benefits[pair[1]][benefits[pair[0]][i]['county']]['peering'] = True
        
        if i==j and benefits[pair[1]][i]['peering']:
            
            cBenefitsA.append(cBenefitsA[-1]+aGain)
            cBenefitsB.append(cBenefitsB[-1]+bGain)
            j += 1
        else:
            while j < len(benefits[pair[1]]) and benefits[pair[1]][j]['peering']:
                j += 1
            
            if j >= len(benefits[pair[1]]):
                break
            
            agreementCounties.append(benefits[pair[1]][j]['county'])
            benefits[pair[1]][j]['peering'] = True
            aGain += setPeeringTrue(benefits[pair[0]], benefits[pair[1]][j]['county'])
            bGain += benefits[pair[1]][j]['benefit']
#             print("{} choosing {} county for {} gain.".format(pair[1], benefits[pair[1]][j]['county'], bGain))
#             print("{} has to peer in {} county for {} gain".format(pair[0], benefits[pair[1]][j]['county'], aGain))
#             benefits[pair[0]][benefits[pair[1]][j]]['peering'] = True
            
            cBenefitsA.append(cBenefitsA[-1] + aGain)
            cBenefitsB.append(cBenefitsB[-1] + bGain)
        
        contracts.append(agreementCounties)
    print(cBenefitsA, cBenefitsB)
    plotCummGraph(cBenefitsA, cBenefitsB, contracts, pair)
    break
        
            
        
        


# %%
tempList = ([asdf['benefit'] for asdf in benefits[pair[0]]])
a = 0
s = 0
while tempList[a] >= 0:
    s += tempList[a]
    a += 1
print(tempList)
print(s)
print(sum(tempList))

# %% [markdown]
# # ----------------

# %%
# def initialize(stateID):

#     customers = []
#     ID = 0
#     testState = State(stateID)

#     sampleSize = 5000
#     statePopulation = sum([c.population for c in testState.counties.values()])
#     for county in testState.counties.values():
#         c_division = {}
#         towerCount = sum([len(v) for v in county.basestations.values()])
#         if (towerCount == 0):
#             continue
#         countyPop = max(100, sampleSize*(county.population/statePopulation))
        
#         for k,v in county.basestations.items():
#             c_division[k] = int(countyPop*(len(v)/towerCount))
        
#         for k,v in c_division.items():

#             for i in range(0,v):
#                 c = Customer(ID, k, county, testState)
#                 ID += 1
#                 customers.append(c)
    
#     return customers, testState

# print("No Peering.")
# stateID = "48"
# customers,state = initialize(stateID)
# cycleCount = 100

# no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)

# with open("./Tower Data/Results/no_peering_csats.json","w") as f:
#     json.dump(no_peering_csats, f)
metric = "csat"
colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}
carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']

plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats["AVG"]],'--', label = "Average")
for c in carriers:
    
    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[c]], label=c, color=colors[c])

plt.legend()
plt.title("Average CSAT without peering")
plt.savefig("Tower Data/Results/Figs/no_peering.pdf")
plt.show()


# %%



# %%



# %%

carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
carriers = ['AT_T', 'VERIZON'] #temp
peering_combinations = combinations(carriers,2)


for pair in peering_combinations:
    
    peering_csats = start(state=state, customers=customers, peering=pair, cycleCount=cycleCount)

    with open('Tower Data/Results/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
        json.dump(peering_csats, f)


    print("Average CSATs with peering ({}, {}):".format(pair[0],pair[1]))
    print("{}: \t{}".format(pair[0],getAvgCSAT(customers,pair[0])))
    print("{}: \t{}\n\n".format(pair[1],getAvgCSAT(customers,pair[1])))


#     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,cycleCount),peering_csats[pair[0]], label=pair[0], color='r')
    plt.plot(range(0,cycleCount),peering_csats[pair[1]], label=pair[1], color='b')
    plt.plot(range(0,cycleCount),no_peering_csats[pair[0]], "-.", color='r' )
    plt.plot(range(0,cycleCount),no_peering_csats[pair[1]], "-.", color='b')
#     plt.ylim([0,1])
    plt.legend()
    plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
    plt.savefig("Tower Data/Results/Figs/peering_{}_{}.pdf".format(pair[0],pair[1]))
    plt.show()
#     break


# %%
stateID = "48"
customers,state = initialize(stateID)

print("No Peering.")

cycleCount = 100
no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)

with open("./Tower Data/Results/no_peering_csats.json","w") as f:
    json.dump(no_peering_csats, f)


# %%
carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
roaming_combinations = combinations(carriers,2)


for pair in roaming_combinations:
    
    roaming_csats = start(state=state, customers=customers, roaming=pair, cycleCount=cycleCount)

    with open('Tower Data/Results/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
        json.dump(roaming_csats, f)


    print("Average CSATs with peering ({}, {}):".format(pair[0],pair[1]))
    print("{}: \t{}".format(pair[0],getAvgCSAT(customers,pair[0])))
    print("{}: \t{}\n\n".format(pair[1],getAvgCSAT(customers,pair[1])))


#     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,cycleCount),roaming_csats[pair[0]], label=pair[0], color='r')
    plt.plot(range(0,cycleCount),roaming_csats[pair[1]], label=pair[1], color='b')
    plt.plot(range(0,cycleCount),no_peering_csats[pair[0]], "-.", color='r' )
    plt.plot(range(0,cycleCount),no_peering_csats[pair[1]], "-.", color='b')
#     plt.ylim([0,1])
    plt.legend()
    plt.title("Average CSAT with roaming ({},{})".format(pair[0],pair[1]))
    plt.savefig("Tower Data/Results/Figs/roaming_{}_{}.pdf".format(pair[0],pair[1]))
    plt.show()
#     break


# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%
print("Peering between At&t and Sprint")
peering_csat = start(state, customers, peering=p)

with open("./Tower Data/Results/peering_csats_att_sprint.json","w") as f:
    json.dump(peering_csats)


# %%
print("Average CSATs with peering (AT_T, SPRINT):")
print("AT_T\t",getAvgCSAT(customers,"AT_T"))
print("SPRINT\t",getAvgCSAT(customers,"SPRINT"))


# %%
print("Peering between At&t and Sprint")
peering_csat = start(state, customers, peering=p)

with open("./Tower Data/Results/peering_csats_att_sprint.json","w") as f:
    json.dump(peering_csats)


# %%



# %%
print("CSATs without peering:")
print("AT_T",getAvgCSAT(customers,"AT_T"))
print("VERIZON",getAvgCSAT(customers,"VERIZON"))
print("T_MOBILE",getAvgCSAT(customers,"T_MOBILE"))
print("SPRINT",getAvgCSAT(customers,"SPRINT"))


# %%
p = ["SPRINT", "AT_T"]
start(state, customers, peering=p)


# %%
print("CSATs with peering: ",p)
print("AT_T",getAvgCSAT(customers,"AT_T"))
print("VERIZON",getAvgCSAT(customers,"VERIZON"))
print("T_MOBILE",getAvgCSAT(customers,"T_MOBILE"))
print("SPRINT",getAvgCSAT(customers,"SPRINT"))


# %%
print(customers[0].county.coverageArea)
print(customers[0].county.area)
print([x.location for x in customers[0].county.basestations["SPRINT"]])
print(len(customers))
for c in customers:
    print(c.coverage,c.carrier)


# %%
# p = ["AT_T","SPRINT"]
# start(state, customers,peering=p)


# %%
# print(len(customers))
# for c in customers:
#     print(c.CSAT["csat"],c.carrier)


# %%



# %%



# %%



# %%



# %%



# %%
print(len(customers))
for c in customers:
    print(c.CSAT["csat"])


# %%



# %%
p = ["AT_T","SPRINT"]
start(state, customers,peering=p)


# %%
csat = []
for c in customers:
    if c.carrier in p:
        csat.append(c.CSAT["csat"])
print(sum(csat)/len(csat))


# %%
start(state, customers)


# %%
csat = []
for c in customers:
    if c.carrier in p:
        csat.append(c.CSAT["csat"])
print(sum(csat)/len(csat))


# %%
for c in customers:
    print(c.speed)


# %%
import matplotlib.pyplot as plt
from shapely.geometry import asShape, MultiPoint, Polygon, mapping
from geojson import Polygon as Polygon2
from area import area
import numpy, math




def bsLocations(bsList):
        locations = []
        for bs in bsList:
            locations.append(bs.location)
        return locations

def areaFor2Points(p1, p2):
    earthRadious = 3959
    dlat = numpy.deg2rad(p2[1] - p1[1])
    dlong = numpy.deg2rad(p2[0] - p1[0])
    a = (numpy.sin(dlat / 2)) ** 2 + numpy.cos(numpy.deg2rad(p1[1])) * numpy.cos(numpy.deg2rad(p2[1])) * ((numpy.sin(dlong / 2)) ** 2)
    b = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1 - a))
    b *= earthRadious
    b /= 2

    p = b*math.tan(math.radians(22.5))

    return 2*(p*b)

def getCoverageArea(county):
    cArea = {}
    for k,v in county.basestations.items():
        if(len(v) < 3):
            print([asdf.location for asdf in v])
            cArea[k] = [[x[0] for x in county.bsLocations(v)], [x[1] for x in county.bsLocations(v)]]
        else:
            print(k,bsLocations(v))
            cArea[k] = MultiPoint(county.bsLocations(v)).convex_hull


#     print (cArea)
    return cArea





tc = 40
x,y = asShape(customers[tc].county.geometry).exterior.xy
print(customers[tc].county.coverageArea)
plt.plot(x,y,'--')
# print(x,max(y))
for k,v in getCoverageArea(customers[tc].county).items():
#     print(v.exterior.xy)
    try:
#         print(v)
#         if(k!="SPRINT"):
        x_,y_ = v.exterior.xy

#             print(x_,y_)

        plt.plot(x_,y_,label=k, marker='x')
        plt.legend()
#         a = mapping(v)
#         print(k,area(a)/2590000)
    except Exception as e:
        plt.plot(v[0],v[1], label=k, marker = 'o')
        plt.legend()
    
print(customers[tc].county.area)
print(customers[tc].county.id)


# %%
print("AT_T",getAvgCSAT(customers,"AT_T"))
print("VERIZON",getAvgCSAT(customers,"VERIZON"))
print("T_MOBILE",getAvgCSAT(customers,"T_MOBILE"))
print("SPRINT",getAvgCSAT(customers,"SPRINT"))


# %%



