import check
import math
import sys

#constants
c = 299792458#m/s
k = 1.38*10**-23#j/k
t0 = 290#k
B = 6#hz bandwidth
R = 6378000#m radius of earth
Hiono = 300000#m
pheight = 20
plength = 70
pheading = 0

def lg(v):
    return math.log(v,10)
    
def RCS(h,l,ra,f):
    return 4 * math.pi * h**2 * l**2 * math.sin(ra)**2 * f**2 / c**2

def Dgc(r,lat1,lon1,lat2,lon2):
    if r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180)) != 0:
        return r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180))
    return 1e-317
    
def Dhtotal(Dgctotal,n,h):
    return math.sqrt(Dgctotal**2 + (2*n)**2 * h**2)

def SNR(p,f,rcs,rrx,rtx,n):#power transmitted(dB), frequency transmitted, RCS of target, distance from tx to target, distance from rx to target, number of hops
   noise = 10 * lg(k * t0 * B)
   signal = p - 30 + 20 * lg(c) - 20 * lg(f) + 10 * lg(rcs) - 30 * lg(4*math.pi) - 20 * lg(rrx) - 20 * lg(rtx)
   losses = 5 * n + 20 * lg (4 * math.pi) - 20 * lg(c) + 20 * lg(rrx + rtx) + 20 * lg(f)
   print(signal, noise, losses)
   return signal - noise 

        
def Hr(a,latp,lonp,lats,lons):#heading of plane relative to north
    #relative heading
    A = lats
    B = latp
    C = math.sin(latp) * math.sin(lats) + math.cos(latp) * math.cos(lats) * math.cos(lons - lonp)
    s = math.acos((math.cos(A) - math.cos(B) * C) / (math.sin(B) * math.sin(math.acos(C))))
    return a - s

j = {'SS_snr': 0.9429847612307231, 'id': '8256539027', 'time': '2024-09-01 03:20:00', 'band': 14, 'rx_sign': 'EA8BFK', 'rx_lat': 28.604, 'rx_lon': -13.875, 'rx_loc': 'IL38bo', 'tx_sign': 'HB9PVI', 'tx_lat': 47.479, 'tx_lon': 6.958, 'tx_loc': 'JN37', 'distance': 2763, 'azimuth': 228, 'rx_azimuth': 34, 'frequency': 14097072, 'power': 23, 'snr': -10, 'drift': 0, 'version': 'WD_3.1.7', 'code': 1}

point = [47.47900000000001, 6.95800000000004,1,1]

#rcs = RCS(pheight,plength,math.pi/2,j.get('frequency'))
Dgctotal1 = Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon'))
N1 = math.ceil(Dgctotal1/(2*R*math.acos(R/(R+300000))))
#Rrx1 = (Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
Rtx1 = (Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
#SNR11 = SNR(j.get('power'),j.get('frequency'),rcs,Rrx1,Rtx1,N1)

r = R
lat1 = 47.4790001
lon1 = 2
lat2 = 47.479
lon2 = 2

print(Rtx1)


