import pandas as pd
import sys


def print_info(filename):
    # filename = sys.argv[1]
    df = pd.read_csv(filename, delim_whitespace=True)
    success_df = df.loc[df['status'] == "success"]
    print("Success statistics information")
    print(success_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].mean())

    block_df = df.loc[df['status'] == "block"]
    print("Block statistics information")
    print(block_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].mean())

    print("Total run " + str(len(df)) + " rounds")
    print("Success " + str(len(success_df)) + " rounds " + str(
        (len(success_df) / len(df)) * 100) + "%")
    print("Fail " + str(len(df) - len(success_df)) + " rounds " + str((
        (len(df) - len(success_df)) / len(df)) * 100) + "%")


if __name__ == "__main__":
    print_info(sys.argv[1])
