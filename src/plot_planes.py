from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import math
import check
import datetime
import time
import process
import query
plt.figure(figsize=(100,60))
map = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,
            llcrnrlon=-180,urcrnrlon=180,resolution='c')

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
def fdrawgreatcircle(maplength,p1_lon, p1_lat,p2_lon,p2_lat, linewidth = 1, c = 'red', zorder = 1):
    
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
            map.drawgreatcircle(lon1, lat1, lmp[1], lmp[0], linewidth = linewidth, c = c, zorder = zorder)
        else:
            map.drawgreatcircle(lon1, lat1, lmp[3], lmp[2], linewidth = linewidth, c = c, zorder = zorder)
        if lmp[1] == maplength[0]:
            map.drawgreatcircle(lon2, lat2, rmp[1], rmp[0], linewidth = linewidth, c = c, zorder = zorder)
        else:
            map.drawgreatcircle(lon2, lat2, rmp[3], rmp[2], linewidth = linewidth, c = c, zorder = zorder)
    else:
        map.drawgreatcircle(lon1, lat1, lon2, lat2, linewidth = linewidth, c = c, zorder = zorder)
            
#plot greatcircle for all data points
def plotgreatcircle_abnomaly(t):
    for i in t:
        if(int(i[8]) != int(i[12])+1 and int(i[8]) != int(i[12])-1 and int(i[8]) != int(i[12])):
            map.drawgreatcircle(i[8], i[7], i[12], i[11],  linewidth = 0.01, c = "red")

def p():#draw map and all plots
    st = time.process_time()
    map.drawcoastlines(linewidth=5)
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
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    
    t = query.read_json('all_points', s, e, MR)
    #t = check.intersect_point(process.anomalies('r', MR, s, e))
    
    #plotgreatcircle_abnomal(t)

    c = None
    for i in t:
        if c != '2024-09-01 03:02:00':
            c = i[2].get('time')
            
        elif c == i[2].get('time'):
            p1_lat1 = i[2].get('rx_lat')
            p1_long1 = i[2].get('rx_lon')
            p1_lat2 = i[2].get('tx_lat')
            p1_long2 = i[2].get('tx_lon')
            if int(p1_lat1) == int(p1_lat2):
                p1_lat1+=1
            if int(p1_long1) == int(p1_long2):
                p1_long1+=1
            fdrawgreatcircle([-180, 180], p1_long1, p1_lat1, p1_long2, p1_lat2, linewidth= 10, c='blue',zorder=1)
            
            p2_lat1 = i[3].get('rx_lat')
            p2_long1 = i[3].get('rx_lon')
            p2_lat2 = i[3].get('tx_lat')
            p2_long2 = i[3].get('tx_lon')
            if int(p2_lat1) == int(p2_lat2):
                p2_lat1+=1
            if int(p2_long1) == int(p2_long2):
                p2_long1+=1
            fdrawgreatcircle([-180, 180], p2_long1, p2_lat1, p2_long2, p2_lat2, linewidth= 10, c='blue',zorder=1)
        
            plt.plot([i[1]], [i[0]], marker=".", markersize=50, c = 'red',zorder=2)
            if i[0] == -15.728999999999997:
                print(i)
            
        else:
            break

    plt.title(c, fontsize = 100)
    plt.savefig("C:/Users/Lyiyang1/Desktop/wspr/data/plot/"+c[0:10]+'_'+c[11:13]+'-'+c[14:16]+'-'+c[17:19]+".png", format="png", dpi=100)
    plt.show()
    
    print("plot,",time.process_time()-st)
    
if __name__ == "__main__":  
    p()

