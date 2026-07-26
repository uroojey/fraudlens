import sys
import pandas as pd
import numpy as np
import sklearn
import matplotlib
import seaborn as sns

print("="*50)
print("FraudLens Environment Check")
print("="*50)
print("Python version:", sys.version.split()[0])
print("Pandas version:", pd.__version__)
print("NumPy version:", np.__version__)
print("Scikit-learn version:", sklearn.__version__)
print("Matplotlib version:", matplotlib.__version__)
print("Seaborn version:", sns.__version__)
print("="*50)

# Note: Fixed the syntax error in your dictionary here: {"a":}
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df["sum"] = df["a"] + df["b"]
assert df["sum"].tolist() == [5,7,9]

print("All libraries imported successfully.")
print("Basic Pandas operation verified.")
print("Environment is ready for Day 3 data cleaning work.")
