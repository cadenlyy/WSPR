import check
import math

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
    return r * math.acos(math.sin(lat1*math.pi/180) * math.sin(lat2*math.pi/180) + math.cos(lat1*math.pi/180) * math.cos(lat2*math.pi/180) * math.cos(lon2*math.pi/180- lon1*math.pi/180))

def Dhtotal(Dgctotal,n,h):
    return math.sqrt(Dgctotal**2 + (2*n)**2 * h**2)

def SNR(p,f,rcs,rrx,rtx,n):#power transmitted(dB), frequency transmitted, RCS of target, distance from tx to target, distance from rx to target, number of hops
    print(- 10 * lg(k * t0 * B) -  5 * n - 20 * lg (4 * math.pi) + 20 * lg(c) - 20 * lg(rrx + rtx) - 20 * lg(f))
    print(p - 30 + 20 * lg(c) - 20 * lg(f) + 10 * lg(rcs) - 30 * lg(4*math.pi) - 20 * lg(rrx) - 20 * lg(rtx))
    print(- 10 * lg(k * t0 * B))
    return p - 30 + 40 * lg(c) - 40 * lg(f) + 10 * lg (rcs) - 50 * lg(4*math.pi) - 20 * lg(rtx)  - 20 * lg(rrx) - 10 * lg(k * t0 * B) - 20 * lg(rrx+rtx) - 5 * n

        
def Hr(a,latp,lonp,lats,lons):#heading of plane relative to north
    #relative heading
    A = lats
    B = latp
    C = math.sin(latp) * math.sin(lats) + math.cos(latp) * math.cos(lats) * math.cos(lons - lonp)
    s = math.acos((math.cos(A) - math.cos(B) * C) / (math.sin(B) * math.sin(math.acos(C))))
    return a - s

j = {"SS_snr": 0.6411933438039, "id": "8256532366", "time": "2024-09-01 03:18:00", "band": 2400, "rx_sign": "OE6PWD/SDR", "rx_lat": 47.479, "rx_lon": 14.958, "rx_loc": "JN77", "tx_sign": "F6BIR", "tx_lat": 49.229, "tx_lon": 2.208, "tx_loc": "JN19cf", "distance": 961, "azimuth": 97, "rx_azimuth": 286, "frequency": 2400069555, "power": 17, "snr": -18, "drift": 0, "version": "2.7.0-rc3", "code": 1}

point = [48.29086228437446, 10.340257663433432,1,1]

rcs = RCS(pheight,plength,math.pi/2,j.get('frequency'))
Dgctotal1 = Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon'))
N1 = math.ceil(Dgctotal1/(2*R*math.acos(R/(R+300000))))
Rrx1 = (Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
Rtx1 = (Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
SNR11 = SNR(j.get('power'),j.get('frequency'),rcs,Rrx1,Rtx1,N1)

print(SNR11)