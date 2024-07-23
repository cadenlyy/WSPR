import query
#id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, frequency, power, snr, drift, version, code
data = []

q = query.wsprlive_get("SELECT COLUMNS('a') FROM wspr.rx LIMIT 1")

for i in q:
    data.append(list(i.values()))

print(data)

