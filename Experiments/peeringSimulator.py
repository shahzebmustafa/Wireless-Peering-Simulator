if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from modules.State import State
from modules.Customer import Customer
from modules.start import start
from modules.initialize import initialize

import os.path
from statistics import fmean
import sys, json, math
import matplotlib.pyplot as plt
from itertools import combinations
import time
import numpy as np



def noPeeringSimulator(customers, state, jsonName="Simulator/no_peering_csats",figName="Simulator/no_peering_csats", drawFig=True):

    cycleCount = 100
    metric = "csat"
    no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)

    colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}
    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']


    with open("./Results/{}.json".format(jsonName),"w") as f:
        json.dump(no_peering_csats, f)

    if drawFig:
        for c in carriers:

            plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[c]], label=c, color=colors[c])

        plt.legend()
        plt.title("Average CSAT without peering")
        plt.savefig("./Results/Figs/{}.pdf".format(figName))
        plt.close()


def peeringSimulator(customers, state, pair, jsonName="Simulator/Peering/", figName="Simulator/Peering/", drawFig=True, heuristic=0):

    with open("./Results/Simulator/no_peering_csats.json","r") as f:
        no_peering_csats = json.load(f)


    
    cycleCount = 100
    metric="csat"

    peering_csats = start(state=state, customers=customers, peering=pair, cycleCount=cycleCount, heuristic=heuristic)



    with open('./Results/{}{}_{}.json'.format(jsonName,pair[0],pair[1]), 'w') as f:
        json.dump(peering_csats, f)

    if drawFig:

        plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[0]]], label=pair[0], color='g')
        plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[1]]], "-.", label=pair[1], color='g')
        plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[0]]], color='r' )
        plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[1]]], "-.", color='r')

        plt.legend()
        plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
        plt.savefig("./Results/Figs/{}{}_{}.pdf".format(figName,pair[0],pair[1]))

        plt.close()



def roamingSimulator(customers, state, pair):
    with open("./Results/Simulator/no_peering_csats.json","r") as f:
        no_peering_csats = json.load(f)

    cycleCount = 100
    metric="csat"
        
    roaming_csats = start(state=state, customers=customers, roaming=pair, cycleCount=cycleCount)

    with open('./Results/Simulator/Roaming/{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
        json.dump(roaming_csats, f)



    plt.plot(range(0,cycleCount),[csat[metric] for csat in roaming_csats[pair[0]]], label=pair[0], color='g')
    plt.plot(range(0,cycleCount),[csat[metric] for csat in roaming_csats[pair[1]]], "-.", label=pair[1], color='g')
    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[0]]], color='r' )
    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[1]]], "-.", color='r')

    plt.legend()
    plt.title("Average CSAT with roaming ({},{})".format(pair[0],pair[1]))
    plt.savefig("./Results/Figs/Simulator/Roaming/{}_{}.pdf".format(pair[0],pair[1]))




def runSimulator(state, customers, mode, pair=None, threshold = 0):
        
    if mode == "No Peering":
        print("Starting NO PEERING Simulation")
        jn = "Simulator/no_peering_csats"
        noPeeringSimulator(customers, state, jsonName=jn, figName=jn, drawFig=True)
    
    elif mode == "Roaming":
        print("Startubg Roaming Simulation")
        roamingSimulator(customers, state, pair)
    
    elif mode == "Peering":
        print("Pair: ", pair)
        print("\tStarting Peering Simulation: Sorted Sum")
        jn = "Simulator/Sorted Sum/"
        peeringSimulator(customers, state, pair, jsonName=jn, figName=jn, drawFig=True, heuristic=0)


        print(f"\tStarting Peering Simulation: Threshold ({threshold})")
        jn = "Simulator/Threshold/"
        pops = [x.pop_density for x in list(state.counties.values())]
        threshold = np.percentile(pops, threshold)
        peeringSimulator(customers, state, pair, jsonName=jn, figName=jn, drawFig=True, heuristic=threshold)


        



# if __name__ == "__main__":
    # if(len(sys.argv) == 1):
    #     stateID = "48"
    #     customers,state = initialize(stateID)
    #     if not os.path.isfile("./Tower Data/Results/Simulator/no_peering_csats.json"):
    #         noPeeringSimulator(customers, state)
    #     peeringSimulator(customers, state)
    # else:
    #     # print(sys.argv)
    #     customers,state = initialize(sys.argv[1],sampleSize=int(sys.argv[2]))
    #     # print(len(customers))
    #     pops = [x.pop_density for x in list(state.counties.values())]
    #     threshold = np.percentile(pops, int(sys.argv[3]))
    #     if not os.path.isfile("./Tower Data/Results/Experiments/no_peering_csats.json"):
    #         noPeeringSimulator(customers, state, jsonName="Experiments/Threshold/no_peering_csats", drawFig=False)

    #     peeringSimulator(customers, state, jsonName="Experiments/Threshold/test_peering_csats", drawFigs=False, heuristic=threshold)