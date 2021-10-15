import json
import pandas as pd
from shapely.geometry import asShape, Point
from add_population import add_population



carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']

countiesData = dict()
statesData = dict()

with open('Tower Data/county-boundaries.json') as f:
    countiesData = json.load(f)

with open('Tower Data/state-boundaries.json') as f:
    statesData = json.load(f)


def getCounty(bs, state):
    for county in countiesData["features"]:
        if state == county["properties"]["STATE"] == state:
            countyPolygon = asShape(county["geometry"])
            # if county["geometry"]["type"] == "Polygon":
            #     countyPolygon = Polygon(county["geometry"]["coordinates"])
            # else:
            #     countyPolygon = MultiPolygon(county["geometry"]["coordinates"])
            if countyPolygon.contains(Point(bs[0],bs[1])):
                return county["properties"]["COUNTY"]
    return None



def getStateCounty(bs):
    bsState = None
    bsCounty = None
    for state in statesData["features"]:
        statePolygon = asShape(state["geometry"])
        # if state["geometry"]["type"] == "Polygon":
        #     statePolygon = Polygon(state["geometry"]["coordinates"])
        # else:
        #     statePolygon = MultiPolygon(state["geometry"]["coordinates"])
        if statePolygon.contains(Point(bs[0],bs[1])):
            bsState = state["properties"]["STATE"]
            bsCounty = getCounty(bs,bsState)

        
    return bsState, bsCounty

def insert_bsData_(bs, bsData, state, county, df):

    if bsData.get(state,False):

        if bsData[state].get(county,False):

            bsData[state][county]["bsLocations"].append(bs)

        else:

            bsData[state][county] = {"bsLocations":[bs]}
        
    else:

        bsData[state] = {county: {"bsLocations":[bs]}}


def insert_bsData(countyBSs, bsData, county):

    if bsData.get(county["properties"]["STATE"],False):

        bsData[county["properties"]["STATE"]][county["properties"]["COUNTY"]] = {"basestations":countyBSs, "properties":county["properties"], "geometry":county["geometry"]}
        
    else:

        bsData[county["properties"]["STATE"]] = {county["properties"]["COUNTY"]: {"basestations":countyBSs, "properties":county["properties"], "geometry":county["geometry"]}}
    

def get_bs_for_county(county, df):

    countyPolygon = asShape(county["geometry"])
    min_lon, min_lat, max_lon, max_lat = countyPolygon.bounds

    _countyBSs = df[df["lat"]>=min_lat]
    _countyBSs = _countyBSs[_countyBSs["lat"]<=max_lat]
    _countyBSs = _countyBSs[_countyBSs["lon"]>=min_lon]
    _countyBSs = _countyBSs[_countyBSs["lon"]<=max_lon]

    countyBSs = []
    for ind in _countyBSs.index:

        if countyPolygon.contains(Point(_countyBSs["lon"][ind],_countyBSs["lat"][ind])):
            bs = {"location":[_countyBSs["lon"][ind],_countyBSs["lat"][ind]], "radio":_countyBSs["radio"][ind], "samples":int(_countyBSs["samples"][ind]), "network":_countyBSs["network"][ind]}
            countyBSs.append(bs)

    

    return countyBSs


for c in carriers:
    i = 0
    print("Getting BS locations for {}".format(c))

    bsData = dict()

    # df = pd.read_csv('./Tower Data/Clean/'+c+'.csv')
    df = pd.read_csv('./Tower Data/Compressed/'+c+'.csv')
    
    for county in countiesData["features"]:

        countyBSs = get_bs_for_county(county, df)
        i += 1
        print(((i/3221)*100)//1,"%", end="\r")
        # print("Got results from {}{} county".format(county["properties"]["STATE"],county["properties"]["COUNTY"]))
        insert_bsData(countyBSs, bsData, county)


    # for ind in df.index:
    #     bs = [df['lat'][ind],df['lon'][ind]]
        
    #     state, county = getStateCounty(bs)
    #     insert_bsData_(bs, bsData, state, county, df.iloc[ind])
    print("Writing files for {}".format(c))
    for k,v in bsData.items():
        with open('Tower Data/States/{}/{}.json'.format(c,k), 'w') as f:
            json.dump(v, f)
    print("BS locations data completed for {}\n\n".format(c))

add_population()