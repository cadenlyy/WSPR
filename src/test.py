import process
import datetime

s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2024,9,1,0,0,1)
MR = datetime.timedelta(minutes = 180)

#pair_KL3RR_WF1A_2024-09-01_00-00-00_2024-09-03_23-59-59_3-00-00
#one_pair(MR, s, e, 'KL3RR', 'VE7AHT')    

#one_pair(MR, datetime.datetime(2024,7,24,9,26,0), datetime.datetime(2024,7,24,9,30,0), 'KJ6MKI', 'W6LPM')
process.all_spots(MR, s, e)