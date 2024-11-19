import check

p=[]

j = {'SS_freq': -348619.2288304247, 'SS_snr': 29.677178697402976, 'SS_drift': 0, 'id': '8256616381', 'time': '2024-09-01 03:52:00', 'band': 18, 'rx_sign': 'VK5TC', 'rx_lat': -35.062, 'rx_lon': 138.542, 'rx_loc': 'PF94gw', 'tx_sign': 'VK4BA', 'tx_lat': -27.521, 'tx_lon': 152.958, 'tx_loc': 'QG62', 'distance': 1604, 'azimuth': 235, 'rx_azimuth': 62, 'frequency': 18106186, 'power': 23, 'snr': -23, 'drift': 0, 'version': '2.6.1', 'code': 1}
k = {'SS_freq': -5993775.392985822, 'SS_snr': 46.565621163477765, 'SS_drift': 19527068.560821768, 'id': '8256619589', 'time': '2024-09-01 03:52:00', 'band': 21, 'rx_sign': 'KFS/SW', 'rx_lat': 37.396, 'rx_lon': -122.375, 'rx_loc': 'CM87tj', 'tx_sign': 'ZL3TKI', 'tx_lat': -43.562, 'tx_lon': 172.625, 'tx_loc': 'RE66hk', 'distance': 11130, 'azimuth': 47, 'rx_azimuth': 221, 'frequency': 21096101, 'power': 23, 'snr': -3, 'drift': 0, 'version': 'WD_3.2.2', 'code': 1}

#point = [-36.00519045246581, 54.121659809004115, 36.00519045246581, -125.8783401909959]
point = check.intersect_greatcircle([j.get('rx_lat'),j.get('rx_lon')], [j.get('tx_lat'),j.get('tx_lon')], [k.get('rx_lat'),k.get('rx_lon')], [k.get('tx_lat'),k.get('tx_lon')])
if check.shortest_hdist(j.get('rx_lon'), k.get('rx_lon'), [-180, 180]) > abs(point[1]-j.get('rx_lon')) and check.shortest_hdist(j.get('rx_lon'), k.get('rx_lon'), [-180, 180]) > abs(point[1]-j.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[1]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[1]-k.get('tx_lon')):
    #adding new openspot
    p.append([point[0],point[1],j,k])
    
elif check.shortest_hdist(j.get('rx_lon'), k.get('rx_lon'), [-180, 180]) > abs(point[3]-j.get('rx_lon')) and check.shortest_hdist(j.get('rx_lon'), k.get('rx_lon'), [-180, 180]) > abs(point[3]-j.get('tx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[3]-k.get('rx_lon')) and abs(k.get('rx_lon')-k.get('tx_lon')) > abs(point[3]-k.get('tx_lon')):
    #adding new openspot
    p.append([point[2],point[3],j,k])
    
print(p)