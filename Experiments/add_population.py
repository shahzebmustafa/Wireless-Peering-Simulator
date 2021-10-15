import json
import pandas as pd
import os
# from shapely.geometry import Point, asShape
import sys
# from area import area


def add_population():

    df = pd.read_csv('Tower Data/county_population.csv')
    df = df[['STATE','COUNTY','POPESTIMATE2019']]

    df.to_csv('Tower Data/county_population.csv', index=False)


    carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']

    for c in carriers:

        for root, dirs, files in os.walk('./Tower Data/States/{}/'.format(c)):

            for stateFile in files:
                if(stateFile == '.DS_Store'):
                    continue
                data = dict()
                with open("./Tower Data/States/{}/{}".format(c,stateFile)) as f:
                    data = json.load(f)
                
                statePops = df[df['STATE'] == int(stateFile.replace('.json',''))]


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
                    elif countyID == "102" and stateFile == '46.json':
                        #Lakota County, South Dakota. Some DBs show this, but it doesnt exist in some. Need to check but can skip for now.
                        continue
                    elif countyID == "158" and stateFile == "02.json":
                        #Kusilvak-> not a county, Alaska
                        continue
                    # countyPolygon = asShape(data[countyID]['geometry'])
                    
                    data[countyID]['properties']['pop_density'] = max(10,population // data[countyID]['properties']['CENSUSAREA'])

                    data[countyID]['properties']['population'] = population
                
                with open("./Tower Data/States/{}/{}".format(c,stateFile), 'w') as f:  
                    json.dump(data,f)



add_population()