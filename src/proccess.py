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
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).update({data[1]:[[],[0,0,0],[None,None,None]]})
    #pushing in transmittion info                                   (SD: freq, snr, drift)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[0].append([0,0,0]+data)
    
    #calculating sum for freq, SNR and drift
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][0]+=data[14]
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][1]+=data[16]
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][2]+=data[17]

#sliding(only actually going through each spot once so still O(N))   
for r in transmitions.items():
    for t in r[1].items():
        numOfSpots = 0
        left = 0
        right = 0
        slidingWindow = [0,0,0]
        for i in range(0, len(t[1])):
            if datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') - ts < MR:
                slidingWindow[0] += t[1].get(list(t[1])[i])[1][0]
                slidingWindow[1] += t[1].get(list(t[1])[i])[1][1]
                slidingWindow[2] += t[1].get(list(t[1])[i])[1][2]
                numOfSpots += len(t[1].get(list(t[1])[i])[0])
                #print(len(t[1].get(list(t[1])[i])[0]))
                right = i
            else:
                for j in  range(left, i):
                    if datetime.datetime.strptime(list(t[1])[j], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') > MR:
                        slidingWindow[0] -= t[1].get(list(t[1])[j])[1][0]
                        slidingWindow[1] -= t[1].get(list(t[1])[j])[1][1]
                        slidingWindow[2] -= t[1].get(list(t[1])[j])[1][2]
                        numOfSpots -= len(t[1].get(list(t[1])[j])[0])
                        #print(len(t[1].get(list(t[1])[j])[0]))
                    else:
                        left = j
                        break
                for j in  range(right, len(t[1])):
                    if datetime.datetime.strptime(list(t[1])[j], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') < MR:
                        slidingWindow[0] += t[1].get(list(t[1])[j])[1][0]
                        slidingWindow[1] += t[1].get(list(t[1])[j])[1][1]
                        slidingWindow[2] += t[1].get(list(t[1])[j])[1][2]
                        numOfSpots += len(t[1].get(list(t[1])[j])[0])
                        #print(len(t[1].get(list(t[1])[j])[0]))
                    else:
                        right = j
                        break
            transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[2][0] = slidingWindow[0]/numOfSpots
            transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[2][1] = slidingWindow[1]/numOfSpots
            transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[2][2] = slidingWindow[2]/numOfSpots
            print(slidingWindow[0],numOfSpots)
                    
print(transmitions)    
                    
