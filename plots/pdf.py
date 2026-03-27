import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("bubbles.csv")

# Print column names so you can choose the right one
print("Columns:", df.columns)

# Select the column (replace 'your_column_name' with the actual column)
column_name = "x"

# Drop missing values (optional but recommended)
data = df[column_name].dropna()

# Create histogram
plt.hist(data/max(data), bins=20, edgecolor='black')

# Labels and title
plt.xlabel(r'$\eta$')
plt.ylabel("PDF")
plt.title(f"Mixing of a conserved scalar")

# Show plot
plt.show()
