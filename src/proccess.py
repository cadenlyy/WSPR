import copy
import query
import datetime
import math

#wspr query
#colums, database, start dateTime, end dateTime, limit = None
ts = datetime.datetime(2024,7,24,9,26,0)
te = datetime.datetime(2024,7,24,12,33,0)
q = query.wsprlive_get("*", "rx", str(ts), str(te), None)
#q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 10, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
print("wspr.rx query successful") #check if proccessing is slow

#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code

#adjList with weight
transmitions = {} #dict mapping receiver to dict of transmitters with dictionary mapping time to 2 arrays, one of spot details, one for sum, mean and SD (i.e a{{{[[[]],[]}}})

def roundEvenDateTime(a): #YYYY-MM-DD HH:MM:SS
    return datetime.datetime.strptime(str(a)[:15]+str(int(str(a)[15])%2+int(str(a)[15]))+str(a)[16:], '%Y-%m-%d %H:%M:%S')

def SD(s, m, n):#sum of x^2, mean, number of values
    try:
        return math.sqrt(float(s/n-m**2))
    except ValueError:
        return 0

def ss(v, m, sd):
    if sd != 0:
        return (v-m)/sd
    else:
        return 0

MR = datetime.timedelta(minutes = 2)

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
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).update({data[1]:[[],[0,0,0,0,0,0,None,None,None,None,None,None,None,[]]]}) #[sum:freq,snr,drift,sum:freq^2,snr^2,drift^2,mean:freq,snr,drift,SD:freq,snr,drift,numOfSpots,sliding window]
    #pushing in transmittion info                                  (Standard score: freq, snr, drift)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[0].append([0,0,0]+data)
    
    #calculating sum for freq, SNR and drift
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][0]+=data[14]
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][1]+=data[16]
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][2]+=data[17]
    
    #calculating sum for freq^2, SNR^2 and drift^2
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][3]+=data[14]**2
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][4]+=data[16]**2
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[1])[1][5]+=data[17]**2

#sliding(only actually going through each spot once so still O(N))   
for r in transmitions.items():
    for t in r[1].items():
        numOfSpots = 0
        left = 0
        right = 0
        slidingWindow = [0,0,0,0,0,0]#sum:freq,snr,drift,sum:freq^2,snr^2,drift^2
        for i in range(0, len(t[1])):
            if datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') - ts < MR:
                slidingWindow[0] += t[1].get(list(t[1])[i])[1][0]
                slidingWindow[1] += t[1].get(list(t[1])[i])[1][1]
                slidingWindow[2] += t[1].get(list(t[1])[i])[1][2]
                slidingWindow[3] += t[1].get(list(t[1])[i])[1][3]
                slidingWindow[4] += t[1].get(list(t[1])[i])[1][4]
                slidingWindow[5] += t[1].get(list(t[1])[i])[1][5]
                numOfSpots += len(t[1].get(list(t[1])[i])[0])
                right = i+1
            elif te - datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') < MR:
                break
            else:
                for j in  range(left, i+1):
                    if datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[j], '%Y-%m-%d %H:%M:%S') > MR:
                        slidingWindow[0] -= t[1].get(list(t[1])[j])[1][0]
                        slidingWindow[1] -= t[1].get(list(t[1])[j])[1][1]
                        slidingWindow[2] -= t[1].get(list(t[1])[j])[1][2]
                        slidingWindow[3] -= t[1].get(list(t[1])[j])[1][3]
                        slidingWindow[4] -= t[1].get(list(t[1])[j])[1][4]
                        slidingWindow[5] -= t[1].get(list(t[1])[j])[1][5]
                        numOfSpots -= len(t[1].get(list(t[1])[j])[0])
                    else:
                        left = j
                        break
                for j in  range(right, len(t[1])):
                    if datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[j], '%Y-%m-%d %H:%M:%S') < MR:
                        slidingWindow[0] += t[1].get(list(t[1])[j])[1][0]
                        slidingWindow[1] += t[1].get(list(t[1])[j])[1][1]
                        slidingWindow[2] += t[1].get(list(t[1])[j])[1][2]
                        slidingWindow[3] += t[1].get(list(t[1])[j])[1][3]
                        slidingWindow[4] += t[1].get(list(t[1])[j])[1][4]
                        slidingWindow[5] += t[1].get(list(t[1])[j])[1][5]
                        numOfSpots += len(t[1].get(list(t[1])[j])[0])
                    else:
                        right = j
                        break
                #mean

                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][6] = slidingWindow[0]/numOfSpots
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][7] = slidingWindow[1]/numOfSpots
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][8] = slidingWindow[2]/numOfSpots
                #SD
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][9] = SD(slidingWindow[3],slidingWindow[0]/numOfSpots,numOfSpots)
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][10] = SD(slidingWindow[4],slidingWindow[1]/numOfSpots,numOfSpots)
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][11] = SD(slidingWindow[5],slidingWindow[2]/numOfSpots,numOfSpots)

                #numofspots
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][12] = numOfSpots
                #sliding window
                transmitions.get(r[0]).get(t[0]).get(list(t[1])[i])[1][13] = copy.deepcopy(slidingWindow)


            
#calculating standard score and detecting abnormallies
abnormallies = []
ssT = 100000
for r in transmitions.items():
    for t in r[1].items():
        for i in t[1].items():
            for j in i[1][0]:
                if i[1][1][6] != None and i[1][1][7] != None and i[1][1][8] != None and i[1][1][9] != None and i[1][1][10] != None and i[1][1][11] != None:
                    if abs(ss(j[14],i[1][1][6],i[1][1][9]))  >= ssT or abs(ss(j[16],i[1][1][7],i[1][1][10]))  >= ssT or abs(ss(j[17],i[1][1][8],i[1][1][11]))  >= ssT:
                        abnormallies.append(j)
                        print()
                        
print(abnormallies)

print(len(q),len(abnormallies))
                    

            
                    
