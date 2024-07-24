import query
#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, frequency, power, snr, drift, version, code
data = []

#colums, database, start dateTime, end dateTime, limit = 100
q = query.wsprlive_get("COLUMNS('rx_sign')", "rx", '2024-07-24 09:24:00', '2024-07-24 09:25:00')

for i in q:
    data.append(list(i.values()))

print(data)
