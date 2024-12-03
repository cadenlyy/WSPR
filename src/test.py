import os
import json
import time
import datetime

filename = "20241121_092952"

st = time.process_time()
base_dir = 'C:\\Users\\caden\\Documents\\code\\Real\\WSPR\\data\\bst'
filename += '.bst'
abs_file = os.path.join(base_dir, filename)
#reading from json
with open(abs_file, 'r') as file: 
    data = file.read()
    print("read_bst,",time.process_time()-st)
    d = ""
    pd = []
    o = []
    for i in data:
        if i == "\n":
            pd.append(d)
            d = ""
            o.append(pd)
            pd = []
        elif i == ',':
            pd.append(d)
            d = ""
        elif i != '"':
            d+=i

for i in o:
    print(i)
    print(datetime.datetime(int(i[0][0:4]),int(i[0][5:7]),int(i[0][8:10]),int(i[1][0:2]),int(i[1][3:5])))
        