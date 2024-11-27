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
    return r * math.aimport check
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

j = {"rx_lat": 47.438, "rx_lon": 9.875, "tx_lat": 53.771, "tx_lon": -3.042, "distance": 1149, "azimuth": 123, "rx_azimuth": 312, "frequency": 5366211, "power": 23, "snr": -28, "drift": 0}

point = [53.33839291328147, -1.9205941457474967,1,1]

rcs = RCS(pheight,plength,math.pi/2,j.get('frequency'))
Dgctotal1 = Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon'))
N1 = math.ceil(Dgctotal1/(2*R*math.acos(R/(R+300000))))
Rrx1 = (Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
Rtx1 = (Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
SNR11 = SNR(j.get('power'),j.get('frequency'),rcs,Rrx1,Rtx1,N1)

print(Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon')))
print(Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon')))
print(Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon')))cos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1- lon2))

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

j = {"rx_lat": 47.438, "rx_lon": 9.875, "tx_lat": 53.771, "tx_lon": -3.042, "distance": 1149, "azimuth": 123, "rx_azimuth": 312, "frequency": 5366211, "power": 23, "snr": -28, "drift": 0}

point = [53.33839291328147, -1.9205941457474967,1,1]

rcs = RCS(pheight,plength,math.pi/2,j.get('frequency'))
Dgctotal1 = Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon'))
N1 = math.ceil(Dgctotal1/(2*R*math.acos(R/(R+300000))))
Rrx1 = (Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
Rtx1 = (Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon'))/Dgctotal1)*Dhtotal(Dgctotal1, N1, Hiono)
SNR11 = SNR(j.get('power'),j.get('frequency'),rcs,Rrx1,Rtx1,N1)

print(Dgc(R,j.get('rx_lat'),j.get('rx_lon'),j.get('tx_lat'),j.get('tx_lon')))
print(Dgc(R,point[0],point[1],j.get('rx_lat'),j.get('rx_lon')))
print(Dgc(R,point[0],point[1],j.get('tx_lat'),j.get('tx_lon')))