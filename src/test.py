import matplotlib.pyplot as plt
import numpy as np

np.random.seed(19680801)

N = 100
x = 0.9 * np.random.rand(N)
y = 0.9 * np.random.rand(N)

plt.scatter(x, y, c='green')
plt.plot(np.linspace(0, 1, 10), np.power(np.linspace(0, 1, 10), 2), c= "red", marker='.', linestyle=':')

plt.gca().invert_yaxis()
plt.show()