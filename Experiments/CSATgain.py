import json
import math
# import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def plotCSATGain(CSATs,peering1CSATs, peering2CSATs,roamingCSATs):

	'''
	CSATs data format: {carrier:int}
	peeringCSATs data format: {carrier1:{carrier2:int}}
	roamingCSATs data format: {carrier1:{carrier2:int}}
	'''
	def gain(x,y):

		return abs(((y-x)/x)*100.0)

	carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
	
	
	xticks = ['Verizon', 'T-Mobile', 'Sprint', 'At&t']
	
	for i,c_ in enumerate(carriers):
		ys = []
		fname = "./Results/Figs/Simulator/{}_CSAT_gain.pdf".format(c_)
		for c in carriers:
			if c_ != c:
				# print("Roaming: ", gain(CSATs[c_],roamingCSATs[c][c_]) ,"Peering:",gain(CSATs[c_],peeringCSATs[c][c_]))
				ys.append([gain(CSATs[c_],roamingCSATs[c][c_]) , gain(CSATs[c_],peering1CSATs[c][c_]) , gain(CSATs[c_],peering2CSATs[c][c_])])

		barGraph(
			ys, 
			title="{} CSAT Gain Comparison".format(xticks[i]), 
			xlabel="", 
			ylabel="Net CSAT Gain (%)",
			xticks=xticks[:i] + xticks[i+1 :], 
			labels=["Roaming", "Peering (T)", "Peering (SS)"], 
			fname=fname, 
			show=False,
			legend=False
		)


if __name__ == "__main__":

	if __package__ is None:
		import sys
		from os import path
		sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
		from plot import barGraph
		from revenue_gain import getCSATs
	else:
		from plot import barGraph
		from revenue_gain import getCSATs

	CSATs,peering1CSATs, peering2CSATs, roamingCSATs = getCSATs()
	plotCSATGain(CSATs,peering1CSATs, peering2CSATs,roamingCSATs)
