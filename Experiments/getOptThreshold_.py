from subprocess import call
import sys, json
from itertools import combinations
import matplotlib.pyplot as plt

def storeResults(threshold):
    threshold = str(threshold)

    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    peering_combinations = combinations(carriers,2)
    
    for pair in peering_combinations:
        data_json = {}
        with open("./Tower Data/Results/Experiments/Threshold/results.json", "r") as f:

            np = open("./Tower Data/Results/Experiments/Threshold/no_peering_csats.json","r")
            p = open("./Tower Data/Results/Experiments/Threshold/test_peering_csats_{}_{}.json".format(pair[0], pair[1]),"r")

            np_json = json.load(np)
            p_json = json.load(p)
            data_json = json.load(f)
            # print("before", data_json)
            if(data_json.get(threshold,False)):
                if(data_json[threshold].get(pair[0],False)):
                    data_json[threshold][pair[0]][pair[1]] = p_json[pair[0]][-1]["csat"]-np_json[pair[0]][-1]["csat"]
                else:
                    data_json[threshold][pair[0]] = {pair[1] : p_json[pair[0]][-1]["csat"]-np_json[pair[0]][-1]["csat"]}
                
                if(data_json[threshold].get(pair[1],False)):
                    data_json[threshold][pair[1]][pair[0]] = p_json[pair[1]][-1]["csat"]-np_json[pair[1]][-1]["csat"]
                else:
                    data_json[threshold][pair[1]] = {pair[0] : p_json[pair[1]][-1]["csat"]-np_json[pair[1]][-1]["csat"]}
            else:
                data_json[threshold] = {pair[0]:{pair[1] : p_json[pair[0]][-1]["csat"]-np_json[pair[0]][-1]["csat"]}}
                data_json[threshold][pair[1]] = {pair[0] : p_json[pair[1]][-1]["csat"]-np_json[pair[1]][-1]["csat"]}
            

            # print("after", data_json)
            np.close; p.close()

        with open("./Tower Data/Results/Experiments/Threshold/results.json", "w") as f:
            # f.seek(0)
            json.dump(data_json,f)

def relGraph():

    data = {}
    with open("./Tower Data/Results/Experiments/Threshold/results.json","r") as f:
        data = json.load(f)
    
    lst = {"T_MOBILE":[], "VERIZON":[], "AT_T":[], "SPRINT":[]}
    for t, c in data.items():
        for k, v in c.items():
            lst[k].append(sum(list(v.values()))/len(list(v.values())))
    # print(lst)
    x = list(range(10,19))+list(range(20,120,10))
    for k,v in lst.items():
        plt.plot(x, v, label=k, marker="o")
    plt.legend()
    # plt.xticks(x)
    plt.title("CSAT gain vs. County Population Density")
    plt.xlabel("Population Density Percentile")
    plt.ylabel("Average CSAT gain")
    plt.show()
        


if __name__ == "__main__":
    
    # for i in range(91,101):
    #     call("python Experiments/peeringSimulator.py {} {} {}".format(sys.argv[1], int(sys.argv[2]), i), shell=True)
    #     # print("Storing for {}".format(i))
    #     storeResults(i)
    #     print(i)
    
    relGraph()


# 10.0
# 10.0
# 10.0
# 14.0
# 21.5
# 33.0
# 49.0
# 80.80000000000001
# 248.40000000000003