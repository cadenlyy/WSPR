from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import check

map = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,
            llcrnrlon=-180,urcrnrlon=180,resolution='c')

def fdrawgreatcircle(maplength,p1_lon, p1_lat,p2_lon,p2_lat, linewidth = 1, c = 'red', zorder = 1):
    
    #checking for left most node
    if p1_lon > p2_lon:
        lat1 = p2_lat
        lon1 = p2_lon
        lat2 = p1_lat
        lon2 = p1_lon
    else:
        lat1 = p1_lat
        lon1 = p1_lon
        lat2 = p2_lat
        lon2 = p2_lon
    #check if it crosses boarder of map
    if lon1-maplength[0]+maplength[1]-lon2 <= lon2-lon1:
        lmp = check.intersect_greatcircle([lat1, lon1], [lat2,lon2], [-90, maplength[0]], [90, maplength[0]])
        rmp = check.intersect_greatcircle([lat1, lon1], [lat2,lon2], [-90, maplength[1]], [90, maplength[1]])
        if lmp[1] == maplength[0]:
            if abs(lat1 - lmp[0]) < 1 and abs(lon1 - lmp[1]) < 3:
                lat1+=1
            map.drawgreatcircle(lon1, lat1, lmp[1], lmp[0], linewidth = linewidth, c = c, zorder = zorder)
        else:
            if abs(lat1 - lmp[2]) < 1 and abs(lon1 - lmp[3]) < 3:
                lat1+=1
            map.drawgreatcircle(lon1, lat1, lmp[3], lmp[2], linewidth = linewidth, c = c, zorder = zorder)
        if lmp[1] == maplength[0]:
            if abs(lat2 - rmp[0]) < 1 and abs(lon2 - rmp[1]) < 3:
                lat2+=1
            map.drawgreatcircle(lon2, lat2, rmp[1], rmp[0], linewidth = linewidth, c = c, zorder = zorder)
        else:
            if abs(lat2 - rmp[2]) < 1 and abs(lon2 - rmp[3]) < 3:
                lat2+=1
            map.drawgreatcircle(lon2, lat2, rmp[3], rmp[2], linewidth = linewidth, c = c, zorder = zorder)
    else:
        if abs(lat1 - lat2) < 1 and abs(lon1 - lon2) < 3:
            lat1+=1
        map.drawgreatcircle(lon1, lat1, lon2, lat2, linewidth = linewidth, c = c, zorder = zorder)

p1_lat1 = 48.563
p1_long1 = 9.875
p1_lat2 = 48.354
p1_long2 = 9.875


fdrawgreatcircle([-180,180],p1_long1, p1_lat1, p1_long2, p1_lat2, linewidth = 1)