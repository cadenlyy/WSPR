import copy
import query
import datetime
import math
import csv
import json
import os


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
    return 0
    
def print_csv(t, rx, tx, ts, te, MR, data):
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr/data"
    filename = t+'_'+rx+'_'+tx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+'_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'.csv'
    abs_file = os.path.join(base_dir, filename)
    with open(abs_file, 'w', newline='') as csvfile:
        fieldnames = ['time', 'band', 'frequency', 'snr', 'drift', 'SS:freq', 'SS:snr', 'SS:drift', 'Numofspots']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
def print_json(data, ts, te, rx = None, tx = None, l=None):
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
    if l == None:
        l = ''
    else:
        l = '_'+str(l)
        
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr"
    filename = ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+rx+tx+l+'.txt'
    abs_file = os.path.join(base_dir, filename)
    with open(abs_file, 'w') as file: 
        file.write(json.dumps(data))

def read_json(ts, te, rx = None, tx = None, l=None):
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
    if l == None:
        l = ''
    else:
        l = '_'+str(l)
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr"
    filename = ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+rx+tx+l+'.txt'
    abs_file = os.path.join(base_dir, filename)
    print(abs_file)
    with open(abs_file, 'r') as file: 
        data = file.read()
        return json.loads(data)

def all_spots(MR,ts,te):
    #wspr query
    #colums, database, start dateTime, end dateTime, rx_sign = None, tx_sign = None limit = None
    #q = query.wsprlive_get("*", "rx", str(ts), str(te))
    #q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
    print("wspr.rx query successful") #check if proccessing is slow
    
    #print_json(q, ts, te)
    q = read_json(ts, te)
    
    #print(q)
    
    #id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code

    #adjList with weight
    transmitions = {} #dict mapping receiver to dict of transmitters with dictionary mapping time to 2 arrays, one of spot details, one for sum, mean and SD (i.e a{{{[[[]],[]}}})
    
    for i in q: #proccess each spot
        data = list(i.values())
        #adding new receving stations
        if transmitions.get(tuple(data[3:7])) == None: 
            transmitions.update({tuple(data[3:7]): {}})
        #adding new transmitting stations to receivers
        if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])) == None:
            transmitions.get(tuple(data[3:7])).update({tuple(data[7:11]):{}})
        #adding new time
        if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]) == None:
            transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).update({data[2]:{}})
        if transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1]) == None:
            transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).update({data[1]:[[],[0,0,0,0,0,0,None,None,None,None,None,None,None,[]]]}) #[sum:freq,snr,drift,sum:freq^2,snr^2,drift^2,mean:freq,snr,drift,SD:freq,snr,drift,numOfSpots,sliding window]
        #pushing in transmittion info                                  (Standard score: freq, snr, drift)
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[0].append([0,0,0]+data)
    
        #calculating sum for freq, SNR and drift
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][0]+=data[14]
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][1]+=data[16]
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][2]+=data[17]
    
        #calculating sum for freq^2, SNR^2 and drift^2
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][3]+=data[14]**2
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][4]+=data[16]**2
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][5]+=data[17]**2

    #sliding(only actually going through each spot once so still O(N))   
    for r in transmitions.items():
        for c in r[1].items():
            for t in c[1].items():
                numOfSpots = 0
                left = 0
                right = 0
                ft = list(t[1])[0]
                lt = list(t[1])[-1]
                slidingWindow = [0,0,0,0,0,0]#sum:freq,snr,drift,sum:freq^2,snr^2,drift^2
                for i in range(0, len(t[1])):
                    if datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(ft, '%Y-%m-%d %H:%M:%S') < MR:                 
                        slidingWindow[0] += t[1].get(list(t[1])[i])[1][0]
                        slidingWindow[1] += t[1].get(list(t[1])[i])[1][1]
                        slidingWindow[2] += t[1].get(list(t[1])[i])[1][2]
                        slidingWindow[3] += t[1].get(list(t[1])[i])[1][3]
                        slidingWindow[4] += t[1].get(list(t[1])[i])[1][4]
                        slidingWindow[5] += t[1].get(list(t[1])[i])[1][5]
                        numOfSpots += len(t[1].get(list(t[1])[i])[0])
                        right = i+1
                    elif datetime.datetime.strptime(lt, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') < MR:
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
                            if datetime.datetime.strptime(list(t[1])[j], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') <= MR or j == len(c[1])-1:
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
                        #print(transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i]))
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][6] = slidingWindow[0]/numOfSpots
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][7] = slidingWindow[1]/numOfSpots
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][8] = slidingWindow[2]/numOfSpots
                        #SD
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][9] = SD(slidingWindow[3],slidingWindow[0]/numOfSpots,numOfSpots)
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][10] = SD(slidingWindow[4],slidingWindow[1]/numOfSpots,numOfSpots)
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][11] = SD(slidingWindow[5],slidingWindow[2]/numOfSpots,numOfSpots)

                        #numofspots
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][12] = numOfSpots
                        #sliding window
                        transmitions.get(r[0]).get(c[0]).get(t[0]).get(list(t[1])[i])[1][13] = copy.deepcopy(slidingWindow)


            
    #calculating standard score and detecting abnormallies
    abnormallies = []
    ssT = 1
    for r in transmitions.items():
        for c in r[1].items():
            for t in c[1].items():
                for i in t[1].items():
                    for j in i[1][0]:
                        if i[1][1][6] != None and i[1][1][7] != None and i[1][1][8] != None and i[1][1][9] != None and i[1][1][10] != None and i[1][1][11] != None:
                            if abs(ss(j[14],i[1][1][6],i[1][1][9]))  >= ssT or abs(ss(j[16],i[1][1][7],i[1][1][10]))  >= ssT or abs(ss(j[17],i[1][1][8],i[1][1][11]))  >= ssT:
                                transmitions.get(r[0]).get(c[0]).get(t[0]).get(i[0])[0][0][0] = ss(j[14],i[1][1][6],i[1][1][9])
                                transmitions.get(r[0]).get(c[0]).get(t[0]).get(i[0])[0][0][1] = ss(j[16],i[1][1][7],i[1][1][10])
                                transmitions.get(r[0]).get(c[0]).get(t[0]).get(i[0])[0][0][2] = ss(j[17],i[1][1][8],i[1][1][11])
                                abnormallies.append([ss(j[14],i[1][1][6],i[1][1][9]),ss(j[16],i[1][1][7],i[1][1][10]),ss(j[17],i[1][1][8],i[1][1][11])]+j[3:])
    
    return abnormallies

   
    
def one_pair(MR,ts,te,rx,tx):
    #wspr query
    #colums, database, start dateTime, end dateTime, rx_sign = None, tx_sign = None limit = None
    q = query.wsprlive_get("*", "rx", str(ts), str(te), rx, tx)
    #q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
    print("wspr.rx query successful") #check if proccessing is slow
    
    #id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code

    #extract needed data
    print(q[0].get('rx_sign'),q[0].get('rx_lat'),q[0].get('rx_lon'),q[0].get('rx_loc'),q[0].get('tx_sign'),q[0].get('tx_lat'),q[0].get('tx_lon'),q[0].get('tx_loc'))
    data = []
    transmitions = {}
    b = q[0].get('band')
    for i in q:
        if i.get('band') == b:#ensure same band
            #adding new time
            if transmitions.get(i.get('time')) == None:
                transmitions.update({i.get('time'):[[],[0,0,0,0,0,0,None,None,None,None,None,None,None,[]]]})#[sum:freq,snr,drift,sum:freq^2,snr^2,drift^2,mean:freq,snr,drift,SD:freq,snr,drift,numOfSpots,sliding window]
            #pushing in new data  
            transmitions.get(i.get('time'))[0].append([i.get('band'),i.get('frequency'),i.get('snr'),i.get('drift'),0,0,0])#SS: freq, snr, drfit
            
            #calculating sum for freq, SNR and drift
            transmitions.get(i.get('time'))[1][0]+=i.get('frequency')
            transmitions.get(i.get('time'))[1][1]+=i.get('snr')
            transmitions.get(i.get('time'))[1][2]+=i.get('drift')
    
            #calculating sum for freq^2, SNR^2 and drift^2
            transmitions.get(i.get('time'))[1][3]+=i.get('frequency')**2
            transmitions.get(i.get('time'))[1][4]+=i.get('snr')**2
            transmitions.get(i.get('time'))[1][5]+=i.get('drift')**2
    
    transmitions = dict(sorted(transmitions.items()))
            
    #sliding(only actually going through each spot once so still O(N))   
    numOfSpots = 1
    left = 0
    right = 0
    ft = list(transmitions)[0]
    lt = list(transmitions)[-1]
    slidingWindow = [0,0,0,0,0,0]#sum:freq,snr,drift,sum:freq^2,snr^2,drift^2
    for t in range(0, len(transmitions.items())):
        if datetime.datetime.strptime(list(transmitions.keys())[t], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(ft, '%Y-%m-%d %H:%M:%S') < MR:#
            slidingWindow[0] += transmitions.get(list(transmitions.keys())[t])[1][0]
            slidingWindow[1] += transmitions.get(list(transmitions.keys())[t])[1][1]
            slidingWindow[2] += transmitions.get(list(transmitions.keys())[t])[1][2]
            slidingWindow[3] += transmitions.get(list(transmitions.keys())[t])[1][3]
            slidingWindow[4] += transmitions.get(list(transmitions.keys())[t])[1][4]
            slidingWindow[5] += transmitions.get(list(transmitions.keys())[t])[1][5]
            numOfSpots += len(transmitions.get(list(transmitions.keys())[t])[0])
            right = t+1
            
            
        elif datetime.datetime.strptime(lt, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(transmitions.keys())[t], '%Y-%m-%d %H:%M:%S') < MR:
            break
        else:
            for j in  range(left, t+1):
                if datetime.datetime.strptime(list(transmitions.keys())[t], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(transmitions.keys())[j], '%Y-%m-%d %H:%M:%S') > MR:
                    slidingWindow[0] -= transmitions.get(list(transmitions.keys())[j])[1][0]
                    slidingWindow[1] -= transmitions.get(list(transmitions.keys())[j])[1][1]
                    slidingWindow[2] -= transmitions.get(list(transmitions.keys())[j])[1][2]
                    slidingWindow[3] -= transmitions.get(list(transmitions.keys())[j])[1][3]
                    slidingWindow[4] -= transmitions.get(list(transmitions.keys())[j])[1][4]
                    slidingWindow[5] -= transmitions.get(list(transmitions.keys())[j])[1][5]
                    numOfSpots -= len(transmitions.get(list(transmitions.keys())[t])[0])
                    #print(-len(transmitions.get(list(transmitions.keys())[t])[0]))
                else:
                    left = j
                    break
            for j in  range(right, len(transmitions.items())):
                #print(datetime.datetime.strptime(list(transmitions.keys())[j], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(transmitions.keys())[t], '%Y-%m-%d %H:%M:%S'))
                if datetime.datetime.strptime(list(transmitions.keys())[j], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(transmitions.keys())[t], '%Y-%m-%d %H:%M:%S') <= MR and j != len(transmitions.items())-1:
                    slidingWindow[0] += transmitions.get(list(transmitions.keys())[j])[1][0]
                    slidingWindow[1] += transmitions.get(list(transmitions.keys())[j])[1][1]
                    slidingWindow[2] += transmitions.get(list(transmitions.keys())[j])[1][2]
                    slidingWindow[3] += transmitions.get(list(transmitions.keys())[j])[1][3]
                    slidingWindow[4] += transmitions.get(list(transmitions.keys())[j])[1][4]
                    slidingWindow[5] += transmitions.get(list(transmitions.keys())[j])[1][5]
                    numOfSpots += len(transmitions.get(list(transmitions.keys())[t])[0])
                    #print(len(transmitions.get(list(transmitions.keys())[t])[0]))
                else:
                    right = j
                    break
            #mean
            transmitions.get(list(transmitions.keys())[t])[1][6] = slidingWindow[0]/numOfSpots
            transmitions.get(list(transmitions.keys())[t])[1][7] = slidingWindow[1]/numOfSpots
            transmitions.get(list(transmitions.keys())[t])[1][8] = slidingWindow[2]/numOfSpots
            #SD
            transmitions.get(list(transmitions.keys())[t])[1][9] = SD(slidingWindow[3],slidingWindow[0]/numOfSpots,numOfSpots)
            transmitions.get(list(transmitions.keys())[t])[1][10] = SD(slidingWindow[4],slidingWindow[1]/numOfSpots,numOfSpots)
            transmitions.get(list(transmitions.keys())[t])[1][11] = SD(slidingWindow[5],slidingWindow[2]/numOfSpots,numOfSpots)

            #numofspots
            transmitions.get(list(transmitions.keys())[t])[1][12] = numOfSpots
            #sliding window
            transmitions.get(list(transmitions.keys())[t])[1][13] = copy.deepcopy(slidingWindow)
    
    #calculating standard score and detecting abnormallies
    for t in transmitions.items():
        for i in range(0,len(t[1][0])):
            if t[1][1][6] != None and t[1][1][7] != None and t[1][1][8] != None and t[1][1][9] != None and t[1][1][10] != None and t[1][1][11] != None:
                transmitions.get(t[0])[0][i][4] = ss(t[1][0][i][1],t[1][1][6],t[1][1][9])
                transmitions.get(t[0])[0][i][5] = ss(t[1][0][i][2],t[1][1][7],t[1][1][10])
                transmitions.get(t[0])[0][i][6] = ss(t[1][0][i][3],t[1][1][8],t[1][1][11])
    
    for i in transmitions.keys():
        for j in transmitions.get(i)[0]:
            data.append({'time': i, 'band': j[0], 'frequency': j[1], 'snr': j[2], 'drift':j[3], 'SS:freq':j[4], 'SS:snr':j[5], 'SS:drift':j[6], 'Numofspots':transmitions.get(i)[1][12]})
    
    

    
    #print anomallies
    sst = 2.0
    for i in data:
        if abs(i.get('SS:freq')) >= sst or abs(i.get('SS:snr')) >= sst or abs(i.get('SS:drift')) >= sst:
            print(i)
    
    print_csv('pair',rx,tx,ts,te,MR, data)
    
    
    
    #print (transmitions)       

if __name__ == "__main__":
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,10,0,0)
    MR = datetime.timedelta(minutes = 180)
    
    #pair_KL3RR_WF1A_2024-09-01_00-00-00_2024-09-03_23-59-59_3-00-00
    #one_pair(MR, s, e, 'KL3RR', 'VE7AHT')    
    
    #one_pair(MR, datetime.datetime(2024,7,24,9,26,0), datetime.datetime(2024,7,24,9,30,0), 'KJ6MKI', 'W6LPM')
    all_spots(MR, s, e)

                    

            
                    