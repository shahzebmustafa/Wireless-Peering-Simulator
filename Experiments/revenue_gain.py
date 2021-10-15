import json
import math
import matplotlib.pyplot as plt
from itertools import combinations
import copy

def gain(x,y, g):

	customers = 29005
	w1 = 1 / (1 + math.exp(-g*(x-0.5)))
	c = 100
	r1 = w1*c*customers
	w2 = (1 / (1 + math.exp(-g*(y-0.5))))
	r2 = w2 * c * customers
	# print(x, y, w1, w2)
	return ((r2-r1)/r1)*100.0

def getRevenueGains(CSATs,peering1CSATs, peering2CSATs,roamingCSATs, c_, l):


	carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
	labels = ['Verizon', 'T-Mobile', 'Sprint', 'At&t']

	results = {}

	# for i, c_ in enumerate(carriers):
	for j,c in enumerate(carriers):
		ys = []
		if c_ != c:
			for g in range(0,100):
				# print(g)
				ys.append([gain(CSATs[c_],roamingCSATs[c][c_], g) , gain(CSATs[c_],peering1CSATs[c][c_], g), gain(CSATs[c_],peering2CSATs[c][c_], g)])
				# print(ys[-1])
			results[(l,labels[j])] = copy.deepcopy(ys)
	return results

		

def plotRevenueGain(CSATs,peering1CSATs, peering2CSATs,roamingCSATs, g):

	'''
	CSATs data format: {carrier:int}
	peeringCSATs data format: {carrier1:{carrier2:int}}
	roamingCSATs data format: {carrier1:{carrier2:int}}
	'''

	carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']


	xticks = ['Verizon', 'T-Mobile', 'Sprint', 'At&t']

	for i,c_ in enumerate(carriers):
		ys = []
		fname = "./Results/Figs/Simulator/rev_{}.pdf".format(c_)
		for c in carriers:
			if c_ != c:
				# print(c,c_)
				ys.append([gain(CSATs[c_],roamingCSATs[c][c_], g) , gain(CSATs[c_],peering1CSATs[c][c_], g), gain(CSATs[c_],peering2CSATs[c][c_], g)])
				# print("\n")

		barGraph(
			ys,
			title="{} Revenue Gain Comparison".format(xticks[i]), 
			xlabel="", 
			ylabel="Net Revenue Gain (%)",
			xticks=xticks[:i] + xticks[i+1 :], 
			labels=["Roaming", "Peering (T)", "Peering (SS)"], 
			fname=fname, 
			show=False)



def getCSATs():
	# Reading CSATs:
	CSATs = dict()
	roamingCSATs = dict()
	peering1CSATs = dict()
	peering2CSATs = dict()
	carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
	carrier_combinations = combinations(carriers,2)

	with open("./Results/Simulator/no_peering_csats.json", "r") as f:
		CSATs = json.load(f)
		for c in carriers:
			CSATs[c] = CSATs[c][-1]["csat"]

	for pair in carrier_combinations:

			# try:
			with open("./Results/Simulator/Roaming/{}_{}.json".format(pair[0],pair[1]),"r") as f:
				# except:
				# 	f = open("./Results/Simulator/Roaming/{}_{}.json".format(pair[1],pair[0]),"r")
				data = json.load(f)
				data1 = data[pair[1]][-1]["csat"]
				data = data[pair[0]][-1]["csat"]

				if(roamingCSATs.get(pair[0],False)):
					roamingCSATs[pair[0]][pair[1]] = data1
				else:
					roamingCSATs[pair[0]] = {pair[1]: data1}

				if(roamingCSATs.get(pair[1],False)):
					roamingCSATs[pair[1]][pair[0]] = data
				else:
					roamingCSATs[pair[1]] = {pair[0]: data}
			# f.close()

			# try:
			with open("./Results/Simulator/Threshold/{}_{}.json".format(pair[0],pair[1]),"r") as f:
				# except:
					# f = open("../Tower Data/Results/peering_{}_{}.json".format(pair[1],pair[0]),"r")
				data = json.load(f)
				data1 = data[pair[1]][-1]["csat"]
				data = data[pair[0]][-1]["csat"]

				if(peering1CSATs.get(pair[0],False)):
					peering1CSATs[pair[0]][pair[1]] = data1
				else:
					peering1CSATs[pair[0]] = {pair[1]: data1}

				if(peering1CSATs.get(pair[1],False)):
					peering1CSATs[pair[1]][pair[0]] = data
				else:
					peering1CSATs[pair[1]] = {pair[0]: data}
			# f.close()

			with open("./Results/Simulator/Sorted Sum/{}_{}.json".format(pair[0],pair[1]),"r") as f:
				# except:
					# f = open("../Tower Data/Results/peering_{}_{}.json".format(pair[1],pair[0]),"r")
				data = json.load(f)
				data1 = data[pair[1]][-1]["csat"]
				data = data[pair[0]][-1]["csat"]

				if(peering2CSATs.get(pair[0],False)):
					peering2CSATs[pair[0]][pair[1]] = data1
				else:
					peering2CSATs[pair[0]] = {pair[1]: data1}

				if(peering2CSATs.get(pair[1],False)):
					peering2CSATs[pair[1]][pair[0]] = data
				else:
					peering2CSATs[pair[1]] = {pair[0]: data}
			# f.close()

	# plotRevenueGain(CSATs,peering2CSATs,roamingCSATs)
	return CSATs,peering1CSATs,peering2CSATs, roamingCSATs

def plotRevenueGRelation(CSATs,peering1CSATs, peering2CSATs,roamingCSATs):

	carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
	labels = ['Verizon', 'T-Mobile', 'Sprint', 'At&t']
	# carriers = ["T_MOBILE",'AT_T']
	# labels = ["T-Mobile",'At&t']

	for i,c in enumerate(carriers):
		revVals = getRevenueGains(CSATs,peering1CSATs, peering2CSATs,roamingCSATs, c, labels[i])
		ys = []
		for k,v in revVals.items():
			# for k,v in revVals.items():
			ys.append([gains[2] for gains in v])
			# plt.plot(range(0,101), [gains[2] for gains in v], label=k[1])
		# plt.title(labels[i])
		# plt.legend()
		# plt.show()
		# print(revVals)
		ys.reverse()
		led = "upper left"
		if c=="AT_T":
			led = "upper right"
		lineGraph(
			[range(0,100)]*3, 
			ys,
			title=labels[i], 
			xlabel="Sensitivity to QoS", 
			ylabel="Revenue Gain (%)", 
			labels=[k[1] for k in list(revVals.keys())],
			# show=True,
			fname = "./Results/Figs/Simulator/rev_{}.pdf".format(c),
			legend=led
		)
		


if __name__ == "__main__":

	if __package__ is None:
		import sys
		from os import path
		sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
		# from plot import *
		from plot import barGraph
		from plot import lineGraph
	else:
		from plot import barGraph


	CSATs,peering1CSATs, peering2CSATs,roamingCSATs = getCSATs()
	# plotRevenueGain(CSATs,peering1CSATs, peering2CSATs,roamingCSATs, 13.8)

	plotRevenueGRelation(CSATs,peering1CSATs, peering2CSATs,roamingCSATs)
