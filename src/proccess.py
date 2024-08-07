import query
import datetime

#wspr query
#colums, database, start dateTime, end dateTime, limit = None
ts = datetime.datetime(2024,7,24,9,26,0)
te = datetime.datetime(2024,7,24,9,30,0)
#q = query.wsprlive_get("*", "rx", str(ts), str(te), None)
q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
print("wspr.rx query successful") #check if proccessing is slow


#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code

#adjList with weight
transmitions = {} #dict mapping receiver to dict of transmitters with array of mean(freq snr and drift in a set range) with transmitions containing arrays of transmittion details (i.e a{{[[[0,0,0],]]}})

def mean(cm, v, l):
    return (cm*l+v)/(l+1)

MR = datetime.time(0,0,1)

for i in q: #proccess each spot
    data = list(i.values())
    #adding new receving stations
    if transmitions.get(tuple(data[3:7])) == None: 
        transmitions.update({tuple(data[3:7]): {}})
    #adding new transmitting stations to receivers
    if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])) == None:
        transmitions.get(tuple(data[3:7])).update({tuple(data[7:11]):[]})
    #pushing in transmittion info                                   (mean: freq, snr, drift SD: freq, snr, drift)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).append([0,0,0,0,0,0]+data[0:3]+data[11:])
    #calculating mean and SD
    if((datetime.datetime.min + abs(datetime.datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S')-ts)).time() < MR):
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0]=mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[14],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-1)
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][1]=mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][1],data[16],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-1)
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][2]=mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][2],data[17],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-1)
   # else:
        #transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0]=2
print(transmitions)