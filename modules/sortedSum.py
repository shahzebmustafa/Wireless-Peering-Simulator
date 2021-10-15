import json
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt

def generateDF(pair):

    benefits = dict()
    with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1]),"r") as f:
        benefits = json.load(f)

    dfDict = {"county":[], "A":[], "B":[], "A*B":[]}

    for i in range(0,len(benefits[pair[0]])):

        if(benefits[pair[0]][i]["benefit"]>0 or benefits[pair[1]][i]["benefit"]>0):
            dfDict["county"].append(benefits[pair[0]][i]["county"])
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

    return df


def createDF(df, selectedCounties):

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


def cummSum(gainDF, selectedCounties):
    A = gainDF["A"].iloc[-1]
    B = gainDF["B"].iloc[-1]

    if(len(gainDF) == 1):
        if (A * B) > 0:
            selectedCounties.add(gainDF["county"].iloc[-1])
            return A, B
        else:
            return 0, 0
    
    sumA, sumB = cummSum(gainDF.iloc[0:len(gainDF)-1].copy(), selectedCounties)
    s = (sumA+A) * (sumB+B)
    ns = sumA * sumB
    if s > ns:
        selectedCounties.add(gainDF["county"].iloc[-1])
        return sumA+A, sumB+B
    else:
        return sumA, sumB


def maxSumProd(pair):

    result = generateDF(pair)
    counties = set([])

    sumA, sumB = cummSum(result, counties)
    return counties



if __name__ == "__main__":
    
    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)
