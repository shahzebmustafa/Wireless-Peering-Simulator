import json, sys, math, geog
from itertools import combinations
from area import area
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import cascaded_union
import numpy as np

BSrange = {
    "LTE":2,
    "CDMA": 4,
    "UMTS": 3,
    "GSM": 10
}

def getBSCount(state,carriers):

    data = dict()
    for c in carriers:
        with open("./Tower Data/States/{}/{}.json".format(c,state),"r") as f:

            data_ = json.load(f)
            for k,v in data_.items():
                
                if data.get(k,False):
                    data[k][c] = len(v["basestations"])
                else:
                    data[k] = {c:len(v["basestations"])}
            # data[c] = len(data_[county]["basestations"])
            # data[c] = data_[county]["properties"]["pop_density"]
    return data


def get_bs_load(state):
    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']
    retData = dict()
    popData = dict()
    for c in carriers:
        
        with open("./Tower Data/States/{}/{}.json".format(c,state),"r") as f:

            data = json.load(f)
            for county,v in data.items():

                if retData.get(county,False):
                    retData[county] += len(data[county]["basestations"])
                else:
                    retData[county] = 1
                    popData[county] = [data[county]["properties"]["pop_density"],data[county]["properties"]["population"]]

    for k,v in retData.items():
        print(k, popData[k][0]/v, popData[k][1], popData[k][0],v)

def getPopData(state,carriers):


    popData = dict()
    for c in carriers:
        
        with open("./Tower Data/States/{}/{}.json".format(c,state),"r") as f:

            data = json.load(f)
            for county,v in data.items():
                # try:
                #     popData[county]["population"] = v["properties"]
                #     popData[county]["pop_density"] = v["pop_density"]
                # except:
                popData[county] = {"population":v["properties"]["population"]}
                popData[county]["pop_density"] = v["properties"]["pop_density"]
    return popData

def getBenefitData(state,carriers):

    
    carrier_combinations = combinations(carriers,2)
    benefitData = dict()

    for pair in carrier_combinations:

        try:
            with open("./Results/Experiments/County Gain/{}_{}.json".format(pair[0],pair[1]),"r") as f:

                data = json.load(f)
                isp1 = pair[0]
                isp2 = pair[1]
                for county in data[pair[0]]:
                    
                    
                    if benefitData.get(county["county"],False):
                        if benefitData[county["county"]].get(isp1, False):
                            benefitData[county["county"]][isp1][isp2] = {"benefit" : county["benefit"]}
                        else:
                            benefitData[county["county"]][isp1] = {isp2:{"benefit" : county["benefit"]}}
                    else:
                        benefitData[county["county"]] = {isp1: {isp2: {"benefit" : county["benefit"]}}}
                    benefitData[county["county"]][isp1][isp2]["before"] = county["before"]
                    benefitData[county["county"]][isp1][isp2]["after"] = county["after"]
                
                for county in data[isp2]:
                    
                    
                    if benefitData.get(county["county"],False):
                        if benefitData[county["county"]].get(isp2, False):
                            benefitData[county["county"]][isp2][isp1] = {"benefit" : county["benefit"]}
                        else:
                            benefitData[county["county"]][isp2] = {isp1:{"benefit" : county["benefit"]}}
                    else:
                        benefitData[county["county"]] = {isp2: {isp1: {"benefit" : county["benefit"]}}}
                    benefitData[county["county"]][isp2][isp1]["before"] = county["before"]
                    benefitData[county["county"]][isp2][isp1]["after"] = county["after"]
        except Exception as e:
            # raise e
            print(e)
            continue
    
    return benefitData


def getCustomerCount(population, pBScount, tBScount):
    tBScount = sum(list(tBScount.values()))
    
    return population * (pBScount/tBScount)

def getCoverage(basestations,CENSUSAREA,a=False, g=False):
    cArea = 0
    circles = []
    for bs in basestations:
        p = Point(bs["location"])

        n_points = 20
        d = BSrange[bs["radio"]] * 1609.34  # miles to meters
        angles = np.linspace(0, 360, n_points)
        polygon = geog.propagate(p, angles, d)
        circles.append(Polygon(polygon))
        # print(json.dumps(shapely.geometry.mapping(shapely.geometry.Polygon(polygon))))

    covgPolygon = cascaded_union(circles)
    cArea = min(area(mapping(covgPolygon))/2590000,CENSUSAREA)

    if a:
        return cArea
    elif g:
        return covgPolygon
    return cArea/CENSUSAREA

def getCovgData(state, carriers, a=False, g=False):

    data1 = dict()

    for c in carriers:


        with open("./Tower Data/States/{}/{}.json".format(c,state), "r") as f:
            data = json.load(f)
            for k,v in data.items():
                # try:
                if data1.get(k,False):
                    data1[k][c] = getCoverage(v["basestations"],v["properties"]["CENSUSAREA"],a=a, g=g)
                else:
                    data1[k] = {c: getCoverage(v["basestations"],v["properties"]["CENSUSAREA"],a=a, g=g)}
                # except:
                #     raise Exception("County: {}, BS Count: {}, Area: {}".format(k,len(v["basestations"]),v["properties"]["CENSUSAREA"]))

        
    return data1

def getCovgAreaGainData(state, carriers):

    covgData = getCovgData(state, carriers, g=True)
    carrier_combinations = combinations(carriers,2)
    covgAreaGain = dict()

    for pair in carrier_combinations:
        print(pair)
        for county,v in covgData.items():
            # print(area(mapping(v[pair[0]].union(v[pair[1]]))))
            uArea  = area(mapping(v[pair[0]].union(v[pair[1]])))/2590000
            p1Area = area(mapping(v[pair[0]]))/2590000
            p2Area = area(mapping(v[pair[1]]))/2590000
            # print("County: ",county, "{} area: ".format(pair[0]),p1Area, "{} area:".format(pair[1]),p2Area,"union area: ",uArea, "{} gain".format(pair[0]),uArea-p1Area, "{} gain".format(pair[1]), uArea-p2Area)
            
            if covgAreaGain.get(county,False):
                if covgAreaGain[county].get(pair[0],False):
                    covgAreaGain[county][pair[0]][pair[1]] = round(uArea - p1Area,10)
                else:
                    covgAreaGain[county][pair[0]] = {pair[1]: round(uArea - p1Area,10)}
                
                if covgAreaGain[county].get(pair[1],False):
                    covgAreaGain[county][pair[1]][pair[0]] = round(uArea - p2Area,10)
                else:
                    covgAreaGain[county][pair[1]] = {pair[0]: round(uArea - p2Area,10)}
            else:
                covgAreaGain[county] = {pair[0] : {pair[1]: round(uArea - p1Area,10)}}
                covgAreaGain[county][pair[1]] = {pair[0]: round(uArea - p2Area,10)}
        # raise Exception("test")
    # print(covgAreaGain)
    return covgAreaGain
            


def createBenefitCSV(state):

    import pandas

    carriers = ['VERIZON', 'T_MOBILE', 'SPRINT', 'AT_T']
    bsCount = getBSCount(state,carriers)
    popData = getPopData(state,carriers)
    benefitData = getBenefitData(state,carriers)
    covgData = getCovgData(state, carriers)
    covgAreaData = getCovgData(state, carriers, a=True)
    covgAreaGainData = getCovgAreaGainData(state, carriers)
    

    carrier_combinations = combinations(carriers,2)

    for pair in carrier_combinations:
        try:
            df = {"County":[],	"Population":[],	"Pop Density":[], "Coverage Diff":[], "BS Load":[],	
                "{} Customer Count".format(pair[0]):[], "{} BS Count".format(pair[0]):[], "{} Coverage".format(pair[0]):[], "{} Coverage Area".format(pair[0]):[], "{} Coverage Area Gain".format(pair[0]):[],	"{} BS Load".format(pair[0]):[],	"{} BS Load (Density)".format(pair[0]):[],	"{} CSAT Gain".format(pair[0]):[], "{} CSAT RGain".format(pair[0]):[],	"{} CSAT Before".format(pair[0]):[],	"{} CSAT After".format(pair[0]):[],	
                "{} Customer Count".format(pair[1]):[], "{} BS Count".format(pair[1]):[], "{} Coverage".format(pair[1]):[], "{} Coverage Area".format(pair[1]):[], "{} Coverage Area Gain".format(pair[1]):[], "{} BS Load".format(pair[1]):[],	"{} BS Load (Density)".format(pair[1]):[],	"{} CSAT Gain".format(pair[1]):[], "{} CSAT RGain".format(pair[1]):[],	"{} CSAT Before".format(pair[1]):[],	"{} CSAT After".format(pair[1]):[]
            }
            for county in bsCount.keys():
                df["County"].append(county)
                df["Population"].append(popData[county]["population"])
                df["Pop Density"].append(popData[county]["pop_density"])
                df["Coverage Diff"].append(abs(covgData[county][pair[0]]-covgData[county][pair[1]]))
                customers1 = getCustomerCount(popData[county]["population"]/1000.0,bsCount[county][pair[0]], bsCount[county])
                customers2 = getCustomerCount(popData[county]["population"]/1000.0,bsCount[county][pair[1]], bsCount[county])

                df["BS Load"].append((customers1+customers2) / max(1,bsCount[county][pair[0]]+bsCount[county][pair[1]]))
                
                df["{} BS Count".format(pair[0])].append(bsCount[county][pair[0]])
                df["{} Coverage".format(pair[0])].append(covgData[county][pair[0]])
                df["{} Coverage Area".format(pair[0])].append(covgAreaData[county][pair[0]])
                df["{} Coverage Area Gain".format(pair[0])].append(covgAreaGainData[county][pair[0]][pair[1]])
                customers = getCustomerCount(popData[county]["population"]/1000.0,bsCount[county][pair[0]], bsCount[county])
                df["{} Customer Count".format(pair[0])].append(customers*1000)
                df["{} BS Load".format(pair[0])].append(customers / max(1,bsCount[county][pair[0]]))
                customers = getCustomerCount(popData[county]["pop_density"],bsCount[county][pair[0]], bsCount[county])
                df["{} BS Load (Density)".format(pair[0])].append(customers / max(1,bsCount[county][pair[0]]))
                try:
                    df["{} CSAT Gain".format(pair[0])].append(100*(benefitData[county][pair[0]][pair[1]]["benefit"]/benefitData[county][pair[0]][pair[1]]["before"]))
                    df["{} CSAT RGain".format(pair[0])].append(100*(benefitData[county][pair[0]][pair[1]]["benefit"]/(1-benefitData[county][pair[0]][pair[1]]["before"])))
                    df["{} CSAT Before".format(pair[0])].append(benefitData[county][pair[0]][pair[1]]["before"])
                    df["{} CSAT After".format(pair[0])].append(benefitData[county][pair[0]][pair[1]]["after"])
                except:
                    df["{} CSAT Gain".format(pair[0])].append(-1)
                    df["{} CSAT RGain".format(pair[0])].append(-1)
                    df["{} CSAT Before".format(pair[0])].append(-1)
                    df["{} CSAT After".format(pair[0])].append(-1)

                df["{} BS Count".format(pair[1])].append(bsCount[county][pair[1]])
                df["{} Coverage".format(pair[1])].append(covgData[county][pair[1]])
                df["{} Coverage Area".format(pair[1])].append(covgAreaData[county][pair[1]])
                df["{} Coverage Area Gain".format(pair[1])].append(covgAreaGainData[county][pair[1]][pair[0 ]])
                customers = getCustomerCount(popData[county]["population"]/1000.0,bsCount[county][pair[1]], bsCount[county])
                df["{} Customer Count".format(pair[1])].append(customers*1000)
                df["{} BS Load".format(pair[1])].append(customers / max(1,bsCount[county][pair[1]]))
                customers = getCustomerCount(popData[county]["pop_density"],bsCount[county][pair[1]], bsCount[county])
                df["{} BS Load (Density)".format(pair[1])].append(customers / max(1,bsCount[county][pair[1]]))
                try:
                    df["{} CSAT Gain".format(pair[1])].append(100*(benefitData[county][pair[1]][pair[0]]["benefit"]/benefitData[county][pair[1]][pair[0]]["before"]))
                    df["{} CSAT RGain".format(pair[1])].append(100*(benefitData[county][pair[1]][pair[0]]["benefit"]/(1-benefitData[county][pair[1]][pair[0]]["before"])))
                    df["{} CSAT Before".format(pair[1])].append(benefitData[county][pair[1]][pair[0]]["before"])
                    df["{} CSAT After".format(pair[1])].append(benefitData[county][pair[1]][pair[0]]["after"])
                except:
                    df["{} CSAT Gain".format(pair[1])].append(-1)
                    df["{} CSAT RGain".format(pair[1])].append(-1)
                    df["{} CSAT Before".format(pair[1])].append(-1)
                    df["{} CSAT After".format(pair[1])].append(-1)

            df = pandas.DataFrame.from_dict(df)
            df.to_csv("./Results/Experiments/County Gain/CSVs/{}_{}.csv".format(pair[0],pair[1]), index=False)
        except Exception as e:
            # print(pair)
            raise e
            print(len(df["{} Customer Count".format(pair[0])]), len(df["{} Customer Count".format(pair[1])]), len(df["{} CSAT Gain".format(pair[1])]))
            print(e)
            continue


if __name__ == "__main__":
    
    # print(count_bs("48",sys.argv[1]))
    # get_bs_load("48")
    createBenefitCSV("48")

