import process
import query
import plot_planes
import check
import datetime

#processing details
s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2024,9,1,0,0,0)
MR = datetime.timedelta(minutes = 180)

#query.wspr_to_json('all', s, e, MR, 'KL3RR', 'VE7AHT')
#process.one_pair(MR, s, e, 'KL3RR', 'VE7AHT', 'r')
print(check.intersect_greatcircle([37.396,-122.375], [-27.521,152.958], [-41.021,173.042], [38.479,-123.042]))