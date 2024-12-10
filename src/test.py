import numpy as np
import matplotlib.pyplot as plt
import scipy

data_to_plot = [1,2,3,4,5,1,1,2,2,4]

#plot pretty histogram
fig3 = plt.figure(figsize = (5,4), dpi = 150)

counts, bins, patches = plt.hist(data_to_plot,5)

print(counts)

# fit Gaussian function

#define function to fit
def gaussian(x, a, mu, sigma):
    return a*np.exp(-(x-mu)**2/(2*sigma**2))

#calculate bin center to use as y data to fit
bins = (bins[:-1] + np.diff(bins) / 2)

#create an arbitrary x axis to fit
x_values_to_fit = np.linspace(0,6,100)

# fit the data and plot the result
param, cov = scipy.optimize.curve_fit(gaussian, xdata = bins, ydata = counts, maxfev=5000)
plt.plot(x_values_to_fit, gaussian(x_values_to_fit, *param), '-', color = 'purple', lw=1.5, label = "Gaussian")


plt.show()
