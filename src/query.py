import urllib.request
import json
import time
import os

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

def wsprlive_get(col, database, ts, te, rx = None, tx = None, l=None):
    # put together the request url
    q = "SELECT " + col + " FROM " + database + " WHERE time >= '" + ts + "' AND time < '" + te + "'"
    
    if rx != None:
        q += " AND rx_sign == '" + rx + "'"
    if tx != None:
        q += " AND tx_sign == '" + tx + "'"
    if l != None:
        q += " Limit " + str(l)
        
    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(q + " FORMAT JSON")
      
    # download contents from wspr.live
    contents = urllib.request.urlopen(url).read()
    
    print(time.process_time())
    # return the json decoded data
    return json.loads(contents.decode("UTF-8"))["data"]

def print_json(t, ts, te, MR, data, rx = None, tx = None):
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
        
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr/data/json"
    filename = t+rx+tx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+'_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'.txt'
    abs_file = os.path.join(base_dir, filename)
    with open(abs_file, 'w') as file: 
        file.write(json.dumps(data))

def read_json(t, ts, te, MR, rx = None, tx = None):
    if rx == None:
        rx = ''
    else:
        rx = '_'+rx
    if tx == None:
        tx = ''
    else:
        tx = '_'+tx
    base_dir = "C:/Users/Lyiyang1/Desktop/wspr/data/json"
    filename = t+rx+tx+'_'+ts.strftime("%Y-%m-%d_%H-%M-%S")+'_'+te.strftime("%Y-%m-%d_%H-%M-%S")+'_'+str(MR).split(':')[0]+'-'+str(MR).split(':')[1]+'-'+str(MR).split(':')[2]+'.txt'
    abs_file = os.path.join(base_dir, filename)
    print(abs_file)
    with open(abs_file, 'r') as file: 
        data = file.read()
        return json.loads(data)

#pulling data
def wspr_to_json(t, ts, te, MR, rx = None, tx = None):
    q = wsprlive_get("*", "rx", str(ts), str(te))
    print('wspr.rx query successful')
    print_json(t, ts, te, MR, q, rx, tx)

if __name__ == "__main__":
    print(wsprlive_get("*", "rx", '2024-09-01 00:00:00', '2024-09-01 07:00:00'))
