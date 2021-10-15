import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd

df = pd.read_csv('./Tower Data/Compressed/VERIZON.csv')
df = df[['lat','lon']]




fig = plt.figure(figsize=(8, 8))
m = Basemap(projection='lcc', resolution=None,
            width=8E6, height=4E6, 
            lat_0=45, lon_0=-100,)
m.etopo(scale=0.5, alpha=0.5)

# Map (long, lat) to (x, y) for plotting
# i = 0
for index, row in df.iterrows():
	# print(row['lat'], row['lon'])
	# plt.plot(row['lon'], row['lat'],marker='o', markersize=5)
	x, y = m(row['lon'], row['lat'])
	plt.plot(x, y, '.k', markersize=1)


# plt.show()
plt.title("BS Location Map: VERIZON")
plt.savefig('./Tower Data/Figs/VERIZON.png')