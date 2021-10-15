import json
from itertools import combinations


def peering_CSAT(cycleCount=100, metric="csat"):
	# colors = {"SPRINT":'gold', "VERIZON":'#0099FF', "T_MOBILE":'#EB70AA', "AT_T":'k'}
	carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
	no_peering_csats = dict()
	peering_csats = dict()
	# peering_combinations = combinations(carriers,2)
	peering_combinations = [('VERIZON','AT_T'),('T_MOBILE','SPRINT')]
	xs = []
	ys = []
	labels = []


	with open("../Tower Data/Results/no_peering_csats.json","r") as f:
	    no_peering_csats = json.load(f)


	for pair in peering_combinations:

		with open("../Tower Data/Results/peering_{}_{}.json".format(pair[0],pair[1]),"r") as f:
			peering_csats = json.load(f)
		xs = []
		ys = []

		xs.append(list(range(0,cycleCount)))
		ys.append([csat[metric] for csat in peering_csats[pair[0]]])
		labels.append(pair[0])

		xs.append(list(range(0,cycleCount)))
		ys.append([csat[metric] for csat in peering_csats[pair[1]]])
		labels.append(pair[1])

		xs.append(list(range(0,cycleCount)))
		ys.append([csat[metric] for csat in no_peering_csats[pair[0]]])
		labels.append(pair[0])

		xs.append(list(range(0,cycleCount)))
		ys.append([csat[metric] for csat in no_peering_csats[pair[1]]])
		labels.append(pair[1])

		# print(xs, ys)
		lineGraph(xs, ys, labels=labels, show=True, title="{} - {}".format(pair[0],pair[1]))

	    # plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[0]]], label=pair[0], color='g')
	    # plt.plot(range(0,cycleCount),[csat[metric] for csat in peering_csats[pair[1]]], "-.", label=pair[1], color='g')
	    # plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[0]]], color='r' )
	    # plt.plot(range(0,cycleCount),[csat[metric] for csat in no_peering_csats[pair[1]]], "-.", color='r')
	#     plt.ylim([0,1])
	    # plt.legend()
	    # plt.title("Average CSAT with peering ({},{})".format(pair[0],pair[1]))
	    # plt.savefig("Tower Data/Results/Figs/peering_{}_{}.pdf".format(pair[0],pair[1]))
	    # plt.show()
	    # break

if __name__ == '__main__':
	if __package__ is None:
		import sys
		from os import path
		sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
		from plot import lineGraph
	else:
		from ..plot import lineGraph

	peering_CSAT(metric="coverage")






