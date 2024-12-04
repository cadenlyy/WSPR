import process
import query
import plot_planes
import check
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

#query details
s = datetime.datetime(2022,11,1,16,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2022,11,3,22,40,0)
qf = 'pair'
rx = 'W3LLA'
tx = 'WA5CB'
query.wspr_to_json(qf, s, e, rx, tx)
#q = query.wsprlive_get('*','rx',s,e,rx,tx)

#processing details
MR = datetime.timedelta(minutes = 180)
ssT = 0.5#Minimum standard score
pf = 'r'#r(read from json), t(test case), q(query from wsprnet)


#check details
a = process.anomalies_freqsnr(pf,MR,ssT,s,e, rx, tx)
#process.print_csv(qf, 'a', s, e, MR, ssT, a, rx, tx)
mSNR = -30#minimun SNR
clat1 = -60
clon1 = 120
clat2 = 0
clon2 = 180
p = check.read_bst("1")


'''
#plot details
mf = 'p'#a(all anomalies, takes in data from anomalies) i (intersecting lines and corresponding points, takes data from intersect_point) p(only points of intersection,  takes data from intersect_point) r(all spots)
lat1 = -90#map lowest lat
lon1 = -180#map lowest lon
lat2 = 90#map highest lat
lon2 = 180#map highest lon
c = "2024-09-01 03:00:00"#timestamp of plot
#p = check.intersect_point_sp(a)#short path calculations only
p = check.intersect_point_lp(a,mSNR)#consider long path and check using SNR calculations
'''

'''
# plot for multiple time stamps
for m in range(0,60,2):
    if(m < 10):
        c = '2024-09-01 03:0'+str(m)+':00'
    else:
        c = '2024-09-01 03:'+str(m)+':00'
    plot_planes.p(p,mf,c, MR, ssT, lat1, lon1, lat2, lon2)
'''

'''
#cross check with flight data
print(check.crosscheck(a,p,clat1,clon1,clat2,clon2))
'''

#query.wspr_to_json('all', s, e, MR, 'KL3RR', 'VE7AHT')
#process.one_pair(MR, s, e, 'KL3RR', 'VE7AHT', 'r')
#print(check.intersect_greatcircle([37.396,-122.375], [-27.521,152.958], [-41.021,173.042], [38.479,-123.042]))