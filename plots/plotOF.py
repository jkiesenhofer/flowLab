import pandas as pd
import matplotlib.pyplot as plt

# Load CSV file
df = pd.read_csv("p_rhg1.csv")

# Plot
plt.plot(df["Points_1"], df["p_rgh"])

# Labels
plt.xlabel("Points_1")
plt.ylabel("p_rgh")
plt.title("lskdmflca")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
