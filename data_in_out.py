import pandas as pd
import os
import numpy as np

# created for my particular historical data files
def prep_my_data(stock_symbol):
    my_data_file_path = os.path.join("stock_data", stock_symbol + "_raw.txt")
    print("reading in {}...".format(my_data_file_path))
    hist_data = pd.read_csv(my_data_file_path, usecols=["Date","Time","Open"], parse_dates=[["Date", "Time"]])
    hist_data.columns = ["Date_Time", "Price"]

    new_file_name = stock_symbol + ".txt"
    hist_data.to_csv("stock_data/" + new_file_name, index=False)
    print("successfully converted and saved to {}.".format(new_file_name))

    return hist_data


def read_hist_data(stock_symbol):
    read_file_path = os.path.join("stock_data", stock_symbol + ".txt")
    print("\nloading data from '{}'...\n".format(read_file_path))
    hist_data = pd.read_csv(read_file_path, parse_dates=[0])

    return hist_data

def save_results(results_files, stock_symbol, results_file_names):
    assert len(results_files) == len(results_file_names), "file_name and dataset lengths do not match."
    dir_name = stock_symbol + "_results"
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    for idx, file_name in enumerate(results_file_names):
        file_path = os.path.join(dir_name, file_name + ".csv")
        print("Saving {} for {} in: '{}'".format(file_name, stock_symbol, file_path))
        results_files[idx].to_csv(file_path, float_format='%.3f')