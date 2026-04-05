import matplotlib.pyplot as plt
a=[]
c=[]
t=[]

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
})


with open("log.foamRun", "r") as file:
    for line in file:
        if line.startswith("Courant Number mean: "):
           b=line.split(" ")
           #print(b)
           a.append(float(b[3]))
           c.append(float(b[5]))
        if line.startswith("Time = "):
           b=line.split("s")
           d=float(b[0].split(" ")[2])
           #print(c)
           t.append(d)
a = a[:-1]
c = c[:-1]


plt.subplot(1, 2, 1)
plt.plot(t,a,"k--")
plt.ylim(0, 0.06)

plt.xlabel("Time in s")
plt.ylabel("Interface Courant Number mean")

plt.subplot(1, 2, 2)
plt.plot(t,c,"k--")
plt.ylim(0, 1)

plt.xlabel("Time in s")
plt.ylabel("Max Courant Number")

plt.show()
