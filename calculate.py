import pandas as pd
import sys


def print_info(filename, gedit=False):
    # filename = sys.argv[1]
    df = pd.read_csv(filename, delim_whitespace=True)
    success_df = df.loc[df['status'] == "success"]
<<<<<<< HEAD
    print("Success statistics information")
    print("MEAN")
    print(success_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].mean())
    print("STANDARD")
    print(success_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].std())

    block_df = df.loc[df['status'] == "block"]
    print("Block statistics information")
    print("MEAN")
    print(block_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].mean())
    print("STANDARD")
    print(block_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].std())
=======
    print("Success statistics information", file=open(filename, "a"))
    print(success_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].mean(), file=open(filename, "a"))

    block_df = df.loc[df['status'] == "block"]
    print("Block statistics information", file=open(filename, "a"))
    print(block_df[[
        "run_time", "route_length", "explorated_area", "unexplorated_area"
    ]].mean(), file=open(filename, "a"))
>>>>>>> bf04d406f83669c3fb4ab09ce311a08cd8c32630

    print("Total run " + str(len(df)) + " rounds", file=open(filename, "a"))
    print("Success " + str(len(success_df)) + " rounds " + str(
        (len(success_df) / len(df)) * 100) + "%", file=open(filename, "a"))
    print("Fail " + str(len(df) - len(success_df)) + " rounds " + str((
        (len(df) - len(success_df)) / len(df)) * 100) + "%", file=open(filename, "a"))

    if gedit:
        import subprocess
        proc = subprocess.Popen(['gedit', filename])

if __name__ == "__main__":
    print_info(sys.argv[1])
