import copy
import query
import datetime
import math
import csv
import os
import time


def roundEvenDateTime(a): #YYYY-MM-DD HH:MM:SS
    return datetime.datetime.strptime(str(a)[:15]+str(int(str(a)[15])%2+int(str(a)[15]))+str(a)[16:], '%Y-%m-%d %H:%M:%S')

def SD(s, m, n):#sum of x^2, mean, number of values
    try:
        return math.sqrt(float(s/(n-1)-((n*m**2)/(n-1))))
    except ValueError:
        return 0
    except ZeroDivisionError:
        return 0

def ss(v, m, sd):#value, mean, standard deviation
    if sd != 0:
        return (v-m)/sd
    return 0
    
def print_csv(tstations, tdata, ts, te, MR, ssT, data, rx = None, tx = None):#output to csv file
    #csv file naming convention
    #typestations_typedata_rx_tx_starttime_endtime_MR,ssT
    #typestations: all(all stations) pair(one pair of stations)
    #typedata: t(all transmited and processed data) a(all anomalous transmition data no processing data)
    st = time.process_time()    
    #check or one pair or multiple    
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
    #file path and nameing
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr/data/csv"
    filename = tstations+'_'+tdata+rx+tx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+'_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'_'+str(ssT)+'.csv' #type_rx_tx_ts_te_MR.csv
    abs_file = os.path.join(base_dir, filename)
    
    #writing to csv file
    with open(abs_file, 'w', newline='') as csvfile:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print('print_csv,',time.process_time()-st)
        
#main processing and calculation of anomalous data
def anomalies(f, MR, ssT, ts, te, rx = None, tx = None):
    st = time.process_time()
    #wspr query
    #id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
    if f == 'r':#read from json
        if rx == None and tx == None:
            q = query.read_json('all', 'r', ts, te)
        else:
            q = query.read_json('pair', 'r', ts, te, rx, tx)
    if f == 'q':
        q = query.wsprlive_get("*", "rx", str(ts), str(te), rx, tx)
    elif f == 't': #testcase
        q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
    
    print("wspr.rx query successful") #check if proccessing is slow
    
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
            transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).update({data[1]:[[],[0,0,0,0,0,0,None,None,None,None,None,None,None,[None,None,None,None,None,None]]]}) #[sum:freq,snr,drift,sum:freq^2,snr^2,drift^2,mean:freq,snr,drift,SD:freq,snr,drift,numOfSpots,sliding window]
        #pushing in transmittion info                                    
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[0].append([0,0,0]+data)#SS_freq,SS_snr,SS_drift,id, time, band, rx_sign, rx_lat, rx_lon, rx_loc, tx_sign, tx_lat, tx_lon, tx_loc, distance, azimuth, rx_azimuth, *frequency, power, *snr, *drift, version, code
    
        #calculating sum for freq, SNR and drift
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][0]+=data[14]
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][1]+=data[16]
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][2]+=data[17]
    
        #calculating sum for freq^2, SNR^2 and drift^2
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][3]+=data[14]**2
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][4]+=data[16]**2
        transmitions.get(tuple(data[3:7])).get(tuple(data[7:11])).get(data[2]).get(data[1])[1][5]+=data[17]**2

    #sliding(only actually going through each spot once so still O(N))   
    for r in transmitions.items():# receivers
        for c in r[1].items():#transmitters
            for t in c[1].items():#band
                numOfSpots = 0
                left = 0
                right = 0
                ft = list(t[1])[0]#time of first spot
                lt = list(t[1])[-1]#time of last spot
                slidingWindow = [0,0,0,0,0,0]#sum:freq,snr,drift,sum:freq^2,snr^2,drift^2
                for i in range(0, len(t[1])):#time
                    #adding still MR away from start time
                    if datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(ft, '%Y-%m-%d %H:%M:%S') < MR:                 
                        slidingWindow[0] += t[1].get(list(t[1])[i])[1][0]
                        slidingWindow[1] += t[1].get(list(t[1])[i])[1][1]
                        slidingWindow[2] += t[1].get(list(t[1])[i])[1][2]
                        slidingWindow[3] += t[1].get(list(t[1])[i])[1][3]
                        slidingWindow[4] += t[1].get(list(t[1])[i])[1][4]
                        slidingWindow[5] += t[1].get(list(t[1])[i])[1][5]
                        numOfSpots += len(t[1].get(list(t[1])[i])[0])
                        right = i+1
                    #end when less then MR to end time
                    elif datetime.datetime.strptime(lt, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(list(t[1])[i], '%Y-%m-%d %H:%M:%S') < MR:
                        break
                    else:
                        #subtracting back of sliding window will within MR
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
                        #adding from of sliding window until MR
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
    a = []#anomalies
    d = []#all data in csv printable format
    for r in transmitions.items():#recievers
        for c in r[1].items():#transmitters
            for t in c[1].items():#bands
                for i in t[1].items():#times
                    for j in range(len(i[1][0])):#data of each spot
                        #checking if within MR and has valid values to calculate
                        if i[1][1][6] != None and i[1][1][7] != None and i[1][1][8] != None and i[1][1][9] != None and i[1][1][10] != None and i[1][1][11] != None:
                            #adding standard score
                            transmitions.get(r[0]).get(c[0]).get(t[0]).get(i[0])[0][j][0] = ss(i[1][0][j][17],i[1][1][6],i[1][1][9])
                            transmitions.get(r[0]).get(c[0]).get(t[0]).get(i[0])[0][j][1] = ss(i[1][0][j][19],i[1][1][7],i[1][1][10])
                            transmitions.get(r[0]).get(c[0]).get(t[0]).get(i[0])[0][j][2] = ss(i[1][0][j][20],i[1][1][8],i[1][1][11])
                            #checking for anomalies
                            if abs(ss(i[1][0][j][17],i[1][1][6],i[1][1][9]))  >= ssT or abs(ss(i[1][0][j][19],i[1][1][7],i[1][1][10]))  >= ssT or abs(ss(i[1][0][j][20],i[1][1][8],i[1][1][11]))  >= ssT:
                                #copying anomalies
                                p = i[1][0][j]
                                a.append({'SS_freq': p[0], 'SS_snr': p[1], 'SS_drift': p[2], 'id': p[3], 'time': p[4], 'band': p[5], 'rx_sign': p[6], 'rx_lat': p[7], 'rx_lon': p[8], 'rx_loc': p[9], 'tx_sign': p[10], 'tx_lat': p[11], 'tx_lon': p[12], 'tx_loc': p[13], 'distance': p[14], 'azimuth': p[15], 'rx_azimuth': p[16], 'frequency': p[17], 'power': p[18], 'snr': p[19], 'drift': p[20], 'version': p[21], 'code': p[22]})
                        d.append({'SS_freq': i[1][0][j][0], 'SS_snr': i[1][0][j][1], 'SS_drift': i[1][0][j][2], 'id': i[1][0][j][3], 'time': i[1][0][j][4], 'band': i[1][0][j][5], 'rx_sign': i[1][0][j][6], 'rx_lat': i[1][0][j][7], 'rx_lon': i[1][0][j][8], 'rx_loc': i[1][0][j][9], 'tx_sign': i[1][0][j][10], 'tx_lat': i[1][0][j][11], 'tx_lon': i[1][0][j][12], 'tx_loc': i[1][0][j][13], 'distance': i[1][0][j][14], 'azimuth': i[1][0][j][15], 'rx_azimuth': i[1][0][j][16], 'frequency': i[1][0][j][17], 'power': i[1][0][j][18], 'snr': i[1][0][j][19], 'drift': i[1][0][j][20], 'version': i[1][0][j][21], 'code': i[1][0][j][22], "sum_freq": i[1][1][0],"sum_snr": i[1][1][1],"sum_drift": i[1][1][2],"sum_freq^2": i[1][1][3],"sum_snr^2": i[1][1][4],"sum_drift^2":i[1][1][5],"mean_freq":i[1][1][6],"mean_snr":i[1][1][7],"mean_drift":i[1][1][8],"SD_freq":i[1][1][9],"SD_snr":i[1][1][10],"SD_drift":i[1][1][11],"numOfSpots":i[1][1][12],"SW_freq":i[1][1][13][0],"SW_snr":i[1][1][13][1],"SW_drift":i[1][1][13][2],"SW_freq^2":i[1][1][13][3],"SW_snr^2":i[1][1][13][4],"SW_drift^2":i[1][1][13][5]})

    #print_csv('all','t',ts,te,MR,ssT,d)
    #print_csv('all','a',ts,te,MR,ssT,a)
    #print_csv('pair','t',ts,te,MR,ssT,d,rx,tx)
    #print_csv('pair','a',ts,te,MR,ssT,a,rx,tx)
    
    #print(transmitions)
    print("anomalies,",time.process_time()-st)#checking code speed
    
    return d

if __name__ == "__main__":
    #process details
    s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,1,7,0,0)
    MR = datetime.timedelta(minutes = 180)
    ssT = 1
    
    #pair_KL3RR_WF1A_2024-09-01_00-00-00_2024-09-03_23-59-59_3-00-00
    anomalies('r', MR, ssT, s, e)    
    
    #one_pair(MR, datetime.datetime(2024,7,24,9,26,0), datetime.datetime(2024,7,24,9,30,0), 'KJ6MKI', 'W6LPM')
    #all_spots(MR, s, e)

#archival code just incase
''' 
def one_pair(f,MR,ts,te,rx,tx):
    #wspr query
    #colums, database, start dateTime, end dateTime, rx_sign = None, tx_sign = None limit = None
    if f == 'r':
        q = query.read_json('pair', ts, te, MR, rx, tx)
    elif f =='t':
        q = [{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1, 'power': 23, 'snr': 1, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:26:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 2, 'power': 23, 'snr': -7, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:28:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 1000000000000000000000000, 'power': 23, 'snr': 3, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1},{'id': '8100420947', 'time': '2024-07-24 09:30:00', 'band': 7, 'rx_sign': 'IU1QQM', 'rx_lat': 44.896, 'rx_lon': 7.208, 'rx_loc': 'JN34ov', 'tx_sign': 'EA6URP', 'tx_lat': 39.563, 'tx_lon': 2.708, 'tx_loc': 'JM19in', 'distance': 699, 'azimuth': 31, 'rx_azimuth': 213, 'frequency': 4, 'power': 23, 'snr': -10, 'drift': 1, 'version': 'WD_3.0.8', 'code': 1}]
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
    
    print_csv('pair',ts,te,MR, data,rx,tx)
    print(data)
    
    print(time.process_time())
    
    
    #print (transmitions)       
'''

            
                    