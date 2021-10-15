from statistics import fmean
import sys, json, math
import matplotlib.pyplot as plt
from itertools import combinations


def peering(customers,state):
	print("here")

	with open("./Tower Data/Results/no_peering_csats.json","r") as f:
		no_peering_csats = json.load(f)

	carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
	peering_combinations = combinations(carriers,2)
	cycleCount = 100
	metric="csat"

	i =0 
	for pair in peering_combinations:
		peering_csats = start(state=state, customers=customers, peering=pair, cycleCount=cycleCount)


		with open('./Tower Data/Results/peering_{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
			json.dump(peering_csats, f)


		plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[0]]], label=pair[0], color='g')
		plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[1]]], "-.", label=pair[1], color='g')
		plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[0]]], color='r' )
		plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[1]]], "-.", color='r')
	#     plt.ylim([0,1])
		plt.legend()
		plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
		plt.savefig("./Tower Data/Results/Figs/peering_{}_{}.pdf".format(pair[0],pair[1]))
		plt.show()
		# break


def roaming(customers,state):
	print("here")

	with open("./Tower Data/Results/no_peering_csats.json","r") as f:
		no_peering_csats = json.load(f)

	carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
	# carriers = ['AT_T', 'VERIZON']
	roaming_combinations = combinations(carriers,2)
	cycleCount = 100
	metric="csat"
	i =0 
	for pair in roaming_combinations:
		roaming_csats = start(state=state, customers=customers, roaming=pair, cycleCount=cycleCount)

	#     printBaseStationConnections(state)

		with open('./Tower Data/Results/roaming_{}_{}.json'.format(pair[0],pair[1]), 'w') as f:
			json.dump(roaming_csats, f)

		plt.plot(range(0,cycleCount),[csat[metric] for csat in roaming_csats[pair[0]]], label=pair[0], color='g')
		plt.plot(range(0,cycleCount),[csat[metric] for csat in roaming_csats[pair[1]]], "-.", label=pair[1], color='g')
		plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[0]]], color='r' )
		plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[1]]], "-.", color='r')
	#     plt.ylim([0,1])
		plt.legend()
		plt.title("Average CSAT with roaming ({},{})".format(pair[0],pair[1]))
		plt.savefig("./Tower Data/Results/Figs/roaming_{}_{}.pdf".format(pair[0],pair[1]))
		plt.show()
		# break


if __name__ == '__main__':
	if __package__ is None:
		import sys
		from os import path
		sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
		from modules.State import State
		from modules.Customer import Customer
		from modules.start import start
		from modules.initialize import initialize
	else:
		from modules.State import State
		from modules.Customer import Customer
		from modules.start import start
		from modules.initialize import initialize

	customers,state = initialize("48",1000)		

	peering(customers,state)
	roaming(customers,state)

