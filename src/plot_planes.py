import matplotlib.pyplot as plt
#import adsb_2024_9_1_153800 as data

#points = data.d.get('aircraft')
lon = [-156.24373,-155.74309,-154.59226,-154.99647,-155.03055,-155.74309,-155.39303,-154.27704,-152.75628,-152.82033,-141.01744,-160.20577,-158.12743,-153.29393,-143.89013,-146.65128,-151.20132,-149.8412]
lat = [22.5214,22.36971,21.23173,19.96724,19.72147,22.36971,24.19889,27.31025,28.69507,26.92797,43.41007,44.02549,44.89581,49.43989,58.74793,60.37248,60.58022,60.9957]

crx = [-149.958, 61.146] #lon, lat
ctx = [-155.04, 19.4792]

#for i in points:
#    if i.get('lat') != None:
#        a = i.get('lon')
#        b = i.get('lat')
#    if (abs(a-crx[0]) < abs(crx[0]-ctx[0]) or abs(a-ctx[0]) < abs(crx[0]-ctx[0])) and (abs(b-crx[1]) < abs(crx[1]-ctx[1]) or abs(b-ctx[1]) < abs(crx[1]-ctx[1])): 
#        lon.append(a)
#        lat.append(b)
    
plt.figure(figsize=(10,6))

plt.scatter(lon, lat, linewidths=1)
plt.plot([crx[0], ctx[0]], [crx[1], ctx[1]], c= "red")

plt.title("2024-08-31  6:38:00")

