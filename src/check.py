import process
import datetime
import math
import numpy as np

crx = [-149.958, 61.146] #lon, lat
ctx = [-155.04, 19.4792]
ca = [-148.61223, 60.38938]#lon,lat

#print(ca[1] == ((crx[0]-ctx[0])/(crx[1]-ctx[1]))*(ca[0]-crx[0])+crx[1])
    
def intersect_greatcircle(A, B, C, D):#lat,lon
    
    p1_lat1 = A[0]
    p1_long1 = A[1]
    p1_lat2 = B[0]
    p1_long2 = B[1]

    p2_lat1 = C[0]
    p2_long1 = C[1]
    p2_lat2 = D[0]
    p2_long2 = D[1]

    # Convert points in great circle 1, degrees to radians
    p1_lat1_rad = ((math.pi * p1_lat1) / 180.0)
    p1_long1_rad = ((math.pi * p1_long1) / 180.0)
    p1_lat2_rad = ((math.pi * p1_lat2) / 180.0)
    p1_long2_rad = ((math.pi * p1_long2) / 180.0)

    # Convert points in great circle 2, degrees to radians
    p2_lat1_rad = ((math.pi * p2_lat1) / 180.0)
    p2_long1_rad = ((math.pi * p2_long1) / 180.0)
    p2_lat2_rad = ((math.pi * p2_lat2) / 180.0)
    p2_long2_rad = ((math.pi * p2_long2) / 180.0)

    # Put in polar coordinates
    x1 = math.cos(p1_lat1_rad) * math.cos(p1_long1_rad)
    y1 = math.cos(p1_lat1_rad) * math.sin(p1_long1_rad)
    z1 = math.sin(p1_lat1_rad)
    x2 = math.cos(p1_lat2_rad) * math.cos(p1_long2_rad)
    y2 = math.cos(p1_lat2_rad) * math.sin(p1_long2_rad)
    z2 = math.sin(p1_lat2_rad)
    cx1 = math.cos(p2_lat1_rad) * math.cos(p2_long1_rad)
    cy1 = math.cos(p2_lat1_rad) * math.sin(p2_long1_rad)
    cz1 = math.sin(p2_lat1_rad)
    cx2 = math.cos(p2_lat2_rad) * math.cos(p2_long2_rad)
    cy2 = math.cos(p2_lat2_rad) * math.sin(p2_long2_rad)
    cz2 = math.sin(p2_lat2_rad)

    # Get normal to planes containing great circles
    # np.cross product of vector to each point from the origin
    N1 = np.cross([x1, y1, z1], [x2, y2, z2])
    N2 = np.cross([cx1, cy1, cz1], [cx2, cy2, cz2])

    # Find line of intersection between two planes
    L = np.cross(N1, N2)

    # Find two intersection points
    X1 = L / np.sqrt(L[0]**2 + L[1]**2 + L[2]**2)
    X2 = -X1
    i_lat1 = math.asin(X1[2]) * 180./np.pi
    i_long1 = math.atan2(X1[1], X1[0]) * 180./np.pi
    i_lat2 = math.asin(X2[2]) * 180./np.pi
    i_long2 = math.atan2(X2[1], X2[0]) * 180./np.pi

    # Print results
    if (abs(i_lat1 - p1_lat1) < abs(i_lat2 - p1_lat1)):
        print (i_lat1, i_long1)
    else:
        print(i_lat2, i_long2)


    
s = datetime.datetime(2024,9,1,0,0,0) #Y,M,D,h,m,s
e = datetime.datetime(2024,9,1,10,0,0)
MR = datetime.timedelta(minutes = 180)

A = process.all_spots(MR, s, e)
    