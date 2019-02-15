import pandas as pd
import os
import numpy as np

def read_hist_data(stock_symbol, start_date_time, end_date_time):
    file_name = stock_symbol + "_" \
                + pd.Timestamp(start_date_time).strftime("%Y-%m-%d-%H%M") + "_" \
                + pd.Timestamp(end_date_time).strftime("%Y-%m-%d-%H%M") + ".csv"
    file_path = os.path.join("stock_data", file_name)
    if os.path.isfile(file_path):
        hist_data = pd.read_csv(file_path)
        print("successfully loaded " + file_path + "...")
    else:
        hist_data = pd.read_csv("stock_data/" + stock_symbol + ".txt")
        print("extracting relevant fields...")
        hist_data = hist_data[["Date", "Time", "Open"]]
        print("converting time...")
        hist_data["Time"] = hist_data["Time"].astype(str).apply(lambda x: x[:-2] + ":" +  x[-2:])
        print("combining data and time...")
        hist_data["date_time"] = hist_data["Date"] + " " + hist_data["Time"]
        print("dropping date and time...")
        hist_data.drop(["Date", "Time"], axis=1, inplace=True)
        print("converting to date type") 
        hist_data["date_time"] = hist_data["date_time"].astype('datetime64[ns]')
        print("filtering out earlier ones...")
        hist_data = hist_data[hist_data["date_time"] >= pd.Timestamp(start_date_time)]
        print("filtering out later ones...")
        hist_data = hist_data[hist_data["date_time"] <= pd.Timestamp(end_date_time)]

        # reset index
        hist_data.index = np.arange(len(hist_data))

        # save for future so don't need to do each time
        hist_data.to_csv(file_path, index=False)
        print("successfully created and saved " + file_path + "...")

    return hist_data