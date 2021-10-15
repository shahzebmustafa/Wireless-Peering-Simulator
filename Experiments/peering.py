from modules.State import State
from modules.Customer import Customer
# from statistics import mean
import sys, json, math
import matplotlib.pyplot as plt
from itertools import combinations 
from modules.initialize import initialize
from modules.start import start


if __name__ == "__main__":

    stateID = "48"
    customers,state = initialize(stateID)
    cycleCount = 100

    ######################################################################################################
    ############################################# INDEPENDENT ############################################  

    no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)

    with open("./Tower Data/Results/no_peering_csats.json","w") as f:
        json.dump(no_peering_csats, f)

    plt.plot(range(0,cycleCount),no_peering_csats["AVG"],'--', label = "Average")
    plt.plot(range(0,cycleCount),no_peering_csats["SPRINT"], label="SPRINT")
    plt.plot(range(0,cycleCount),no_peering_csats["AT_T"], label="AT_T")
    plt.plot(range(0,cycleCount),no_peering_csats["VERIZON"], label="VERIZON")
    plt.plot(range(0,cycleCount),no_peering_csats["T_MOBILE"], label="T_MOBILE")
    plt.xlabel("Cycle")
    plt.ylabel("Customer Satisfaction (CSAT)")
    plt.legend()
    plt.title("Average CSAT without peering")
    plt.savefig("Tower Data/Results/Figs/no_peering.pdf")

    ######################################################################################################
    ############################################### PEERING ##############################################

    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    
    peering_combinations = combinations(carriers,2)


    for pair in peering_combinations:
        
        peering_csats = start(state=state, customers=customers, peering=pair, cycleCount=cycleCount)

        with open('Tower Data/Results/peering_{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
            json.dump(peering_csats, f)

    #     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
        plt.plot(range(0,cycleCount),peering_csats[pair[0]], label=pair[0], color='r')
        plt.plot(range(0,cycleCount),peering_csats[pair[1]], label=pair[1], color='b')
        plt.plot(range(0,cycleCount),no_peering_csats[pair[0]], "-.", color='r' )
        plt.plot(range(0,cycleCount),no_peering_csats[pair[1]], "-.", color='b')
    #     plt.ylim([0,1])
        plt.xlabel("Cycle")
        plt.ylabel("Customer Satisfaction (CSAT)")
        plt.legend()
        plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
        plt.savefig("Tower Data/Results/Figs/peering_{}_{}.pdf".format(pair[0],pair[1]))
        plt.show()
    #     break


    ######################################################################################################
    ############################################### ROAMING ##############################################

    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    roaming_combinations = combinations(carriers,2)


    for pair in roaming_combinations:
        
        roaming_csats = start(state=state, customers=customers, roaming=pair, cycleCount=cycleCount)

        with open('Tower Data/Results/roaming_{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
            json.dump(roaming_csats, f)


    #     plt.plot(range(0,100),peering_csats["AVG"],'--', label = "Average")
        plt.plot(range(0,cycleCount),roaming_csats[pair[0]], label=pair[0], color='r')
        plt.plot(range(0,cycleCount),roaming_csats[pair[1]], label=pair[1], color='b')
        plt.plot(range(0,cycleCount),no_peering_csats[pair[0]], "-.", color='r' )
        plt.plot(range(0,cycleCount),no_peering_csats[pair[1]], "-.", color='b')
    #     plt.ylim([0,1])
        plt.xlabel("Cycle")
        plt.ylabel("Customer Satisfaction (CSAT)")
        plt.legend()
        plt.title("Average CSAT with roaming ({},{})".format(pair[0],pair[1]))
        plt.savefig("Tower Data/Results/Figs/roaming_{}_{}.pdf".format(pair[0],pair[1]))
        plt.show()
    #     break    