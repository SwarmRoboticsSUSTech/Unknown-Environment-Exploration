import pandas as pd
import sys

# filename = "WedApr251720092018.csv"
filename = sys.argv[1]
df = pd.read_csv(filename, delim_whitespace=True)
success_df = df.loc[df['status']=="success"]
print(success_df[["run_time", "route_length"]].mean())