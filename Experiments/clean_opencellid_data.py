import json
import pandas as pd
import os


mnc_data = dict()

with open('./Tower Data/mcc_mnc-network.json') as f:
    mnc_data = json.load(f)


dfList = []
carriers = ['VERIZON', 'AT_T', 'T_MOBILE', 'SPRINT']

for root, dirs, files in os.walk('./Tower Data/Raw/'):
    for f in files:
        if('.csv' in f):
            df = pd.read_csv('./Tower Data/Raw/'+f)
            df = df.drop(["unit", "range", "changeable", "created", "updated", "averageSignal"], axis=1)
            df = df.drop_duplicates(subset =["lat", "lon"], keep = 'first')
            df = df.drop_duplicates(subset =["cell"], keep = 'first')

            df = df[df['lat'] <= 50]
            df = df[df['lat'] >= 24]

            df = df[df['lon'] <= -66.5]
            df = df[df['lon'] >= -125]

            networks = []
            for i in range(len(df)):
                try:
                    networks.append(mnc_data[str(df['mcc'][i])+'_'+str(df['net'][i])])
                except:
                    networks.append(None)
            df['network'] = networks
            df = df[df['network'].isin(carriers)]
            
            df = df.drop(['mcc', 'net', 'area'], axis=1)
            dfList.append(df)


mergedData = pd.concat(dfList)
dfList = []

for c in carriers:

    mergedData[mergedData['network'] == c].to_csv('Tower Data/Clean/'+c+'.csv', index=False)
    print('Compiled '+c+' successfully.')