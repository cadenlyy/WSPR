import query
#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, frequency, power, snr, drift, version, code
transmitions = {}

#colums, database, start dateTime, end dateTime, limit = 100
q = query.wsprlive_get("*", "rx", '2024-07-24 09:24:00', '2024-07-24 09:25:00',10000)

for i in q: #proccess each spot
    data = list(i.values())
    if transmitions.get(data[3]) == None:
        transmitions.update({data[3]: []})
    transmitions.get(data[3]).append(data[7])

print(transmitions)

