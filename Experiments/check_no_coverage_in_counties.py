import os
import json


def count_counties_with_no_coverage(carrier,state):

	with open('../Tower Data/States/{}/{}.json'.format(carrier, state), 'r') as f:
		data = json.load(f)
		no_coverage_count = 0

		for k, v in data.items():

			if len(v["basestations"]) == 0:
				no_coverage_count += 1

		return no_coverage_count
	raise Exception("Something went wrong! I wasn't able to read the file...")


if __name__ == '__main__':
	
	carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
	state = "48"
	
	for c in carriers:

		print("{} has no coverage in {} counties.".format(c, count_counties_with_no_coverage(c,state)))
