import numpy as np
from sim_functions import Holdings
from data_in_out import read_hist_data
import pandas as pd

# choose parameters
STOCK_SYMBOL = "QQQ" 
START_DATE_TIME = "2007-10-31 2:58 pm"
END_DATE_TIME = "2010-12-7 9:30 am"
CAPITAL_AMOUNT = 1000000
MAX_EXPECTED_DEPRECIATION_RATE = .60
GROWTH_STEP_SIZE = .005

# get the high and low prices
historical_prices = read_hist_data(STOCK_SYMBOL, START_DATE_TIME, END_DATE_TIME) # (ToDo - create read_hist_data functions)
start_price = historical_prices["Open"][0]
lowest_expected_price = start_price * (1 - MAX_EXPECTED_DEPRECIATION_RATE)

# Create Holdings Instance (automatically initializes first position)
sim_holdings = Holdings(CAPITAL_AMOUNT, START_DATE_TIME, start_price, lowest_expected_price, GROWTH_STEP_SIZE)

# run the simulation
for sim_index in range(1, len(historical_prices)-1):
	new_price = historical_prices.iloc[sim_index, 0]
	new_date_time = historical_prices.iloc[sim_index, 1]
	sim_holdings.sim_step(new_price, new_date_time)

last_index = historical_prices[-1]
sim_holdings.close_simulation(historical_prices.iloc[last_index ,0], historical_prices.iloc[last_index, 1])

