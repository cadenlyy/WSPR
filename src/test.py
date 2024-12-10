import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit #module to fit curves

#k_list = [15, 18, 33, 36, 39]
#v_list = 


data_to_plot = [1,2,3,2,1]

#plot pretty histogram
fig3 = plt.figure(figsize = (5,4), dpi = 150)

counts, bins, patches = plt.hist(data_to_plot, bins = 20, edgecolor='black', color = 'seagreen', density = True, alpha=0.6, label = 'FtsZ')

plt.xlim([0,150])
plt.xlabel('Velocities (nm/s)', fontsize=12)
plt.ylabel('PDF', fontsize=12)
plt.legend(loc=0, fontsize = 10, frameon = False)
#plt.title("TrackMate Info", fontsize = 12)
plt.tick_params(direction = 'in', top=False, right=False)
plt.grid(False)

# fit Gaussian function

#define function to fit
def gaussian(x, a, mu, sigma):
    return a*np.exp(-(x-mu)**2/(2*sigma**2))

#calculate bin center to use as y data to fit
bins = (bins[:-1] + np.diff(bins) / 2)

#create an arbitrary x axis to fit
x_values_to_fit = np.linspace(1,3,100)

# fit the data and plot the result
param, cov = curve_fit(gaussian, bins,counts, p0=(10,10,10))
plt.plot(x_values_to_fit, gaussian(x_values_to_fit, *param))

plt.show()