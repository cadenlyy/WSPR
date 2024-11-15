import datetime
import math
import numpy as np
import time
import process

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
    if (abs(i_lat1 - p1_lat1) < abs(i_lat2 - p1_lat1)):
        print(time.process_time())#check process time
        return[i_lat1, i_long1]
    else:
        print(time.process_time())#check process time
        return[i_lat2, i_long2]
        
    
        
def first_node(a):#find higher node in a spot
    if a.get('rx_lat') > a.get('tx_lat'):
        print(time.process_time())
        return a.get('rx_lat')
    print(time.process_time())#check process time
    return a.get('tx_lat')

def last_node(a):
    if a.get('rx_lat') < a.get('tx_lat'):
        print(time.process_time())
        return a.get('rx_lat')
    print(time.process_time())#check process time
    return a.get('tx_lat')
            
def comp(arr,a,b):#comparator or spot data structure
    #find lower nodes
    if arr[a].get('rx_lat') < arr[a].get('tx_lat'):
        ov = arr[a].get('rx_lat')
    else:
        ov = arr[a].get('tx_lat')
    if b.get('rx_lat') < b.get('tx_lat'):
        nv = b.get('rx_lat')
    else:
        nv = b.get('tx_lat')
    return ov < nv #return if old node is higher
            
#find points of intersection
def intersect_point(d):#list of dict with SS_freq, SS_snr,SS_drift,id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
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
                    if last_node(k) < first_node(j):#removing closed spots
                        o.pop()
                    else:
                        #check for intersections
                        I = intersect_greatcircle([j.get('rx_lat'),j.get('rx_lon')], [j.get('tx_lat'),j.get('tx_lon')], [k.get('rx_lat'),k.get('rx_lon')], [k.get('tx_lat'),k.get('tx_lon')])
                        if abs(j.get('rx_lon')-j.get('tx_lon')) > abs(I[1]-j.get('rx_lon')) and abs(j.get('rx_lon')-j.get('tx_lon')) > abs(I[1]-j.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(I[1]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(I[1]-k.get('tx_lon')):
                            #adding new openspot
                            p.append([i,j,k])
                        o.add(j,key = comp)
    print(p)
                    
                

    print(time.process_time())
    
if __name__ == "__main__":  
    d = [{'rx_lat': 1, 'tx_lat': 9},{'rx_lat': -7, 'tx_lat': 3},{'rx_lat': 3, 'tx_lat': 0}]
    
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,10,0,0)
    MR = datetime.timedelta(minutes = 180)
    
    #A = [{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
    A = process.anomalies('r', MR, s, e)
    
    intersect_point(A)
    