import pandas as pd
import sys

# filename = "WedApr251720092018.csv"
def print_info():
    filename = sys.argv[1]
    df = pd.read_csv(filename, delim_whitespace=True)
    success_df = df.loc[df['status']=="success"]
    print("Statistics information")
    print(success_df[["run_time", "route_length"]].mean())

    print("Total run " + str(len(df)) + " rounds")
    print("Success " + str(len(success_df)) + " rounds " + str((len(success_df) / len(df))*100) + "%")
    print("Fail " + str(len(df) - len(success_df)) + " rounds " + str(((len(df) - len(success_df)) / len(df))*100) + "%")

if __name__ == "__main__":
    print_info()