import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import os
from subprocess import call

def drawBSGraphs(state):

    stateBasestations = state.getAllBS()
    heatMap(stateBasestations, state)
    


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

