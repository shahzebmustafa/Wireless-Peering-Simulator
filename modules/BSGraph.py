import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import os
from subprocess import call

def drawBSGraphs(state):

    stateBasestations = state.getAllBS()
    heatMap(stateBasestations, state)
    return

    stateShapes = gpd.read_file('Tower Data/2018_us_state_shapes/cb_2018_us_state_500k.shp')
    crs = {'init': 'epsg:4326'}
    stateShapes = stateShapes.to_crs("EPSG:4326")

    stateName = stateShapes.loc[stateShapes['STATEFP'] == state.id, "NAME"].iloc[0]
    # df.loc[df['B'] == 3, 'A'].iloc[0]
    
    colors = {"VERIZON": "black", "AT_T": "#5DADE2", "T_MOBILE": "#E71E85", "SPRINT": "#F2CA27"}
    for carrier in stateBasestations:
        for i in range(len(stateBasestations[carrier])):

            bs = stateBasestations[carrier][i]
            stateBasestations[carrier][i] = list(reversed(bs.location))
        
        # print(stateBasestations[carrier])
        BS_locations = list(map(Point, stateBasestations[carrier]))
        BS_locations_geo = gpd.GeoDataFrame(geometry=BS_locations)
        BS_locations_geo.set_crs("EPSG:4326")
        
        
        fig, ax = plt.subplots(figsize = (8, 6))
        stateShapes[stateShapes['STATEFP'] == state.id].plot(ax = ax, alpha=0.4, color='grey') 
        BS_locations_geo.plot(ax=ax, color=colors[carrier], marker=".")
        
        plt.axis('off')
        if stateName not in os.listdir("./Results/Figs/Maps/"):
            call(f"mkdir ./Results/Figs/Maps/{stateName}/", shell=True)
        plt.savefig(f"./Results/Figs/Maps/{stateName}/{carrier}.pdf", bbox_inches="tight")
        # plt.show()

    
    # 32.053292, -100.023998
    # plt.show()


def heatMap(stateBasestations, state):
    import folium
    from folium import plugins
    from subprocess import call

    MAP = folium.Map(location = [15,30], zoom_start = 2)

    for carrier in stateBasestations:
        for i in range(len(stateBasestations[carrier])):

            bs = stateBasestations[carrier][i]
            stateBasestations[carrier][i] = list(reversed(bs.location))
        
        # print(stateBasestations[carrier])
        BS_locations = list(map(Point, stateBasestations[carrier]))
        BS_locations_geo = gpd.GeoDataFrame(geometry=BS_locations)
        BS_locations_geo.set_crs("EPSG:4326")

        heat_data = [[point.xy[1][0], point.xy[0][0]] for point in BS_locations_geo.geometry ]

        plugins.HeatMap(heat_data, min_opacity=0.5, max_zoom=18, radius=5, blur=2, overlay=True, control=True, show=True).add_to(MAP)
        if not os.path.exists(f"./Results/Figs/Maps/{state.id}"):
            call(f"mkdir ./Results/Figs/Maps/{state.id}", shell=True)
        MAP.save(f"./Results/Figs/Maps/{state.id}/{carrier}.html")
        # break

