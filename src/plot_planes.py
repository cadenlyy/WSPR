from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import math
import check
import datetime
import time
import process

map = Basemap(projection='cyl',llcrnrlat=45,urcrnrlat=60,
            llcrnrlon=-10,urcrnrlon=10,resolution='c')

class plane: #maintain the necessary details for each plane
    lat = 0
    lon = 0
    heading = 0
    ac = [0,0,0,0]#coordinates to plot on map
    def __init__(self,lat,lon,heading):
        self.lat = lat
        self.lon = lon
        self.heading = heading
        self.ac = [lon,lat,lon-1,lat-math.tan(heading*math.pi/180)]
    def plot(self):#plot arrow on map
        plt.annotate('', xy=(map(self.ac[0],self.ac[1])), xytext=(map(self.ac[2],self.ac[3])),arrowprops=dict(arrowstyle="->"))

#"fixing" bug in drawgreatcircle
def fdrawgreatcircle(maplength,p1_lon, p1_lat,p2_lon,p2_lat, linewidth = 1, c = 'red'):
    
    #checking for left most node
    if p1_lon > p2_lon:
        lat1 = p2_lat
        lon1 = p2_lon
        lat2 = p1_lat
        lon2 = p1_lon
    else:
        lat1 = p1_lat
        lon1 = p1_lon
        lat2 = p2_lat
        lon2 = p2_lon
    #check if it crosses boarder of map
    if lon1-maplength[0]+maplength[1]-lon2 <= lon2-lon1:
        lmp = check.intersect_greatcircle([lat1, lon1], [lat2,lon2], [-90, maplength[0]], [90, maplength[0]])
        rmp = check.intersect_greatcircle([lat1, lon1], [lat2,lon2], [-90, maplength[1]], [90, maplength[1]])
        if lmp[1] == maplength[0]:
            map.drawgreatcircle(lon1, lat1, lmp[1], lmp[0], linewidth = linewidth, c = c)
        else:
            map.drawgreatcircle(lon1, lat1, lmp[3], lmp[2], linewidth = linewidth, c = c)
        if lmp[1] == maplength[0]:
            map.drawgreatcircle(lon2, lat2, rmp[1], rmp[0], linewidth = linewidth, c = c)
        else:
            map.drawgreatcircle(lon2, lat2, rmp[3], rmp[2], linewidth = linewidth, c = c)
    else:
        map.drawgreatcircle(lon1, lat1, lon2, lat2, linewidth = linewidth, c = c)
            
#plot greatcircle for all data points
def plotgreatcircle_abnomaly(t):
    for i in t:
        if(int(i[8]) != int(i[12])+1 and int(i[8]) != int(i[12])-1 and int(i[8]) != int(i[12])):
            map.drawgreatcircle(i[8], i[7], i[12], i[11],  linewidth = 0.01, c = "red")

def p():#draw map and all plots
    
    map.drawcoastlines(linewidth=0.25)
   # map.drawmapboundary()
    
    map.drawmeridians(np.arange(0,360,30))
    map.drawparallels(np.arange(-90,90,30))
    
    #aircraft
    #one = plane(48.84321,-148.64913,129)
    
    #x, y = map(one.ac[0],one.ac[1])
    #x2, y2 = map(one.ac[2],one.ac[3])
    
    #one.plot()
    
    #spots
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,10,0,0)
    MR = datetime.timedelta(minutes = 180)
    
    t = check.intersect_point(process.anomalies('r', MR, s, e))
    
    #plotgreatcircle_abnomal(t)

    for j in range (10):
        i = t[j]
        p1_lat1 = i[2].get('rx_lat')
        p1_long1 = i[2].get('rx_lon')
        p1_lat2 = i[2].get('tx_lat')
        p1_long2 = i[2].get('tx_lon')
        if int(p1_lat1) == int(p1_lat2):
            p1_lat1+=1
        if int(p1_long1) == int(p1_long2):
            p1_long1+=1
        fdrawgreatcircle([-180, 180], p1_long1, p1_lat1, p1_long2, p1_lat2)
        
        p2_lat1 = i[3].get('rx_lat')
        p2_long1 = i[3].get('rx_lon')
        p2_lat2 = i[3].get('tx_lat')
        p2_long2 = i[3].get('tx_lon')
        if int(p2_lat1) == int(p2_lat2):
            p2_lat1+=1
        if int(p2_long1) == int(p2_long2):
            p2_long1+=1
        fdrawgreatcircle([-180, 180], p2_long1, p2_lat1, p2_long2, p2_lat2)
    
        plt.scatter([i[1]], [i[0]])

    #plt.title("2024-09-03 05:46:00")
    plt.show()
    
    print("plot,",time.process_time())
    
if __name__ == "__main__":  
    p()

