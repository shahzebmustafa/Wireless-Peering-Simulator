if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from statistics import mean
from statistics import fmean

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

def enablePeering(state, counties, c1, c2):

    for county in counties:

        for bs in state.counties[str(county)].basestations[c1]:
            bs.agreements.append(c2)

        for bs in state.counties[str(county)].basestations[c2]:
            bs.agreements.append(c1)


#     for county in state.counties.values():

#         # if forcePeering or (county.pop_density <= 200 and county.pop_density >= 20):
#         cd = abs(county.coverageArea[c1]-county.coverageArea[c2])
#         if forcePeering or (cd <= 0.3):
# #             if round(county.coverageArea[c1],1) != round(county.coverageArea[c2],1):
#             for bs in county.basestations[c1]:
#                 bs.agreements.append(c2)

#             for bs in county.basestations[c2]:
#                 bs.agreements.append(c1)




def enableRoaming(state, c1, c2):

    roamingCounties = {c1:[], c2:[]}

    for county in state.counties.values():
        c1Coverage = county.coverageArea[c1]/county.area
        c2Coverage = county.coverageArea[c2]/county.area
#         if (county.pop_density < 85) and ((c1Coverage==0) ^ (c2Coverage==0)):
        if (county.pop_density < 200):
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





def resetCustomerCSAT(customers):
    
    for c in customers:
        c.CSAT["csat"] = 0.5
        c.CSAT["weight"] = 0.5
        c.CSAT["speed"] = 0.5
        c.CSAT["coverage"] = 0.5
        c.CSAT["signal"] = 0.5

def getAvgCSAT(customers, carrier):
    avg = []
    for c in customers:
        if c.carrier == carrier:
            avg.append(c.CSAT["csat"])
    return round(sum(avg)/len(avg),2)


def printBaseStationConnections(state):
    for county in state.counties.values():
        print("County:",county.id)
        for k,v in county.basestations.items():
            print(k)
            print([len(bs.customers) for bs in v])

def getPeeringCounties(state, peering, heuristic, forcePeering):

    if forcePeering:
        return [x.id for x in list(state.counties.values())]

    selectedCounties = []

    if heuristic==0:
        from modules.sortedSum import maxSumProd
        return maxSumProd(peering)
    else:

        for county in state.counties.values():
            if (county.pop_density <= heuristic):
                selectedCounties.append(county.id)

        return selectedCounties

def start(state=None, customers=[], peering=False, roaming=False, cycleCount=100, forcePeering=False, heuristic=0):
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
    # if(forcePeering):
    #     enablePeering_(state, peering[0],peering[1])
    if(peering):
        selectedCounties = getPeeringCounties(state, peering, heuristic, forcePeering)
        enablePeering(state, selectedCounties, peering[0], peering[1])
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
                    avgCSAT = {"csat":fmean([u["csat"] for u in v]), "speed":fmean([u["speed"] for u in v]), "signal":fmean([u["signal"] for u in v]), "coverage":fmean([u["coverage"] for u in v])}
                    csats[k].append(avgCSAT)
                except:
                    avgCSAT = {"csat":0, "speed":0, "signal":0, "coverage":0}
                    csats[k].append(avgCSAT)
##################################################################################################################                
#                 avgCSAT = {"csat":fmean([u["csat"] for u in csats_["peering"][k]]), "speed":fmean([u["speed"] for u in csats_["peering"][k]]), "signal":fmean([u["signal"] for u in csats_["peering"][k]]), "coverage":fmean([u["coverage"] for u in csats_["peering"][k]])}
#                 csats["peering"][k].append(avgCSAT)

#                 avgCSAT = {"csat":fmean([u["csat"] for u in csats_["roaming"][k]]), "speed":fmean([u["speed"] for u in csats_["roaming"][k]]), "signal":fmean([u["signal"] for u in csats_["roaming"][k]]), "coverage":fmean([u["coverage"] for u in csats_["roaming"][k]])}
#                 csats["roaming"][k].append(avgCSAT)
##################################################################################################################       
        # print(j+1,end='\r')

##################################################################################################################
    # profile.disable()
    # ps = pstats.Stats(profile)
    # ps.print_stats()
##################################################################################################################        

#     print("Total CSATs: \n    SPRINT: {}\n    VERIZON: {}\n    T-MOBILE: {}\n    AT&T: {}".format(fmean(csats["SPRINT"]), fmean(csats["VERIZON"]), fmean(csats["T_MOBILE"]), mean(csats["AT_T"])))
    return csats

