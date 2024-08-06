import query

#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code

def mean(cm, v, l):
    return (cm*l+v)/(l+1)

#adjList with weight
transmitions = {} #dict mapping receiver to dict of transmitters with array of mean(freq snr and drift) with transmitions containing arrays of transmittion details (i.e a{{[[0,0,0],[]]}})

#colums, database, start dateTime, end dateTime, limit = None
q = query.wsprlive_get("*", "rx", '2024-07-24 09:24:00', '2024-07-24 09:25:00', None)

print("wspr.rx query successful") #check if proccessing is slow

for i in q: #proccess each spot
    data = list(i.values())
    #adding new receving stations
    if transmitions.get(tuple(data[3:7])) == None: 
        transmitions.update({tuple(data[3:7]): {}})
    #adding new transmitting stations to receivers
    if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])) == None:
        transmitions.get(tuple(data[3:7])).update({tuple(data[7:11]):[[0,0,0]]})
    #pushing in transmittion info
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).append(data[0:3]+data[11:])
    #calculating mean of freq snr and drift
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0] = mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[14],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-2)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][1] = mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[16],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-2)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][2] = mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[17],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-2)

print(transmitions)