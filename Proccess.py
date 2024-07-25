import query

def mean(cm, v, l):
    return (cm*l+v)/(l+1)

#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
transmitions = {}

#colums, database, start dateTime, end dateTime, limit = 100
q = query.wsprlive_get("*", "rx", '2024-07-24 09:24:00', '2024-07-24 09:25:00', 10000)

for i in q: #proccess each spot
    data = list(i.values())
    if transmitions.get(tuple(data[3:7])) == None:
        transmitions.update({tuple(data[3:7]): {}})
    if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])) == None:
        transmitions.get(tuple(data[3:7])).update({tuple(data[7:11]):[[0,0,0]]})
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).append(data[0:3]+data[11:])
    
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0] = mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[14],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-2)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][1] = mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[16],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-2)
    transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][2] = mean(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11]))[0][0],data[17],len(transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])))-2)

print(transmitions)