import json
import pandas as pd
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt

def selectOptCounties(df, selectedCounties):

    df_ = df.loc[df['county'].isin(selectedCounties)].copy()
    df_.reset_index(drop=True, inplace=True)


    sumA = []; sumB = []; net= []

    for i in range(len(df_)):
        try:
            sumA.append(df_["A"].iloc[i]+sumA[i-1])
            sumB.append(df_["B"].iloc[i]+sumB[i-1])
        except:
            sumA.append(df_["A"].iloc[i])
            sumB.append(df_["B"].iloc[i])
        net.append(sumA[i]*sumB[i])
    
    df_["sumA"] = sumA
    df_["sumB"] = sumB
    df_["net"] = net

    return df_


def getPopData(state):

    popData = dict()

    with open("./Tower Data/States/AT_T/{}.json".format(state), "r") as f:
        data = json.load(f)
        for k,v in data.items():
            popData[k] = v["properties"]["population"]/float(v["properties"]["CENSUSAREA"])

    
    return popData

def createDF(pair, state, threshold=False):

    
    benefits = dict()
            
    with open('./Results/Experiments/County Gain/red_{}_{}.json'.format(pair[0],pair[1]),"r") as f:
        benefits = json.load(f)

    dfDict = {"county":[], "A":[], "B":[], "A*B":[], "popDensity":[]}
    
    for i in range(0,len(benefits[pair[0]])):

        if(benefits[pair[0]][i]["benefit"]>0 or benefits[pair[1]][i]["benefit"]>0):
            dfDict["county"].append(benefits[pair[0]][i]["county"])
            dfDict["popDensity"].append(popData[benefits[pair[0]][i]["county"]])
            dfDict["A"].append(benefits[pair[0]][i]["benefit"])
            dfDict["B"].append(benefits[pair[1]][i]["benefit"])
    
    for i in range(0,len(dfDict["county"])):
        dfDict["A*B"].append(dfDict["A"][i]*dfDict["B"][i])
    
    df = pd.DataFrame.from_dict(dfDict)
    df = df.sort_values("A*B", ascending=False)
    sumA = []; sumB = []; net= []

    for i in range(len(df)):
        try:
            sumA.append(df["A"].iloc[i]+sumA[i-1])
            sumB.append(df["B"].iloc[i]+sumB[i-1])
        except:
            sumA.append(df["A"].iloc[i])
            sumB.append(df["B"].iloc[i])
        net.append(sumA[i]*sumB[i])
    
    df["sumA"] = sumA
    df["sumB"] = sumB
    df["net"] = net

    df = df[df["popDensity"] <= threshold]

    return selectOptCounties(df, list(df["county"]))

def getOptThreshold(netGains):
    
    for k,v in netGains.items():

        for i in range(1,len(v)):

            if((v[i]-v[i-1])/v[i] < 0.01):
                check = 0
                for j in range(i+1,len(v)):
                    if((v[j]-v[j-1])/v[j] < 0.01):
                        check += 1
                    else:
                        break
                # print(check , len(v)-i)
                if(check == len(v)-i-1):
                    print(k,i+1)
                    break

def marginal(netGains):
    m = []
    m_ = netGains[0]
    for i in range(0,len(netGains)):

        m.append(((netGains[i]-m_)/m_)*100)
        m_ = netGains[i]
    
    return m


if __name__ == "__main__":
    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)
    popData = getPopData("48")
    pops = list(popData.values())
    result = dict()
    fig = plt.figure(figsize=(10, 8))

    for pair in carrier_combinations:
        
        result[pair] = []
        for i in range(1,101):
            threshold = np.percentile(pops, i)
            # print(threshold)
            result[pair].append(createDF(pair, "48", threshold)["net"].iloc[-1])

        
        plt.plot(range(1,101), result[pair], label=pair[0]+"-"+pair[1], linewidth=2)
        # break
    # getOptThreshold(result)
    plt.legend(fontsize=22)
    plt.xlabel("Population Density Percentile", fontsize=24)
    plt.ylabel("Net Benefit", fontsize=24)
    plt.title("CSAT gain vs. Population Density", fontsize=24)
    
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)


    # plt.show()
    plt.savefig("./Results/Figs/Experiments/Threshold/netBenefit_popDensity.pdf")


