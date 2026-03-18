import numpy as np
import matplotlib.pyplot as plt
import math
# https://doi.org/10.1016/S0301-7516(97)00073-2
# Generate x values from 0 to 0.5 pi

np.cot = lambda x: 1 / np.tan(x)

phim = np.linspace(1e-6, 0.5 * np.pi, 500)  # 500 points for smooth curve
phi0 = 10*np.pi/180
Db = 0.001 
Dp = 0.0001
U = 4

Re = U*Dp/10**(-6)

V = 1/6*np.pi*Db**3
X = 3/2+9*Re/(32+9.888*Re**0.694)
Y = 3*Re/(8+1.736*Re**0.518)
C = V/U*(Db/Dp)**2
D = (math.sqrt((X+C)**2+3*Y**2)-(X+C))/(3*Y)
M = -9/4-27*Re/64+0.2266*Re**1.1274
N = -0.437*Re**1.0562

A = V/U + Db/Db*X+(Dp/Db)**2*M
B = Dp/Db*Y/A+(Dp/Db)**2*N/A

ts = ((Dp + Db) / (2*U*(1-B**2)*A) * 
np.log((np.tan(phim/2)/np.tan(phi0/2))*
(1/(np.sin(phim)+B*np.cot(phim))/
1/(np.sin(phi0)+B*np.cot(phi0)))**B))

# Plot
plt.plot(phim*90/np.pi, ts, label='ts', color='blue')
plt.title('Bubble–particle collision and attachment')
plt.xlabel('Grazing angle ')
plt.ylabel('Induction time in s')
plt.grid(True)
plt.legend()
plt.ylim(0, max(ts))
#plt.show()

plt.savefig("plot.png")
