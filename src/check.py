import datetime
import math
import numpy as np
import time
import process
import query

#constants
c = 299792458#m/s
k = 1.38*10**-23#j/k
t0 = 290#k
B = 6
R = 6378000#m radius of earth
Hiono = 300000#m
pheight = 20
plength = 70
pheading = 0


crx = [-149.958, 61.146] #lon, lat
ctx = [-155.04, 19.4792]
ca = [-148.61223, 60.38938]#lon,lat

#print(ca[1] == ((crx[0]-ctx[0])/(crx[1]-ctx[1]))*(ca[0]-crx[0])+crx[1])

class ordered_list:#list but all items are ordered
    items = [];
    def add(self, v, low = 0,high = None, key = lambda a,i: a[i]):
        if high == None:#check for first recursion
            high = len(self.items)-1
        if len(self.items) == 0:#check if empty
            self.items.append(v)
        #Binary search
        elif high >= low:#check if done searching
            mid = (high + low) // 2
            if self.items[mid] == v:#check if found same value
                self.items.insert(mid+1, v)
            elif key(self.items,mid,v):#check if too high
                self.add(v, low, mid - 1, key)
            else:#too low
                self.add(v, mid + 1, high, key)
        else:
            self.items.insert(low, v)
    def pop(self):
        self.items = self.items[1:]

#calculate intersection of greate circles
def intersect_greatcircle(A, B, C, D):#lat,lon
    
    p1_lat1 = A[0]
    p1_long1 = A[1]
    p1_lat2 = B[0]
    p1_long2 = B[1]

    p2_lat1 = C[0]
    p2_long1 = C[1]
    p2_lat2 = D[0]
    p2_long2 = D[1]

    # Convert degrees to radians
    p1_lat1_rad = ((math.pi * p1_lat1) / 180.0)
    p1_long1_rad = ((math.pi * p1_long1) / 180.0)
    p1_lat2_rad = ((math.pi * p1_lat2) / 180.0)
    p1_long2_rad = ((math.pi * p1_long2) / 180.0)
    p2_lat1_rad = ((math.pi * p2_lat1) / 180.0)
    p2_long1_rad = ((math.pi * p2_long1) / 180.0)
    p2_lat2_rad = ((math.pi * p2_lat2) / 180.0)
    p2_long2_rad = ((math.pi * p2_long2) / 180.0)

    # Put in polar coordinates
    x1 = math.cos(p1_lat1_rad) * math.cos(p1_long1_rad)
    y1 = math.cos(p1_lat1_rad) * math.sin(p1_long1_rad)
    z1 = math.sin(p1_lat1_rad)
    x2 = math.cos(p1_lat2_rad) * math.cos(p1_long2_rad)
    y2 = math.cos(p1_lat2_rad) * math.sin(p1_long2_rad)
    z2 = math.sin(p1_lat2_rad)
    cx1 = math.cos(p2_lat1_rad) * math.cos(p2_long1_rad)
    cy1 = math.cos(p2_lat1_rad) * math.sin(p2_long1_rad)
    cz1 = math.sin(p2_lat1_rad)
    cx2 = math.cos(p2_lat2_rad) * math.cos(p2_long2_rad)
    cy2 = math.cos(p2_lat2_rad) * math.sin(p2_long2_rad)
    cz2 = math.sin(p2_lat2_rad)

    # Get normal to planes containing great circles
    N1 = np.cross([x1, y1, z1], [x2, y2, z2])
    N2 = np.cross([cx1, cy1, cz1], [cx2, cy2, cz2])

    # Find line of intersection between two planes
    L = np.cross(N1, N2)

    # Find two intersection points
    X1 = L / np.sqrt(L[0]**2 + L[1]**2 + L[2]**2)
    X2 = -X1
    i_lat1 = math.asin(X1[2]) * 180./np.pi
    i_long1 = math.atan2(X1[1], X1[0]) * 180./np.pi
    i_lat2 = math.asin(X2[2]) * 180./np.pi
    i_long2 = math.atan2(X2[1], X2[0]) * 180./np.pi

    # Print results
    return[i_lat1, i_long1, i_lat2, i_long2]

def lg(v):
    return math.log(v,10)
    
def RCS(h,l,ra,f):
    return 4 * math.pi * h**2 * l**2 * math.sin(ra)**2 * f**2 / c**2

def Dgc(r,lat1,lon1,lat2,lon2):
    return r * math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1- lon2))

def Dhtotal(Dgctotal,n,h):
    return math.sqrt(Dgctotal + n**2 * h**2)

def SNR(p,f,rcs,rrx,rtx,n):#power transmitted(dB), frequency transmitted, RCS of target, distance from tx to target, distance from rx to target, number of hops
    return p + 40 * lg(c) - 40 * lg(f) + 10 * lg (rcs) - 50 * lg(4*math.pi) - 40 * lg(rtx)  - 40 * lg(rtx) - 10 * lg(k * t0 * B) - 5 * n
        
def Hr(a,latp,lonp,lats,lons):#heading of plane relative to north
    #relative heading
    A = lats
    B = latp
    C = math.sin(latp) * math.sin(lats) + math.cos(latp) * math.cos(lats) * math.cos(lons - lonp)
    s = math.acos((math.cos(A) - math.cos(B) * C) / (math.sin(B) * math.sin(math.acos(C))))
    return a - s

def first_node(a):#find higher node in a spot
    if a.get('rx_lat') > a.get('tx_lat'):
        return a.get('rx_lat')
    return a.get('tx_lat')

def last_node(a):#find lower node in a spot
    if a.get('rx_lat') < a.get('tx_lat'):
        return a.get('rx_lat')
    return a.get('tx_lat')
            
def comp(arr,a,b):#comparator or spot data structure
    return last_node(arr[a]) < last_node(b) #return if old node is higher

def shortest_hdist(lon1,lon2,maplength):
    l = min(lon1,lon2)
    r = max(lon1,lon2)
    return min(r-l,l-maplength[0]+maplength[1]-r)
            
#find points of intersection
def intersect_point_sp(d):#list of dict with SS_freq, SS_snr,SS_drift,id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
    st = time.process_time()    
    a = {}    
    #arranging by time
    for i in d:
        #adding new times
        if a.get(i.get('time')) == None: 
            a.update({i.get('time'): []})
        a.get(i.get('time')).append(i)
        
    #line sweep for all time stamps
    p = []
    for i in a.keys():#time
        a.get(i).sort(key=first_node, reverse=True)#sorting by highest higher node
        o = ordered_list()
        for j in a.get(i):#data
            if len(o.items) == 0:
                o.add(j,key = comp)
            else:
                for k in o.items:#open data
                    if last_node(k) > first_node(j):#removing closed spots
                        o.pop()
                    else:
                        #check for intersections
                        point = intersect_greatcircle([j.get('rx_lat'),j.get('rx_lon')], [j.get('tx_lat'),j.get('tx_lon')], [k.get('rx_lat'),k.get('rx_lon')], [k.get('tx_lat'),k.get('tx_lon')])
                        if (j.get('rx_lon') != k.get('rx_lon') or j.get('rx_lat') != k.get('rx_lat')) and (j.get('tx_lon') != k.get('tx_lon') or j.get('tx_lat') != k.get('tx_lat')) and (j.get('rx_lon') != k.get('tx_lon') or j.get('rx_lat') != k.get('tx_lat')) and (j.get('tx_lon') != k.get('rx_lon') or j.get('tx_lat') != k.get('rx_lat')):
                            if shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[1]-j.get('rx_lon')) and shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[1]-j.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[1]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[1]-k.get('tx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[1]-k.get('rx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[1]-k.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[1]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[1]-k.get('tx_lon')):
                                #adding point
                                p.append([point[0],point[1],j,k])
                                
                            if shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[3]-j.get('rx_lon')) and shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[3]-j.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[3]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[3]-k.get('tx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[3]-k.get('rx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[3]-k.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[3]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[3]-k.get('tx_lon')):
                                #adding point
                                p.append([point[2],point[3],j,k])
                #adding new openspot              
                o.add(j,key = comp)
    
    print("intersect_point_sp,",time.process_time()-st)
                
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    query.print_json('all','a',s,e,p,MR,ssT)
    
    return p

def intersect_point_lp(d):#list of dict with SS_freq, SS_snr,SS_drift,id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
    st = time.process_time()    
    a = {}    
    #arranging by time
    for i in d:
        #adding new times
        if a.get(i.get('time')) == None: 
            a.update({i.get('time'): []})
        a.get(i.get('time')).append(i)
    
    #O(N^2) but DP
    mem = {}
    p = []
    for i in a.keys():#time
        #prevent comparing with prev spot
        for j in range(len(a.get(i))):#data
            for k in range(j+1,len(a.get(i))):
                #check if alr know ans
                if mem.get([min(j.get('rx_lat'),j.get('rx_lon')),max(j.get('rx_lat'),j.get('rx_lon'))]).get([min(k.get('rx_lat'),k.get('rx_lon')),max(k.get('rx_lat'),k.get('rx_lon'))]) == None:
                    #calculating points on intersection
                    point = intersect_greatcircle([j.get('rx_lat'),j.get('rx_lon')], [j.get('tx_lat'),j.get('tx_lon')], [k.get('rx_lat'),k.get('rx_lon')], [k.get('tx_lat'),k.get('tx_lon')])
                    #point 1 with spot 1
                    rcs = RCS(pheight,plength,math.pi/2,j.get('frequency'))
                    Dgctotal1 = Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon'))
                    N1 = math.ceil(Dgctotal1/(2*R*math.acos(R/(R+300000))))
                    Rrx1 = (Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
                    Rtx1 = (Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
                    SNR11 = SNR(j.get('power'),j.get('frequency'),rcs,Rrx1,Rtx1,N1)
                
    
    print("intersect_point_lp,",time.process_time()-st)
                
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    #query.print_json('all','a',s,e,p,MR,ssT)
    
    #return p
                    

if __name__ == "__main__":  
    d = [{'rx_lat': 1, 'tx_lat': 9},{'rx_lat': -7, 'tx_lat': 3},{'rx_lat': 3, 'tx_lat': 0}]
    
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    #intersect_greatcircle([10,-70],[10,70],[10,-70],[10,-70])
    
    #A = [{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
    #A = process.anomalies('r', MR, ssT, s, e)
    
    print(intersect_point_lp([{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-09-01 02:00:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': -80, 'rx_lon': -80, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 80, 'tx_lon': 80, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-09-01 02:00:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': -80, 'rx_lon': -75, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 80, 'tx_lon': 80, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]))
    #intersect_point_sp(A)