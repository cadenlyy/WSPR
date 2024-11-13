crx = [-149.958, 61.146] #lon, lat
ctx = [-155.04, 19.4792]
ca = [-148.61223, 60.38938]#lon,lat

print(ca[1] == ((crx[0]-ctx[0])/(crx[1]-ctx[1]))*(ca[0]-crx[0])+crx[1])
    

