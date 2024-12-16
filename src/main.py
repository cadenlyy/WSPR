from ctypes.wintypes import LPDWORD, LPFILETIME
from xmlrpc.client import DateTime
import process
import query
import plot_data
import check
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import os
import math
import temp

#constants
c = 299792458#m/s
k = 1.38*10**-23#j/k
t0 = 290#k
B = 6
R = 6378000#m radius of earth
Hiono = 100000#m
pheight = 20
plength = 70
pheading = 0
SPN = 4.9406564584124654e-324
int_MAX = 2**63-1
tTransmittion = 110.6#S transmittion time 
fSample = 12000
N = 30 #number of samples

#checking for short path by plotting
'''
s = datetime.datetime(2022,11,1,15,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2022,11,1,23,59,0)
#file path and naming
base_dir = "C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\json"
filename = 's.txt'
abs_file = os.path.join(base_dir, filename)
with open(abs_file, 'r') as file: 
    data = file.read()
tx = ''
rx = ''
tor = 0
temp = 0;
nos = [0]
for i in range(len(data)):
    if temp > 0:
        temp -= 1
        continue
    if data[i] == '\n':
        #q = query.wsprlive_get('*','rx',str(s),str(e),rx,tx)
        #query.print_json('pair', 'r', s, e, q, rx = rx, tx = tx)
        q = query.read_json('pair','r',s,e,rx=rx,tx=tx)
        if len(q) == 0:
            print(rx,tx)
            tx = ''
            rx = ''
            continue

        Dgctotal11 = 2 * math.pi * R - check.Dgc(R,q[0].get('rx_lat'),q[0].get('rx_lon'),q[0].get('tx_lat'),q[0].get('tx_lon'))
        N11 = math.ceil(Dgctotal11/(2*R*math.acos(R/(R+300000))))
        lpd = check.Dhtotal(Dgctotal11, N11, Hiono)
        
        lpsnr = check.SNR(q[0].get('power'),q[0].get('frequency'),1,lpd,1,N11)
        #print(lpsnr,Dgctotal11,N11,lpd)
        '''

'''
        plt.figure(figsize=(100,60))
        m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='c')
        m.drawcoastlines(linewidth=5)
        m.drawmeridians(np.arange(0,360,30))
        m.drawparallels(np.arange(-90,90,30))
        plot_planes.fdrawgreatcircle([-180,180], q[0].get('rx_lon'), q[0].get('rx_lat'),  q[0].get('tx_lon'),  q[0].get('tx_lat'), m, linewidth= 10)
        plt.title(q[0].get('rx_sign')+'_'+q[0].get('tx_sign')+'_'+str(len(q))+'_'+str(lpsnr)+'_'+str(Dgctotal11)+'_'+str(q[0].get('power'))+'_'+str(q[0].get('frequency')), fontsize = 100)
        
        base_dir = "C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\plot"
        filename = str(i)+'.png'
        abs_file = os.path.join(base_dir, filename)
        plt.savefig(abs_file, format="png", dpi=100)
        plt.close()
        '''
'''
        print(len(q))
        if lpsnr > -30 and len(q) > nos[0] and len(q) < 214:
            nos = [len(q),q[0].get('rx_sign'),q[0].get('tx_sign'),q[0].get('rx_lat'),q[0].get('rx_lon'),q[0].get('tx_lat'),q[0].get('tx_lon')]
        
        tx = ''
        rx = ''
        tor = 0
        continue
    elif  data[i:i+4] == ' to ':
        tor = 1
        temp = 3
        continue
    if tor:
        rx += data[i]
    else:
        tx += data[i]
print(nos)
'''

#query details
s = datetime.datetime(2022,11,1,0,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2022,11,1,23,59,0)
qf = 'pair'
rx = 'KFS'
tx = 'KG5QFD'
#query.wspr_to_json(qf, s, e)
#q = query.wsprlive_get('*','rx',s,e,rx,tx)

#processing details
MR = datetime.timedelta(minutes = 180)
ssT = 0.5 #Minimum standard score
pf = 'r'#r(read from json), t(test case), q(query from wsprnet)

#check details
#a = query.read_json('all','a',s,e,MR,ssT)
a = process.anomalies_freqsnr(pf,MR,ssT,s,e,rx,tx)
#process.print_csv(qf, 'a', s, e, MR, ssT, a, rx, tx)
mSNR = -30 #minimun SNR in dB
clat1 = -60
clon1 = 120
clat2 = 0
clon2 = 180

#plot details
'''
mf = 'p'#a(all anomalies, takes in data from anomalies) i (intersecting lines and corresponding points, takes data from intersect_point) p(only points of intersection,  takes data from intersect_point) r(all spots)
lat1 = -90#map lowest lat
lon1 = -180#map lowest lon
lat2 = 90#map highest lat
lon2 = 180#map highest lon
c = "2024-09-01 03:00:00"#timestamp of plot
#p = check.intersect_point_sp(a,s,e,MR,ssT)#short path calculations only
p = check.intersect_point_lp(a,mSNR,s,e,MR,ssT)#consider long path and check using SNR calculations
'''

#plot for multiple time stamps
'''
for m in range(0,60,2):    
    if(m < 10):
        c = '2024-09-01 03:0'+str(m)+':00'
    else:
        c = '2024-09-01 03:'+str(m)+':00'
    plot_data.p(p,mf,c, MR, ssT, lat1, lon1, lat2, lon2)
    '''

#histogram for SNR
v = []
for i in a:
    if abs(i.get('snr')) < 0.5:     
        v.append(i.get('snr'))

d = plot_data.subtract_trend(v,50)
plot_data.fit(d, 100, 100, s, e, rx, tx, n = 'sub')
#plot_data.fit(v, 100, 100, s, e, rx, tx, n = 'presub')

#histogram for distance
'''
a = temp.d
v = []
for i in a:
    v.append({'distance':i[0]})
    
process.print_csv('all','dist',s,e,MR,ssT,v)

#d = plot_data.subtract_trend(v,50)
#plot_data.fit(d, 100, 100, s, e, n = 'sub')
#plot_data.fit(v, 100, 100, s, e, n = 'dist')
'''

#cross check with flight data
'''
#points = check.intersect_point_lp(a,mSNR,s,e,MR,ssT)#consider long path and check using SNR calculations
points = query.read_json('all','p',s,e,MR,ssT)
p = check.read_bst("20241204_091202")
#p = check.read_bst("1")
print(check.crosscheck(points,p,clat1,clon1,clat2,clon2, s, e))
'''

#example of considering lp and sp
'''
plt.figure(figsize=(100,60))
m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,
            llcrnrlon=-180,urcrnrlon=180,resolution='c')

m.drawcoastlines(linewidth=5)
    
m.drawmeridians(np.arange(0,360,30))
m.drawparallels(np.arange(-90,90,30))

lon1 = [-80,-40]
lat1 = [20,0]

plot_data.fulldrawgreatcircle([-180,180],lon1[0],lat1[0],lon1[1],lat1[1],m,linewidth = 10, c = 'b',zorder = 1)
plot_data.fdrawgreatcircle([-180,180],lon1[0],lat1[0],lon1[1],lat1[1],m,linewidth = 10,zorder = 2)
plt.plot(lon1[0], lat1[0], marker=".", markersize=50, c = 'green',zorder=3)
plt.plot(lon1[1], lat1[1], marker=".", markersize=50, c = 'green',zorder=3)

lon2 = [-60,-30]
lat2 = [-20,25]

plot_data.fulldrawgreatcircle([-180,180],lon2[0],lat2[0],lon2[1],lat2[1],m,linewidth = 10, c = 'b',zorder = 1)
plot_data.fdrawgreatcircle([-180,180],lon2[0],lat2[0],lon2[1],lat2[1],m,linewidth = 10,zorder = 2)
plt.plot(lon2[0], lat2[0], marker=".", markersize=50, c = 'green',zorder=3)
plt.plot(lon2[1], lat2[1], marker=".", markersize=50, c = 'green',zorder=3)

points = check.intersect_greatcircle([lat1[0],lon1[0]],[lat1[1],lon1[1]],[lat2[0],lon2[0]],[lat2[1],lon2[1]])
plt.plot(points[1], points[0], marker=".", markersize=50, c = 'black',zorder=4)
plt.plot(points[3], points[2], marker=".", markersize=50, c = 'black',zorder=4)

#plt.show()
base_dir = "C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\plot"
filename = "example of considering both lp and sp.png"
abs_file = os.path.join(base_dir, filename)
plt.title(filename, fontsize = 100)
plt.savefig(abs_file, format="png", dpi=100)
'''

#calulating number of points
'''
nop = 0
for i in p:
    if i[2].get('time') == "2024-09-01 03:32:00":
        nop += 1
print(nop)
'''

#query.wspr_to_json('all', s, e, MR, 'KL3RR', 'VE7AHT')
#process.one_pair(MR, s, e, 'KL3RR', 'VE7AHT', 'r')
#print(check.intersect_greatcircle([37.396,-122.375], [-27.521,152.958], [-41.021,173.042], [38.479,-123.042]))