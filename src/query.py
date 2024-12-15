import urllib.request
import json
import time
import os
import datetime
import process

#   name             type
#|id        |UInt64                |The unique spot id (same id as used by wsprnet.org)
#|time      |DateTime              |The time the spot was received and reported
#|band      |Int16                 |The band the transmission took place on (First digit of Frequency not the band in meter!) (-1: LF, 0: MF, 1: 160m, … see band table below for translations)
#|rx_sign   |LowCardinality(String)|The receiver callsign
#|rx_lat    |Float32               |The receiver latitude in degrees (derived from rx_loc)
#|rx_lon    |Float32               |The receiver longitude in degrees (derived from rx_loc)
#|rx_loc    |LowCardinality(String)|The receiver locator
#|tx_sign   |LowCardinality(String)|The sender callsign
#|tx_lat    |Float32               |The sender latitude in degrees (derived from tx_loc)
#|tx_lon    |Float32               |The sender longitude in degrees (derived from tx_loc)
#|tx_loc    |LowCardinality(String)|The sender locator
#|distance  |UInt16                |The distance in km
#|azimuth   |UInt16                |The sender azimuth (as on wsprnet.org angle of receiver as seen from the transmitter 0 to 359)
#|rx_azimuth|UInt16                |The receiver azimuth (angle of incoming short path as seen from the receiver 0 to 359)
#|frequency |UInt32                |The receive frequency in Hz
#|power     |Int8                  |The reported transmit power in dBm (might be wrong when used for other stats)
#|snr       |Int8                  |The reported snr in dB
#|drift     |Int8                  |The reported frequency drift (-3 to 3 unknown unit, might be Hz)
#|version   |LowCardinality(String)|The receiver software version string as reported (see wsprnet.org forum for details on this)
#|code      |Int8                  |The code/mode flag see Wspr / FSt4W mode mappings below to find out what this values mean

#query data from wspr.net
def wsprlive_get(col, database, ts, te, rx = None, tx = None, l = None, minlat = None, minlon = None, maxlat = None, maxlon = None): #colums, database, start dateTime, end dateTime, rx_sign = None, tx_sign = None limit = None
    st = time.process_time()    
    # put together the request url
    q = "SELECT " + col + " FROM " + database + " WHERE time >= '" + ts + "' AND time < '" + te + "'"
    
    if rx != None:
        q += " AND rx_sign == '" + rx + "'"
    if tx != None:
        q += " AND tx_sign == '" + tx + "'"
    if l != None:
        q += " Limit " + str(l)
    if l != None:
        q += " Limit " + str(l)

    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(q + " FORMAT JSON")
      
    # download contents from wspr.live
    contents = urllib.request.urlopen(url).read()
    
    print("wsprlive_get,",time.process_time()-st)
    # return the json decoded data
    return json.loads(contents.decode("UTF-8"))["data"]

#print data to json to accomodate large amt of data
def print_json(tstation, tdata, ts, te, data, MR = None, ssT = None, rx = None, tx = None):#type, ts, te, MR, data, *rx, *tx
    #json file naming convention
    #typestations_typedata_rx_tx_starttime_endtime_MR_ssT
    #typestations: all(all stations) pair(one pair of stations)
    #typedata: t(all transmited and processed data) a(all anomalous transmition data no processing data) r(all raw data with no processing data, MR and ssT not in name)
    
    #checking if one_pair or all_pairs
    if rx == None:
        frx = ''
    else:
        frx = '_'
        for i in rx:
            if i != '/' and i != '\\':
                frx+=i
    if tx == None:
        ftx = ''
    else:
        ftx = '_'
        for i in tx:
            if i != '/' and i != '\\':
                ftx+=i
    #file path and naming
    base_dir = "C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\json"
    filename = tstation+"_"+tdata+frx+ftx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S") #type_rx_tx_ts_te_MR_ssT.txt
    if tdata != 'r' and tdata != 'd':
        filename += '_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'_'+str(ssT)
    filename += '.txt'
    abs_file = os.path.join(base_dir, filename)
    #writing to json
    with open(abs_file, 'w') as file: 
        file.write(json.dumps(data))
        
def clear_json(tstation, tdata, ts, te, MR = None, ssT = None, rx = None, tx = None):#type, ts, te, MR, data, *rx, *tx
    #json file naming convention
    #typestations_typedata_rx_tx_starttime_endtime_MR_ssT
    #typestations: all(all stations) pair(one pair of stations)
    #typedata: t(all transmited and processed data) a(all anomalous transmition data no processing data) r(all raw data with no processing data, MR and ssT not in name)
    
    #checking if one_pair or all_pairs
    if rx == None:
        frx = ''
    else:
        frx = '_'
        for i in rx:
            if i != '/' and i != '\\':
                frx+=i
    if tx == None:
        ftx = ''
    else:
        ftx = '_'
        for i in tx:
            if i != '/' and i != '\\':
                ftx+=i
    #file path and naming
    base_dir = "C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\json"
    filename = tstation+"_"+tdata+frx+ftx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S") #type_rx_tx_ts_te_MR_ssT.txt
    if tdata != 'r' and tdata != 'd':
        filename += '_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'_'+str(ssT)
    filename += '.txt'
    abs_file = os.path.join(base_dir, filename)
    #writing to json
    open(abs_file, 'w').close()

        
def append_json(tstation, tdata, ts, te, data, MR = None, ssT = None, rx = None, tx = None):#type, ts, te, MR, data, *rx, *tx
    #json file naming convention
    #typestations_typedata_rx_tx_starttime_endtime_MR_ssT
    #typestations: all(all stations) pair(one pair of stations)
    #typedata: t(all transmited and processed data) a(all anomalous transmition data no processing data) r(all raw data with no processing data, MR and ssT not in name)
    
    #checking if one_pair or all_pairs
    if rx == None:
        frx = ''
    else:
        frx = '_'
        for i in rx:
            if i != '/' and i != '\\':
                frx+=i
    if tx == None:
        ftx = ''
    else:
        ftx = '_'
        for i in tx:
            if i != '/' and i != '\\':
                ftx+=i
    #file path and naming
    base_dir = "C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\json"
    filename = tstation+"_"+tdata+frx+ftx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S") #type_rx_tx_ts_te_MR_ssT.txt
    if tdata != 'r' and tdata != 'd':
        filename += '_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'_'+str(ssT)
    filename += '.txt'
    abs_file = os.path.join(base_dir, filename)
    #writing to json
    with open(abs_file, 'a') as file: 
        file.write('%s,' %data)

#reading data from json to accomodate large amt of data
def read_json(tstation, tdata, ts, te, MR = None, ssT = None, rx = None, tx = None):
    #json file naming convention
    #typestations_typedata_rx_tx_starttime_endtime_MR_ssT
    #typestations: all(all stations) pair(one pair of stations)
    #typedata: t(all transmited and processed data) a(all anomalous transmition data no processing data) r(all raw data with no processing data) p(all intersections of anomalous data with anomalous link data) psh(all short path intersections of anomalous data with anomalous link data) plp(all possible intersections of anomalous data with anomalous link data) d(distance from closes plane to point)
    
    st = time.process_time()
    #checking if one_pair or all_pairs
    if rx == None:
        frx = ''
    else:
        frx = '_'
        for i in rx:
            if i != '/' and i != '\\':
                frx+=i
    if tx == None:
        ftx = ''
    else:
        ftx = '_'
        for i in tx:
            if i != '/' and i != '\\':
                ftx+=i
    #file path and naming
    base_dir = 'C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\json'
    filename = tstation+"_"+tdata+frx+ftx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S") #type_rx_tx_ts_te_MR_ssT.txt
    if tdata != 'r':
        filename += '_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'_'+str(ssT)
    filename += '.txt'
    abs_file = os.path.join(base_dir, filename)
    #reading from json
    with open(abs_file, 'r') as file: 
        data = file.read()
        print("read_json,",time.process_time()-st)
        return json.loads(data)

#putting data queried from WSPR into json file
def wspr_to_json(t, ts, te, rx = None, tx = None):
    st = time.process_time()
    q = wsprlive_get("*", "rx", str(ts), str(te),rx, tx)
    print('wspr.rx query successful')
    print("Wspr_to_json,",time.process_time()-st)#incase wspr dies
    #print(q)
    print_json(t, 'r', ts, te, q, rx = rx, tx = tx)

if __name__ == "__main__":
    #print(wsprlive_get("*", "rx", '2024-09-01 00:00:00', '2024-09-01 07:00:00'))
    s = datetime.datetime(2022,11,1,0,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,12,1,15,0,0)
    tx = 'DL4DTL'
    rx = 'SO5CW'
    
    #process.print_csv('all_UTC',s,e,MR,wsprlive_get("*", "rx", str(s), str(e)))
    
    wspr_to_json('pair', s, e, rx, tx)