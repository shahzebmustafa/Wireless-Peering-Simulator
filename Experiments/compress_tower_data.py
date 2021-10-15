
import pandas as pd
import os


for root, dirs, files in os.walk('./Tower Data/Clean/'):

    for dFile in files:

        if dFile != ".DS_Store":

            df = pd.read_csv(os.path.join(root,dFile))            
            df['lat'] = df['lat'].round(decimals=1)
            df['lon'] = df['lon'].round(decimals=1)



            # testDF = df[(df["lon"] == -100.8) & (df["lat"] == 36.47) | (df["lon"] == -100.7) & (df["lat"] == 36.16)]
            # print(testDF)
            # testDF["lat"] = testDF['lat'].round(decimals=1)
            # print(testDF)
            # testDF = testDF.drop_duplicates(subset=['lat', 'lon'])
            # print(testDF)

            df = df.drop_duplicates(subset=['lat', 'lon','radio'])
            # print(df.head())

            # testDF = df[(df["lon"] == -100.8) & (df["lat"] == 36.5) | (df["lon"] == -100.7) & (df["lat"] == 36.2)]
            # print(testDF)


            df.to_csv('./Tower Data/Compressed/'+dFile, index=False)
