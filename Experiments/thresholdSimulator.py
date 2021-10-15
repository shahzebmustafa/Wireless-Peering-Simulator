from subprocess import call
from itertools import combinations


if __name__ == "__main__":
    
    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)

    call("python sim.py -np 48 0", shell=True)

    for pair in carrier_combinations:

        call("python sim.py -p 48 0 {} {} 89".format(pair[0],pair[1]), shell=True)
