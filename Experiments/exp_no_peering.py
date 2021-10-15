#!/wpeering/bin/python

import time
from modules.start import start
from modules.initialize import initialize
import matplotlib.pyplot as plt
import json

def exp_no_peering(stateID='48', customerCount=1000):
    customers,state = initialize(stateID, customerCount)

    s = time.time()

    cycleCount = 100
    metric = "csat"

    no_peering_csats = start(state=state, customers=customers, cycleCount=cycleCount)
    colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}
    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']


    with open("./Tower Data/Results/no_peering_csats.json","w") as f:
        json.dump(no_peering_csats, f)


    plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats["AVG"]],'--', label = "Average")
    for c in carriers:

        plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[c]], label=c, color=colors[c])

    plt.legend()
    plt.title("Average CSAT without peering")
    plt.savefig("Tower Data/Results/Figs/no_peering.pdf")
    plt.show()

    return customers, state, no_peering_csats
