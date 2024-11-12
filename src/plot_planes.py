import matplotlib.pyplot as plt
import adsb_2024_9_1_000000

data = adsb_2024_9_1_000000.d.get('aircraft')
lon = []
lat = []

for i in data:
    lon.append(i.get('lon'))
    lat.append(i.get('lat'))
    
plt.figure(figsize=(100,60))

plt.scatter(lon, lat, linewidths=0.1)