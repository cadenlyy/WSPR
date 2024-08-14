import query
import datetime

#wspr query
#colums, database, start dateTime, end dateTime, limit = None
ts = datetime.datetime(2024,7,24,9,26,0)
te = datetime.datetime(2024,7,24,9,30,0)
#q = query.wsprlive_get("*", "rx", str(ts), str(te), None)
q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
print("wspr.rx query successful") #check if proccessing is slow


#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code

#adjList with weight
transmitions = {} #dict mapping receiver to dict of transmitters with dictionary mapping time to 3 arrays, one of spot details, one for sum and one for mean (i.e a{{{[[[]],[],[]}}})

def mean(v, l):
    return sum(v)/l

def addMean(cm, v, cl, vl=-1):
    if (vl == -1):
        vl = len(v)
    return mean([cm*cl,sum(v)],cl+vl)    

def subMean(cm, v, cl, vl=-1):
    if (vl == -1):
        vl = len(v)
    return mean([cm*cl,-sum(v)],cl-vl) 

def slideMean(cm, sv, av, cl, svl=-1, avl=-1):
    if (svl == -1):
        svl = len(sv)
    if (avl == -1):
        avl = len(av)
    return addMean(subMean(cm,sv,cl,svl),av,cl-svl,avl)

def roundEvenDateTime(a): #YYYY-MM-DD HH:MM:SS
    return datetime.datetime.strptime(str(a)[:15]+str(int(str(a)[15])%2+int(str(a)[15]))+str(a)[16:], '%Y-%m-%d %H:%M:%S')

MR = datetime.timedelta(minutes=2)

for i in q: #proccess each spot
    data = list(i.values())
    #adding new receving stations
    if transmitions.get(tuple(data[3:7])) == None: 
        transmitions.update({tuple(data[3:7]): {}})
    #adding new transmitting stations to receivers
    if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])) == None:
        transmitions.get(tuple(data[3:7])).update({tuple(data[7:11]):{}})
    #adding new time
    if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1]) == None:
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).update({data[1]:[[],[0,0,0],[0,0,0]]})
    #pushing in transmittion info                                   (SD: freq, snr, drift)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[0].append([0,0,0]+data)
    
    #calculating sum for freq, SNR and drift
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][0]+=data[14]
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][1]+=data[16]
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][2]+=data[17]

#sliding(only actually going through each spot once so still O(N))   
for r in transmitions.items():
    for t in r[1].items():
        for d in t[1].items():
            slidingWindow = [0,0,0]
            if datetime.datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S') < ts+MR:
                for i in d[1][0]:
                    slidingWindow[0]+=i[17]
                transmitions.get(r[0]).get(t[0]).get(d[0])[2][0] = None
                transmitions.get(r[0]).get(t[0]).get(d[0])[2][1] = None
                transmitions.get(r[0]).get(t[0]).get(d[0])[2][2] = None

print(transmitions)
