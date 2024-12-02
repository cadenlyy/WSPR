import datetime
import math
import numpy as np
import time

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
SPN = 4.9406564584124654e-324


crx = [-149.958, 61.146] #lon, lat
ctx = [-155.04, 19.4792]
ca = [-148.61223, 60.38938]#lon,lat

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
    if r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180)) != 0:
        return r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180))
    return 1e-316#smallest float u can return in sypder

def Dhtotal(Dgctotal,n,h):
    return math.sqrt(Dgctotal**2 + (2*n)**2 * h**2)

def SNR(p,f,rcs,rrx,rtx,n):#power transmitted(dB), frequency transmitted, RCS of target, distance from tx to target, distance from rx to target, number of hops
    noise = 10 * lg(k * t0 * B)
    signal = p - 30 + 20 * lg(c) - 20 * lg(f) + 10 * lg(rcs) - 30 * lg(4*math.pi) - 20 * lg(rrx) - 20 * lg(rtx)
    #print(signal, noise, losses)
    return signal - noise 

        
def Hr(a,latp,lonp,lats,lons):#heading of plane relative to north
    #relative heading
    A = lats
    B = latp
    C = math.sin(latp) * math.sin(lats) + math.cos(latp) * math.cos(lats) * math.cos(lons - lonp)
    s = math.acos((math.cos(A) - math.cos(B) * C) / (math.sin(B) * math.sin(math.acos(C))))
    return a - s

s1 = {"SS_freq": 2.8300436870993213, "SS_snr": -1.2252408110288089, "id": "8256591620", "time": "2024-09-01 03:40:00", "band": 5, "rx_sign": "G4MSA", "rx_lat": 50.854, "rx_lon": -1.958, "rx_loc": "IO90au", "tx_sign": "HB9AK", "tx_lat": 46.896, "tx_lon": 7.292, "tx_loc": "JN36pv", "distance": 806, "azimuth": 306, "rx_azimuth": 119, "frequency": 5366159, "power": 23, "snr": -19, "drift": 0, "version": "1.4A Kiwi", "code": 1}

point = [-49.85089567217109, -179.292, 1,1]
  
rcs1 = RCS(pheight,plength,math.pi/2,s1.get('frequency'))
Dgctotal11 = Dgc(R,s1.get('rx_lat'),s1.get('rx_lon'),s1.get('tx_lat'),s1.get('tx_lon'))
N11 = math.ceil(Dgctotal11/(2*R*math.acos(R/(R+300000))))
Rrx11 = (Dgc(R,point[0],point[1],s1.get('rx_lat'),s1.get('rx_lon'))/Dgctotal11)*Dhtotal(Dgctotal11, N11, Hiono)
Rtx11 = (Dgc(R,point[0],point[1],s1.get('tx_lat'),s1.get('tx_lon'))/Dgctotal11)*Dhtotal(Dgctotal11, N11, Hiono)
SNR11 = SNR(s1.get('power'),s1.get('frequency'),rcs1,Rrx11,Rtx11,N11)
#print('11',SNR11)

print(SNR11)