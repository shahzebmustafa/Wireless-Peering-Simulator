import matplotlib.pyplot as plt
from shapely.geometry import MultiPoint, mapping, asShape
import json, math
from itertools import combinations
import pandas as pd
from area import area
import numpy as np

def readPopulation(state):
    data_ = dict()

    df = pd.read_csv('Tower Data/county_population.csv')
    statePops = df[df['STATE'] == int(state)]

    for ind in statePops.index:
        countyID = int(statePops['COUNTY'][ind])
        population = int(statePops['POPESTIMATE2019'][ind])

        if countyID < 10:
            countyID = "00"+str(countyID)
        elif countyID < 100:
            countyID = "0"+str(countyID)
        else:
            countyID = str(countyID)

        if countyID == "000":
            continue

        data_[countyID] = population
    return data_

def readPopDensity(state):

    data = dict()
    data_ = dict()
    with open("./Tower Data/county-boundaries.json","r") as f:
        data = json.load(f)
    


    df = pd.read_csv('./Tower Data/county_population.csv')
    statePops = df[df['STATE'] == int(state)]

    for ind in statePops.index:
        countyID = int(statePops['COUNTY'][ind])
        population = int(statePops['POPESTIMATE2019'][ind])

        if countyID < 10:
            countyID = "00"+str(countyID)
        elif countyID < 100:
            countyID = "0"+str(countyID)
        else:
            countyID = str(countyID)

        if countyID == "000":
            continue
        
        area = 0
        for county in data["features"]:
            if countyID == county["properties"]["COUNTY"] and state == county["properties"]["STATE"]:
                area = county['properties']['CENSUSAREA']

        data_[countyID] = population / area
    return data_

def areaFor2Points(p1, p2):
    earthRadious = 3959
    dlat = np.deg2rad(p2[1] - p1[1])
    dlong = np.deg2rad(p2[0] - p1[0])
    a = (np.sin(dlat / 2)) ** 2 + np.cos(np.deg2rad(p1[1])) * np.cos(np.deg2rad(p2[1])) * ((np.sin(dlong / 2)) ** 2)
    b = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    b *= earthRadious
    b /= 2

    p = b*math.tan(math.radians(22.5))

    return 2*(p*b)

def getCoverage(basestations,CENSUSAREA):

    if(len(basestations) == 0):
        cArea = 0
    elif (len(basestations) == 1):
        cArea = 70
    elif (len(basestations) == 2):
        cArea = areaFor2Points(basestations[0]["location"],basestations[1]["location"])
    else:

        convex_hull = MultiPoint([bs["location"] for bs in basestations]).convex_hull
        cArea = area(mapping(convex_hull))/2590000
        cArea = min(cArea*1.25,CENSUSAREA)

    return cArea/CENSUSAREA
        
def readCoverageDiff(state,isp1,isp2):
    data1 = dict()
    data2 = dict()

    with open("./Tower Data/States/{}/{}.json".format(isp1,state), "r") as f:
        data = json.load(f)
        for k,v in data.items():
            data1[k] = getCoverage(v["basestations"],v["properties"]["CENSUSAREA"])

    with open("./Tower Data/States/{}/{}.json".format(isp2,state), "r") as f:
        data = json.load(f)
        for k,v in data.items():
            data2[k] = getCoverage(v["basestations"],v["properties"]["CENSUSAREA"])
        
    return {isp1:data1, isp2:data2}



def benefit_popdensity(state):

    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)

    pop_density = readPopDensity(state)

    for pair in carrier_combinations:

        benefits = dict()
        with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1])) as f:
            benefits = json.load(f)

        d1 = {'x':[], 'y':[]}
        d2 = {'x':[], 'y':[]}

        for county in benefits[pair[0]]:
            d1['x'].append(pop_density[county["county"]])
            d1['y'].append(county["benefit"])
        
        for county in benefits[pair[1]]:
            d2['x'].append(pop_density[county["county"]])
            d2['y'].append(county["benefit"])

        plt.figure(figsize=(20,5))    
        plt.xscale("log")
        plt.plot(d1['x'],d1['y'],'.',label=pair[0])
        plt.plot(d2['x'],d2['y'],'x',label=pair[1])
        plt.legend()

        plt.show()
        # break

def removeOutliers(klist, avglatlist):
    # klist = ['1', '2', '3', '4', '5', '6', '7', '8', '4000']
    # avglatlist = ['1', '2', '3', '4', '5', '6', '7', '8', '9']


    klist_np = np.array(klist).astype(np.float)
    avglatlist_np = np.array(avglatlist).astype(np.float)    

    klist_filtered = klist_np[(abs(klist_np - np.mean(klist_np))) < (np.std(klist_np))]
    avglatlist_filtered = avglatlist_np[(abs(klist_np - np.mean(klist_np))) < (np.std(klist_np))]
    


    return klist_filtered,avglatlist_filtered

def benefit_coveragediff(state):

    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)

    for pair in carrier_combinations:

        coverage_diff = readCoverageDiff(state,pair[0],pair[1])
        benefits = dict()
        with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1])) as f:
            benefits = json.load(f)

        d1 = {'x':[], 'y':[]}
        d2 = {'x':[], 'y':[]}

        for county in benefits[pair[0]]:
            coverage = abs(coverage_diff[pair[0]][county["county"]] - coverage_diff[pair[1]][county["county"]])
            d1['x'].append(coverage)
            d1['y'].append(county["benefit"])
        
        for county in benefits[pair[1]]:
            coverage = abs(coverage_diff[pair[0]][county["county"]] - coverage_diff[pair[1]][county["county"]])
            d2['x'].append(coverage)
            d2['y'].append(county["benefit"])

        d1['x'], d1['y'] = removeOutliers(d1['x'], d1['y'])
        d2['x'], d2['y'] = removeOutliers(d2['x'], d2['y'])


        plt.figure(figsize=(20,5))    
        plt.xscale("log")
        plt.plot(d1['x'],d1['y'],'.',label=pair[0])
        plt.plot(d2['x'],d2['y'],'x',label=pair[1])
        plt.legend()

        plt.show()


def combinedGraph(state):

    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)

    for pair in carrier_combinations:

        coverage_diff = readCoverageDiff(state,pair[0],pair[1])
        pop_density = readPopDensity(state)
        benefits = dict()
        with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1])) as f:
            benefits = json.load(f)

        d1 = {'x':[], 'y':[]}
        d2 = {'x':[], 'y':[]}

        for county in benefits[pair[0]]:
            coverage = abs(coverage_diff[pair[0]][county["county"]] - coverage_diff[pair[1]][county["county"]])
            d1['x'].append(abs(coverage - pop_density[county["county"]]))
            d1['y'].append(county["benefit"])
        
        for county in benefits[pair[1]]:
            coverage = abs(coverage_diff[pair[0]][county["county"]] - coverage_diff[pair[1]][county["county"]])
            d2['x'].append(abs(coverage - pop_density[county["county"]]))
            d2['y'].append(county["benefit"])

        d1['x'], d1['y'] = removeOutliers(d1['x'], d1['y'])
        d2['x'], d2['y'] = removeOutliers(d2['x'], d2['y'])

        plt.figure(figsize=(20,5))    
        plt.xscale("log")
        plt.plot(d1['x'],d1['y'],'.',label=pair[0])
        plt.plot(d2['x'],d2['y'],'x',label=pair[1])
        plt.legend()

        plt.show()

def getBsCount(state):
    import os
    bsCount = {'VERIZON':{}, 'AT_T':{}, 'T_MOBILE':{}, 'SPRINT':{}}

    for root, dirs, files in os.walk("./Tower Data/States/"):

        for d in dirs:

            with open("./Tower Data/States/{}/{}.json".format(d,state),"r") as f:
                data = json.load(f)
                for k,v in data.items():

                    bsCount[d][k] = len(v["basestations"])
    return bsCount




def benefit_bsLoad(state):

    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    carrier_combinations = combinations(carriers,2)

    bsCount = getBsCount(state)
    # population = readPopulation(state)
    population = readPopDensity(state)

    for pair in carrier_combinations:

        
        benefits = dict()
        with open('./Results/Experiments/County Gain/{}_{}.json'.format(pair[0],pair[1])) as f:
            benefits = json.load(f)

        d1 = {'x':[], 'y':[]}
        d2 = {'x':[], 'y':[]}

        for county in benefits[pair[0]]:
            
            d1['x'].append(population[county["county"]] / max(1,bsCount[pair[0]][county["county"]]))
            # d1['x'].append(bsCount[pair[0]][county["county"]] / population[county["county"]])
            d1['y'].append(county["benefit"])
        
        for county in benefits[pair[1]]:
            
            d2['x'].append(population[county["county"]] / max(1,bsCount[pair[1]][county["county"]]))
            # d2['x'].append(bsCount[pair[1]][county["county"]] / population[county["county"]])
            d2['y'].append(county["benefit"])

        d1['x'], d1['y'] = removeOutliers(d1['x'], d1['y'])
        d2['x'], d2['y'] = removeOutliers(d2['x'], d2['y'])

        plt.figure(figsize=(20,5))    
        plt.xscale("log")
        plt.plot(d1['x'],d1['y'],'.',label=pair[0])
        plt.plot(d2['x'],d2['y'],'x',label=pair[1])
        plt.legend()

        plt.show()

def logTransform(axes):

    for j, axis in enumerate(axes):

        m = min(axis)
        # if m<1:
        t = 1-m
        for i, value in enumerate(axis):
            axes[j][i] += t

    return axes


# def overlapGraph():



def plotCombinedGraph(state):
    
    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    labels = ['Verizon', 'T-Mobile', 'Sprint', 'At&t']
    carrier_combinations = combinations(carriers,2)
    labels = list(combinations(labels,2))
    
    from plot import scatterPlot
    # scatterPlot(xs=[df["AT_T Coverage"]], ys=[df["AT_T BS Count"]], cs=[df["AT_T CSAT Gain"]], zs=[df["AT_T BS Load"]], labels=["At&t"])
    for i, pair in enumerate(carrier_combinations):
        df = pd.read_csv("./Results/Experiments/County Gain/CSVs/{}_{}.csv".format(pair[0], pair[1]))

        bsCount = [df["{} BS Count".format(pair[0])], df["{} BS Count".format(pair[1])]]
        bsLoad = [df["{} BS Load".format(pair[0])], df["{} BS Load".format(pair[1])]]
        bsLoad_ = [df["{} BS Load".format(pair[0])]+(1-min(df["{} BS Load".format(pair[0])])), df["{} BS Load".format(pair[1])]+(1-min(df["{} BS Load".format(pair[1])]))]

        # bsLoad = [df["BS Load"], df["BS Load"]]
        # bsLoad_ = [df["BS Load"]+(1-min(df["BS Load"])), df["BS Load"]+(1-min(df["BS Load"]))]
        
        bsLoadD = [df["{} BS Load (Density)".format(pair[0])], df["{} BS Load".format(pair[1])]]
        CSATgain = [df["{} CSAT Gain".format(pair[0])], df["{} CSAT Gain".format(pair[1])]]
        CSATRgain_ = [df["{} CSAT RGain".format(pair[0])]+(1-min(df["{} CSAT RGain".format(pair[0])])), df["{} CSAT RGain".format(pair[1])]+(1-min(df["{} CSAT RGain".format(pair[1])]))]
        CSATRgain = [df["{} CSAT RGain".format(pair[0])], df["{} CSAT RGain".format(pair[1])]]

        coverageGain = [df["{} Coverage Area Gain".format(pair[0])], df["{} Coverage Area Gain".format(pair[1])]]
        popDensity = [df["Pop Density"], df["Pop Density"]]
        pop = [df["Population"], df["Population"]]
        covg = [df["{} Coverage".format(pair[0])], df["{} Coverage".format(pair[1])]]
        covgDiff = [df["Coverage Diff"], df["Coverage Diff"]]


        y = [[abs(y1 - y2) for (y1, y2) in zip(df["{} CSAT RGain".format(pair[0])], df["{} CSAT RGain".format(pair[1])])]]
        y_ = [[i+(1-min(y[0])) for i in y[0]]]

        x = [covgDiff[0]]


        # zeroLine = 1-min(df["{} CSAT RGain".format(pair[0])])
        # xlabel = r"Coverage Area Gain ($km^2$)"
        ylabel = r"Relative CSAT Gain (%)"
        zlabel = "CSAT Gain"
        # cs = [df["{} CSAT Gain".format(pair[0])], df["{} CSAT Gain".format(pair[1])]]

        
        # xlabel = r"Coverage Area Score Difference"
        # scatterPlot(
        #     xs=covgDiff, 
        #     ys=CSATRgain, 
        #     title="", 
        #     labels=labels[i], 
        #     xlabel=xlabel, 
        #     ylabel=ylabel, 
        #     zlabel=zlabel, 
        #     fname="./Results/Figs/Experiments/County Gain/covgDiff_{}_{}.pdf".format(pair[0],pair[1]),
        #     show=False)
        
        xlabel = r"Coverage Area Gain ($km^2$)"
        scatterPlot(
            xs=coverageGain, 
            ys=CSATRgain, title="", 
            labels=labels[i], 
            xlabel=xlabel, 
            ylabel=ylabel, 
            zlabel=zlabel, 
            fname="./Results/Figs/Experiments/County Gain/covgGain_{}_{}.pdf".format(pair[0],pair[1]), 
            show=False)

        # overlapGraph(covgDiff, CSATRgain_)

# benefit_coveragediff("48") 
# benefit_popdensity("48")
# combinedGraph("48")
# benefit_bsLoad("48")
plotCombinedGraph("48")