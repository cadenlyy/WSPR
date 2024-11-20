from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import math
import check
import datetime
import time
import process
import query

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
def fdrawgreatcircle(maplength,p1_lon, p1_lat,p2_lon,p2_lat, m, linewidth = 1, c = 'red', zorder = 1):
    
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
            if abs(lat1 - lmp[0]) < 1 and abs(lon1 - lmp[1]) < 3:
                if lat1 > lmp[0]:
                    lat1 += 1
                else:
                    lat1 -= 1
            m.drawgreatcircle(lon1, lat1, lmp[1], lmp[0], linewidth = linewidth, c = c, zorder = zorder)
        else:
            if abs(lat1 - lmp[2]) < 1 and abs(lon1 - lmp[3]) < 3:
                if lat1 > lmp[2]:
                    lat1 += 1
                else:
                    lat1 -= 1
            m.drawgreatcircle(lon1, lat1, lmp[3], lmp[2], linewidth = linewidth, c = c, zorder = zorder)
        if lmp[1] == maplength[0]:
            if abs(lat2 - rmp[0]) < 1 and abs(lon2 - rmp[1]) < 3:
                if lat2 > rmp[0]:
                    lat2 += 1
                else:
                    lat2 -= 1
            m.drawgreatcircle(lon2, lat2, rmp[1], rmp[0], linewidth = linewidth, c = c, zorder = zorder)
        else:
            if abs(lat2 - rmp[2]) < 1 and abs(lon2 - rmp[3]) < 3:
                if lat2 > rmp[2]:
                    lat2 += 1
                else:
                    lat2 -= 1
            m.drawgreatcircle(lon2, lat2, rmp[3], rmp[2], linewidth = linewidth, c = c, zorder = zorder)
    else:
        if abs(lat1 - lat2) < 1 and abs(lon1 - lon2) < 3:
            if lat1 > lat2:
                lat1 += 1
            else:
                lat1 -= 1
        m.drawgreatcircle(lon1, lat1, lon2, lat2, linewidth = linewidth, c = c, zorder = zorder)
            
#plot greatcircle for all data points


def p(f,c,t,lat1,lon1,lat2,lon2):#draw map and all plots
    st = time.process_time()
    #making map
    plt.figure(figsize=(100,60))
    m = Basemap(projection='cyl',llcrnrlat=lat1,urcrnrlat=lat2,
                llcrnrlon=lon1,urcrnrlon=lon2,resolution='c')
    
    m.drawcoastlines(linewidth=5)
    #map.drawmapboundary()
    
    m.drawmeridians(np.arange(0,360,30))
    m.drawparallels(np.arange(-90,90,30))
    
    #aircraft
    #one = plane(48.84321,-148.64913,129)
    
    #x, y = map(one.ac[0],one.ac[1])
    #x2, y2 = map(one.ac[2],one.ac[3])
    
    #one.plot()
   
    #ploting anomalies
    for i in t:
        if f == 'a':
            if c == i.get('time') and c == i.get('time'):
                p1_lat1 = i.get('rx_lat')
                p1_long1 = i.get('rx_lon')
                p1_lat2 = i.get('tx_lat')
                p1_long2 = i.get('tx_lon')
                fdrawgreatcircle([lon1, lon2], p1_long1, p1_lat1, p1_long2, p1_lat2, m, linewidth= 10, c='blue',zorder=1)
        elif f == 'p&l':
            if c == i[2].get('time') and c == i[3].get('time'):
                p1_lat1 = i[2].get('rx_lat')
                p1_long1 = i[2].get('rx_lon')
                p1_lat2 = i[2].get('tx_lat')
                p1_long2 = i[2].get('tx_lon')
                fdrawgreatcircle([lon1, lon2], p1_long1, p1_lat1, p1_long2, p1_lat2, m, linewidth= 10, c='blue',zorder=1)
                
                p2_lat1 = i[3].get('rx_lat')
                p2_long1 = i[3].get('rx_lon')
                p2_lat2 = i[3].get('tx_lat')
                p2_long2 = i[3].get('tx_lon')
                fdrawgreatcircle([lon1, lon2], p2_long1, p2_lat1, p2_long2, p2_lat2, m, linewidth= 10, c='blue',zorder=1)
            
                plt.plot([i[1]], [i[0]], marker=".", markersize=50, c = 'red',zorder=3)
                plt.plot([i[2].get('rx_lon'),i[2].get('tx_lon'),i[3].get('rx_lon'),i[3].get('tx_lon')],[i[2].get('rx_lat'),i[2].get('tx_lat'),i[3].get('rx_lat'),i[3].get('tx_lat')], linestyle='None', marker=".", markersize=50, c = 'green',zorder=2)
                
                #print(i)
                
    plt.title(f+c, fontsize = 100)
    #saving plot as img
    plt.savefig("C:/Users/Lyiyang1/Desktop/wspr/data/plot/"+f+"/"+c[0:10]+'_'+c[11:13]+'-'+c[14:16]+'-'+c[17:19]+'_'+str(lat1)+'_'+str(lon1)+'_'+str(lat2)+'_'+str(lon2)+".png", format="png", dpi=100)
    plt.show()
    plt.clf()#clear plot
    
    print("plot,",time.process_time()-st)#check is slow
    
if __name__ == "__main__":  
    ts = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    te = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    #p('p&l',s,e,query.read_json('all_points', ts, te, MR))
    #p('p&l',s,e,check.intersect_point(process.anomalies('r', MR, ts, te)))
    p('a',"2024-09-01 03:00:00",process.anomalies('r',MR,ssT,ts,te), -90, -60, -30, 60)
    #p('p&l',s,e,[[-35.83848798770491, 55.91852851448542, {'SS_freq': -348619.2288304247, 'SS_snr': 29.677178697402976, 'SS_drift': 0, 'id': '8256616381', 'time': '2024-09-01 03:52:00', 'band': 18, 'rx_sign': 'VK5TC', 'rx_lat': -35.062, 'rx_lon': 138.542, 'rx_loc': 'PF94gw', 'tx_sign': 'VK4BA', 'tx_lat': -27.521, 'tx_lon': 152.958, 'tx_loc': 'QG62', 'distance': 1604, 'azimuth': 235, 'rx_azimuth': 62, 'frequency': 18106186, 'power': 23, 'snr': -23, 'drift': 0, 'version': '2.6.1', 'code': 1}, {'SS_freq': -5993775.392985822, 'SS_snr': 46.565621163477765, 'SS_drift': 19527068.560821768, 'id': '8256619589', 'time': '2024-09-01 03:52:00', 'band': 21, 'rx_sign': 'KFS/SW', 'rx_lat': 37.396, 'rx_lon': -122.375, 'rx_loc': 'CM87tj', 'tx_sign': 'ZL3TKI', 'tx_lat': -43.562, 'tx_lon': 172.625, 'tx_loc': 'RE66hk', 'distance': 11130, 'azimuth': 47, 'rx_azimuth': 221, 'frequency': 21096101, 'power': 23, 'snr': -3, 'drift': 0, 'version': 'WD_3.2.2', 'code': 1}]])
    

