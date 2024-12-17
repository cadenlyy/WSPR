from ast import Num
import datetime
import math
from operator import ne
import numpy as np
import time
import process
import query
import os
import constants


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
    return 4 * math.pi * h**2 * l**2 * math.sin(ra)**2 * f**2 / constants.c**2

def Dgc(r,lat1,lon1,lat2,lon2):#greatcircle distance between 2 points
    #print(r,lat1,lon1,lat2,lon2)
    if r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180)) != 0:
        return r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180))
    return 1e-316#smallest float u can return in sypder

def Dhtotal(Dgctotal,n,h,r):
    return math.sqrt(2 * r * (r + h) * (1 - math.cos(Dgctotal / (2 * r * n))) + h**2)

def SNR(p,f,rcs,rrx,rtx,n):#power transmitted(dB), frequency transmitted, RCS of target, distance from tx to target, distance from rx to target, number of hops
    noise = 10 * lg(constants.k * constants.t0 * constants.B)
    signal = p - 30 + 20 * lg(constants.c) - 20 * lg(f) + 10 * lg(rcs) - 30 * lg(4*math.pi) - 20 * lg(rrx) - 20 * lg(rtx) + 10 * lg(constants.N)
    #print(signal, noise, losses)
    return signal - noise 
        
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
def intersect_point_sp(d,s,e,MR,ssT):#list of dict with SS_freq, SS_snr,SS_drift,id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
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
                            if shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[1]-j.get('rx_lon')) and shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[1]-j.get('tx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[1]-k.get('rx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[1]-k.get('tx_lon')):
                                #adding point
                                p.append([point[0],point[1],j,k])
                                
                            if shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[3]-j.get('rx_lon')) and shortest_hdist(j.get('rx_lon'), j.get('tx_lon'), [-180, 180]) > abs(point[3]-j.get('tx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[3]-k.get('rx_lon')) and shortest_hdist(k.get('rx_lon'), k.get('tx_lon'), [-180, 180]) > abs(point[3]-k.get('tx_lon')):
                                #adding point
                                p.append([point[2],point[3],j,k])
                #adding new openspot              
                o.add(j,key = comp)
    
    print("intersect_point_sp,",time.process_time()-st)
                
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    query.print_json('all','psp',s,e,p,MR,ssT)
    
    return p

def read_bst(filename):
    #date, time, ABSD S-Mode 1, S-Mode2, callsign, Departure airport code, ?, altitude, altitude, lat, lon, ?, ?, ?, ?, ?, ?, ?, reportor, aircraft type code, aircraft registration, ?, destination airport code, flight number
    st = time.process_time()
    base_dir = constants.dir+'data\\bst'
    filename += '.bst'
    abs_file = os.path.join(base_dir, filename)
    #reading from json
    with open(abs_file, 'r') as file: 
        data = file.read()
        d = ""
        pd = []
        o = []
        for i in data:
            if i == "\n":
                pd.append(d)
                d = ""
                o.append(pd)
                pd = []
            elif i == ',':
                pd.append(d)
                d = ""
            elif i != '"':
                d+=i
        o.append(pd)
        print("read_bst,",time.process_time()-st)
    return o
    

def intersect_point_lp(d, mSNR, s, e, MR, ssT):#list of dict with SS_freq, SS_snr,SS_drift,id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
        
    st = time.process_time()    
    a = {}    
    #arranging by time
    for i in d:
        #adding new times
        if a.get(i.get('time')) == None: 
            a.update({i.get('time'): []})
        a.get(i.get('time')).append(i)
    
    #O(N^2) but DP
    '''mem = {}'''
    p = []
    for i in a.keys():#time
        #prevent comparing with prev spot
        for j in range(len(a.get(i))):#data
            for k in range(j+1,len(a.get(i))):
                '''
                #check if alr know ans
                if mem.get(j).get(k) == None:
                    '''
                s1 = a.get(i)[j]
                s2 = a.get(i)[k]
                #check that tx and rx are not repeated
                if (s1.get('rx_lon') != s2.get('rx_lon') or s1.get('rx_lat') != s2.get('rx_lat')) and (s1.get('tx_lon') != s2.get('tx_lon') or s1.get('tx_lat') != s2.get('tx_lat')) and (s1.get('rx_lon') != s2.get('tx_lon') or s1.get('rx_lat') != s2.get('tx_lat')) and (s1.get('tx_lon') != s2.get('rx_lon') or s1.get('tx_lat') != s2.get('rx_lat')):
                    #calculating points on intersection
                    point = intersect_greatcircle([s1.get('rx_lat'),s1.get('rx_lon')], [s1.get('tx_lat'),s1.get('tx_lon')], [s2.get('rx_lat'),s2.get('rx_lon')], [s2.get('tx_lat'),s2.get('tx_lon')])
                    
                    rcs1 = RCS(constants.pheight,constants.plength,math.pi/2,s1.get('frequency'))
                    rcs2 = RCS(constants.pheight,constants.plength,math.pi/2,s2.get('frequency'))
                    #point 1 with spot 1
                    #checking if it point on long path or short path
                    if shortest_hdist(s1.get('rx_lon'), s1.get('tx_lon'), [-180, 180]) > abs(point[1]-s1.get('rx_lon')) and shortest_hdist(s1.get('rx_lon'), s1.get('tx_lon'), [-180, 180]) > abs(point[1]-s1.get('tx_lon')):
                        Dgctotal11 = Dgc(constants.R,s1.get('rx_lat'),s1.get('rx_lon'),s1.get('tx_lat'),s1.get('tx_lon'))
                    else:
                        Dgctotal11 = 2 * math.pi * constants.R - Dgc(constants.R,s1.get('rx_lat'),s1.get('rx_lon'),s1.get('tx_lat'),s1.get('tx_lon'))
                    N11 = math.ceil(Dgctotal11/(2*constants.R*math.acos(constants.R/(constants.R+300000))))
                    #ensuring distance from rx to target is the correct 1
                    if shortest_hdist(point[1], s1.get('tx_lon'), [-180, 180]) > abs(s1.get('rx_lon')-s1.get('tx_lon')) and shortest_hdist(point[1], s1.get('tx_lon'), [-180, 180]) > abs(s1.get('rx_lon')-point[1]):
                        Rrx11 = (Dgc(constants.R,point[0],point[1],s1.get('rx_lat'),s1.get('rx_lon'))/Dgctotal11)*Dhtotal(Dgctotal11, N11, constants.constants.Hiono, constants.R)
                    else:
                        Rrx11 = ((2 * math.pi * constants.R - Dgc(constants.R,point[0],point[1],s1.get('rx_lat'),s1.get('rx_lon')))/Dgctotal11)*Dhtotal(Dgctotal11, N11, constants.constants.Hiono, constants.R)
                    if shortest_hdist(point[1], s1.get('rx_lon'), [-180, 180]) > abs(s1.get('tx_lon')-s1.get('rx_lon')) and shortest_hdist(point[1], s1.get('rx_lon'), [-180, 180]) > abs(s1.get('tx_lon')-point[1]):
                        Rtx11 = (Dgc(constants.R,point[0],point[1],s1.get('tx_lat'),s1.get('tx_lon'))/Dgctotal11)*Dhtotal(Dgctotal11, N11, constants.constants.Hiono, constants.R)
                    else:
                        Rtx11 = ((2 * math.pi * constants.R - Dgc(constants.R,point[0],point[1],s1.get('tx_lat'),s1.get('tx_lon')))/Dgctotal11)*Dhtotal(Dgctotal11, N11, constants.constants.Hiono, constants.R)
                    SNR11 = SNR(s1.get('power'),s1.get('frequency'),rcs1,Rrx11,Rtx11,N11)
                    #print('11',SNR11)
                    if SNR11 > mSNR:
                        
                        #point 1 with spot 2
                        if shortest_hdist(s2.get('rx_lon'), s2.get('tx_lon'), [-180, 180]) > abs(point[1]-s2.get('rx_lon')) and shortest_hdist(s2.get('rx_lon'), s2.get('tx_lon'), [-180, 180]) > abs(point[1]-s2.get('tx_lon')):
                            Dgctotal12 = Dgc(constants.R,s2.get('rx_lat'),s2.get('rx_lon'),s2.get('tx_lat'),s2.get('tx_lon'))
                        else:
                            Dgctotal12 = 2 * math.pi * constants.R - Dgc(constants.R,s2.get('rx_lat'),s2.get('rx_lon'),s2.get('tx_lat'),s2.get('tx_lon'))
                        N12 = math.ceil(Dgctotal12/(2*constants.R*math.acos(constants.R/(constants.R+300000))))
                        #ensuring distance from rx to target is the correct 1
                        if shortest_hdist(point[1], s2.get('tx_lon'), [-180, 180]) > abs(s2.get('rx_lon')-s2.get('tx_lon')) and shortest_hdist(point[1], s2.get('tx_lon'), [-180, 180]) > abs(s2.get('rx_lon')-point[1]):
                            Rrx12 = (Dgc(constants.R,point[0],point[1],s2.get('rx_lat'),s2.get('rx_lon'))/Dgctotal12)*Dhtotal(Dgctotal12, N12, constants.constants.Hiono, constants.R)
                        else:
                            Rrx12 = ((2 * math.pi * constants.R - Dgc(constants.R,point[0],point[1],s2.get('rx_lat'),s2.get('rx_lon')))/Dgctotal12)*Dhtotal(Dgctotal12, N12, constants.constants.Hiono, constants.R)
                        if shortest_hdist(point[1], s2.get('rx_lon'), [-180, 180]) > abs(s2.get('tx_lon')-s2.get('rx_lon')) and shortest_hdist(point[1], s2.get('rx_lon'), [-180, 180]) > abs(s2.get('tx_lon')-point[1]):
                            Rtx12 = (Dgc(constants.R,point[0],point[1],s2.get('tx_lat'),s2.get('tx_lon'))/Dgctotal12)*Dhtotal(Dgctotal12, N12, constants.constants.Hiono, constants.R)
                        else:
                            Rtx12 = ((2 * math.pi * constants.R - Dgc(constants.R,point[0],point[1],s2.get('tx_lat'),s2.get('tx_lon')))/Dgctotal12)*Dhtotal(Dgctotal12, N12, constants.constants.Hiono, constants.R)
                        SNR12 = SNR(s2.get('power'),s2.get('frequency'),rcs2,Rrx12,Rtx12,N12)
                        #print('12',SNR12)
                        if SNR12 > mSNR:
                            p.append([point[0],point[1],s1,s2])
                            
                    #point 2 with spot 1
                    #checking if it point on long path or short path
                    if shortest_hdist(s1.get('rx_lon'), s1.get('tx_lon'), [-180, 180]) > abs(point[3]-s1.get('rx_lon')) and shortest_hdist(s1.get('rx_lon'), s1.get('tx_lon'), [-180, 180]) > abs(point[3]-s1.get('tx_lon')):
                        Dgctotal21 = Dgc(constants.R,s1.get('rx_lat'),s1.get('rx_lon'),s1.get('tx_lat'),s1.get('tx_lon'))
                    else:
                        Dgctotal21 = 2 * math.pi *constants.R- Dgc(constants.R,s1.get('rx_lat'),s1.get('rx_lon'),s1.get('tx_lat'),s1.get('tx_lon'))
                    N21 = math.ceil(Dgctotal21/(2*constants.R*math.acos(constants.R/(constants.R+300000))))
                    #ensuring distance from rx to target is the correct 1
                    if shortest_hdist(point[3], s1.get('tx_lon'), [-180, 180]) > abs(s1.get('rx_lon')-s1.get('tx_lon')) and shortest_hdist(point[3], s1.get('tx_lon'), [-180, 180]) > abs(s1.get('rx_lon')-point[3]):
                        Rrx21 = (Dgc(constants.R,point[2],point[3],s1.get('rx_lat'),s1.get('rx_lon'))/Dgctotal21)*Dhtotal(Dgctotal21, N21, constants.Hiono, constants.R)
                    else:
                        Rrx21 = ((2 * math.pi *constants.R- Dgc(constants.R,point[2],point[3],s1.get('rx_lat'),s1.get('rx_lon')))/Dgctotal21)*Dhtotal(Dgctotal21, N21, constants.Hiono, constants.R)
                    if shortest_hdist(point[3], s1.get('rx_lon'), [-180, 180]) > abs(s1.get('tx_lon')-s1.get('rx_lon')) and shortest_hdist(point[3], s1.get('rx_lon'), [-180, 180]) > abs(s1.get('tx_lon')-point[3]):
                        Rtx21 = (Dgc(constants.R,point[2],point[3],s1.get('tx_lat'),s1.get('tx_lon'))/Dgctotal21)*Dhtotal(Dgctotal21, N21, constants.Hiono, constants.R)
                    else:
                        Rtx21 = ((2 * math.pi *constants.R- Dgc(constants.R,point[2],point[3],s1.get('tx_lat'),s1.get('tx_lon')))/Dgctotal21)*Dhtotal(Dgctotal21, N21, constants.Hiono, constants.R)
                    SNR21 = SNR(s1.get('power'),s1.get('frequency'),rcs1,Rrx21,Rtx21,N21)
                    #print('21',SNR21)
                    if SNR21 > mSNR:
                        #point 1 with spot 2
                        if shortest_hdist(s2.get('rx_lon'), s2.get('tx_lon'), [-180, 180]) > abs(point[3]-s2.get('rx_lon')) and shortest_hdist(s2.get('rx_lon'), s2.get('tx_lon'), [-180, 180]) > abs(point[3]-s2.get('tx_lon')):
                            Dgctotal22 = Dgc(constants.R,s2.get('rx_lat'),s2.get('rx_lon'),s2.get('tx_lat'),s2.get('tx_lon'))
                        else:
                            Dgctotal22 = 2 * math.pi *constants.R- Dgc(constants.R,s2.get('rx_lat'),s2.get('rx_lon'),s2.get('tx_lat'),s2.get('tx_lon'))
                        N22 = math.ceil(Dgctotal22/(2*constants.R*math.acos(constants.R/(constants.R+300000))))
                        #ensuring distance from rx to target is the correct 1
                        if shortest_hdist(point[3], s2.get('tx_lon'), [-180, 180]) > abs(s2.get('rx_lon')-s2.get('tx_lon')) and shortest_hdist(point[3], s2.get('tx_lon'), [-180, 180]) > abs(s2.get('rx_lon')-point[3]):
                            Rrx22 = (Dgc(constants.R,point[2],point[3],s2.get('rx_lat'),s2.get('rx_lon'))/Dgctotal22)*Dhtotal(Dgctotal22, N22, constants.Hiono, constants.R)
                        else:
                            Rrx22 = ((2 * math.pi *constants.R- Dgc(constants.R,point[2],point[3],s2.get('rx_lat'),s2.get('rx_lon')))/Dgctotal22)*Dhtotal(Dgctotal22, N22, constants.Hiono, constants.R)
                        if shortest_hdist(point[3], s2.get('rx_lon'), [-180, 180]) > abs(s2.get('tx_lon')-s2.get('rx_lon')) and shortest_hdist(point[3], s2.get('rx_lon'), [-180, 180]) > abs(s2.get('tx_lon')-point[3]):
                            Rtx22 = (Dgc(constants.R,point[2],point[3],s2.get('tx_lat'),s2.get('tx_lon'))/Dgctotal22)*Dhtotal(Dgctotal22, N22, constants.Hiono, constants.R)
                        else:
                            Rtx22 = ((2 * math.pi *constants.R- Dgc(constants.R,point[2],point[3],s2.get('tx_lat'),s2.get('tx_lon')))/Dgctotal22)*Dhtotal(Dgctotal22, N22, constants.Hiono, constants.R)
                        SNR22 = SNR(s2.get('power'),s2.get('frequency'),rcs2,Rrx22,Rtx22,N22)
                        #print('22',SNR22)
                        if SNR22 > mSNR:
                            p.append([point[2],point[3],s1,s2])
                        '''
                        mem.get(j).get(k).update([SNR11,SNR12,SNR21,SNR22])
                else:
                    if mem.get(j).get(k)[0] > 30 and mem.get(j).get(k)[1] > 30:
                        p.append([point[0],point[1],j,k])
                    if mem.get(j)(k)[2] > 30 and mem.get(j)(k)[3] > 30:
                        p.append([point[2],point[3],j,k])
                        '''

    print("intersect_point_lp,",time.process_time()-st)        
    
    query.print_json('all','plp',s,e,p,MR,ssT)
    
    return p

def crosscheck(d,p, lat1, lon1, lat2, lon2, s, e):#data, planes, minimum radius, area of focus
    st = time.process_time()   
    query.clear_json('all','d',s,e)
    mError = 0
    mMin = constants.int_MAX
    mMax = 0
    numOfData = 0
    dist = []
    #print(p)
    #print(len(d),len(p))
    for i in d:
        nearby = [constants.int_MAX,[]]
        #print(i[0],i[1])
        if i[0] > lat1 and i[0] < lat2 and i[1] > lon1 and i[1] < lon2:
            for j in p:    
                #check if time and location is correct
                if i[2].get('time') == j[0][0:4]+'-'+j[0][5:7]+'-'+j[0][8:10]+' '+j[1][0:2]+':'+j[1][3:5]+':00':
                    
                    if Dgc(constants.R,i[0],i[1],float(j[9]),float(j[10])) <= nearby[0]:
                        nearby=[Dgc(constants.R,i[0],i[1],float(j[9]),float(j[10])),j]
                        #print(nearby)
            if len(nearby[1]) != 0:
                mError += nearby[0]
                if mMin > nearby[0]:
                    mMin = nearby[0]
                if mMax < nearby[0]:
                    mMax = nearby[0]
                numOfData += 1
                query.append_json('all','d',s, e, nearby)
                print(mError/numOfData, mMin, mMax, numOfData)
    query.append_json('all','d',s, e, ']')    
    mError /= numOfData
    print(mError,numOfData,i[0],i[1],j[9],j[10],)
    print("crosscheck,",st)
    return [mError,mMin,mMax,numOfData]

if __name__ == "__main__":  
    d = [{'rx_lat': 1, 'tx_lat': 9},{'rx_lat': -7, 'tx_lat': 3},{'rx_lat': 3, 'tx_lat': 0}]
    
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    #intersect_greatcircle([10,-70],[10,70],[10,-70],[10,-70])
    
    #A = [{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
    #A = process.anomalies('r', MR, ssT, s, e)
    
    #print(intersect_point_lp([{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-09-01 02:00:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': -80, 'rx_lon': -80, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 80, 'tx_lon': 80, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'SS_freq': 1, 'SS_snr': 1, 'SS_drift': 1, 'id': '8100420947', 'time': '2024-09-01 02:00:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': -80, 'rx_lon': -75, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 80, 'tx_lon': 80, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]))
    #intersect_point_sp(A)
    d = [[0,0,{'time': '2024-01-01 00:00:00'}]]
    p = [["2024/01/01","00:00:44.408827","2","1","?","?","?","?","?","0","0","?","?","?","?","?","?","?","?","?","?","?","?","?"],["2024/01/01","00:00:44.408827","?","?","?","?","?","?","?","1","1","?","?","?","?","?","?","?","?","?","?","?","?","?"]]
    print(crosscheck(d, p, -90, -180, 90, 180))