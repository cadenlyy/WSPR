from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import math
import process
import datetime
import time

class plane:
    lat = 0
    lon = 0
    heading = 0
    ac = [0,0,0,0]
    def __init__(self,lat,lon,heading):
        self.lat = lat
        self.lon = lon
        self.heading = heading
        self.ac = [lon,lat,lon-1,lat-math.tan(heading*math.pi/180)]
    def plot(self):
        plt.annotate('', xy=(map(self.ac[0],self.ac[1])), xytext=(map(self.ac[2],self.ac[3])),arrowprops=dict(arrowstyle="->"))


map = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,
            llcrnrlon=-180,urcrnrlon=180,resolution='c')

map.drawcoastlines(linewidth=0.25)
map.drawcountries(linewidth=0.25)
map.fillcontinents()

map.drawmapboundary()

map.drawmeridians(np.arange(0,360,30))
map.drawparallels(np.arange(-90,90,30))

#aircraft
one = plane(48.84321,-148.64913,129)
lon = [-148.64913,-150.25799,-148.61223]
lat = [48.84321,51.01763,60.38938]

#spots
s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2024,9,1,10,0,0)
MR = datetime.timedelta(minutes = 180)

t = process.all_spots(MR,s,e)
#print(t)

#for i in points:
#    if i.get('lat') != None:
#        a = i.get('lon')
#        b = i.get('lat')
#    if (abs(a-crx[0]) < abs(crx[0]-ctx[0]) or abs(a-ctx[0]) < abs(crx[0]-ctx[0])) and (abs(b-crx[1]) < abs(crx[1]-ctx[1]) or abs(b-ctx[1]) < abs(crx[1]-ctx[1])): 
#        lon.append(a)
#        lat.append(b)

x, y = map(one.ac[0],one.ac[1])
x2, y2 = map(one.ac[2],one.ac[3])

one.plot()

#plot abnormallies
for i in t:
    if(int(i[8]) != int(i[12])+1 and int(i[8]) != int(i[12])-1 and int(i[8]) != int(i[12])):
        print(int(i[8]), int(i[7]), int(i[12]), int(i[11]))
        map.drawgreatcircle(i[8], i[7], i[12], i[11],  linewidth = 0.01, c = "red")

plt.title("2024-09-03 05:46:00")

print(time.process_time())

