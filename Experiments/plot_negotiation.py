import matplotlib
import matplotlib.pyplot as plt
from itertools import combinations
import json
font = {'family' : 'sans-serif',
        'weight' : 'light',
        'size'   : 12}
matplotlib.rc('font', **font)


def plotCummGraph(cBenefitsA, cBenefitsB, contracts, pair):
    x = [0]
    x_ = [len(c) for c in contracts]
    for point in x_:
        x.append(x[-1]+point)

    plt.plot(x, cBenefitsA, label=pair[0])
    plt.plot(x, cBenefitsB, label=pair[1])

    plt.ylabel("Cummulative CSAT")
    plt.xlabel("Peering Counties")
    plt.legend()
    plt.title("Peering Location CSAT ({}, {})".format(pair[0],pair[1]))
    # plt.savefig("Tower Data/Results/Benefits/NEWbenefit_{}_{}.pdf".format(pair[0],pair[1]))
    plt.show()


def setPeeringTrue(lst, county):
    for item in lst:
        if item["county"] == county:
            item["peering"] = True
            return item['benefit_']


if __name__ == "__main__":


    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)

    for pair in carrier_combinations:
        
        benefits = {}
        with open('Tower Data/Results/Benefits/trybenefit_{}_{}.json'.format(pair[0],pair[1]), 'r') as f:
            
            benefits = json.load(f)
            
        for i in range(0,len(benefits[pair[0]])):
            benefits[pair[0]][i]["benefit_"] = (benefits[pair[0]][i]["after"] - benefits[pair[0]][i]["before"])/(1-benefits[pair[0]][i]["after"])
        for i in range(0,len(benefits[pair[1]])):
            benefits[pair[1]][i]["benefit_"] = (benefits[pair[1]][i]["after"] - benefits[pair[1]][i]["before"])/(1-benefits[pair[1]][i]["after"])    

        with open('Tower Data/Results/Benefits/NEWTESTbenefit_{}_{}.json'.format(pair[0],pair[1]),"w") as f:
            
            json.dump(benefits,f)

        benefits[pair[0]] = sorted(benefits[pair[0]], key = lambda i: i['benefit_'], reverse=True)
        benefits[pair[1]] = sorted(benefits[pair[1]], key = lambda i: i['benefit_'], reverse=True)
        
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
            aGain = benefits[pair[0]][i]['benefit_']
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
                bGain += benefits[pair[1]][j]['benefit_']
    #             print("{} choosing {} county for {} gain.".format(pair[1], benefits[pair[1]][j]['county'], bGain))
    #             print("{} has to peer in {} county for {} gain".format(pair[0], benefits[pair[1]][j]['county'], aGain))
    #             benefits[pair[0]][benefits[pair[1]][j]]['peering'] = True
                
                cBenefitsA.append(cBenefitsA[-1] + aGain)
                cBenefitsB.append(cBenefitsB[-1] + bGain)
            
            contracts.append(agreementCounties)
        # print(cBenefitsA, cBenefitsB)
        plotCummGraph(cBenefitsA, cBenefitsB, contracts, pair)
    