import urllib.request
import json
import time
import os
import datetime
import process

#   name             type
#|id        |UInt64                |
#|time      |DateTime              |
#|band      |Int16                 |
#|rx_sign   |LowCardinality(String)|
#|rx_lat    |Float32               |
#|rx_lon    |Float32               |
#|rx_loc    |LowCardinality(String)|
#|tx_sign   |LowCardinality(String)|
#|tx_lat    |Float32               |
#|tx_lon    |Float32               |
#|tx_loc    |LowCardinality(String)|
#|distance  |UInt16                |
#|azimuth   |UInt16                |
#|rx_azimuth|UInt16                |
#frequency  |UInt32                |
#|power     |Int8                  |
#|snr       |Int8                  |
#|drift     |Int8                  |
#|version   |LowCardinality(String)|
#|code      |Int8                  |

#query data from wspr.net
def wsprlive_get(col, database, ts, te, rx = None, tx = None, l=None): #colums, database, start dateTime, end dateTime, rx_sign = None, tx_sign = None limit = None
    st = time.process_time()    
    # put together the request url
    q = "SELECT " + col + " FROM " + database + " WHERE time >= '" + ts + "' AND time < '" + te + "'"
    
    if rx != None:
        q += " AND rx_sign == '" + rx + "'"
    if tx != None:
        q += " AND tx_sign == '" + tx + "'"
    if l != None:
        q += " Limit " + str(l)
        
    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(q + " AND rx_lon < '15' AND rx_lon > '-15' " + " FORMAT JSON")
      
    # download contents from wspr.live
    contents = urllib.request.urlopen(url).read()
    
    print("wsprlive_get,",time.process_time()-st)
    # return the json decoded data
    return json.loads(contents.decode("UTF-8"))["data"]

#print data to json to accomodate large amt of data
def print_json(t, ts, te, MR, data, rx = None, tx = None):#type, ts, te, MR, data, *rx, *tx
    #checking if one_pair or all_pairs
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
    #file path and naming
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr/data/json"
    filename = t+rx+tx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+'_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'.txt' #type_rx_tx_ts_te_MR.txt
    abs_file = os.path.join(base_dir, filename)
    #writing to json
    with open(abs_file, 'w') as file: 
        file.write(json.dumps(data))

#reading data from json to accomodate large amt of data
def read_json(t, ts, te, MR, rx = None, tx = None):
    st = time.process_time()
    #checking if one_pair or all_pairs
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
    #file path and naming
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr/data/json"
    filename = t+rx+tx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+'_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'.txt' #type_rx_tx_ts_te_MR.txt
    abs_file = os.path.join(base_dir, filename)
    #reading from json
    with open(abs_file, 'r') as file: 
        data = file.read()
        print("read_json,",time.process_time()-st)
        return json.loads(data)

#putting data queried from WSPR into json file
def wspr_to_json(t, ts, te, MR, rx = None, tx = None):
    st = time.process_time()
    q = wsprlive_get("*", "rx", str(ts), str(te))
    print('wspr.rx query successful')
    print("Wspr_to_json,",time.process_time()-st)#incase wspr dies
    print_json(t, ts, te, MR, q, rx, tx)

if __name__ == "__main__":
    #print(wsprlive_get("*", "rx", '2024-09-01 00:00:00', '2024-09-01 07:00:00'))
    s = datetime.datetime(2024,9,2,20,0,0) #Y,M,D,h,m,s
    e = datetime.datetime(2024,9,3,0,0,0)
    MR = datetime.timedelta(minutes = 180)
    
    process.print_csv('all_UTC',s,e,MR,wsprlive_get("*", "rx", str(s), str(e)))
    
    #wspr_to_json('all', s, e, MR)