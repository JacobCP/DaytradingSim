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

# Create Holdings Instance (automatically initializes first position)
sim_holdings = Holdings(historical_prices, CAPITAL_AMOUNT, GROWTH_STEP_SIZE, MAX_EXPECTED_DEPRECIATION_RATE)

# run the simulation
sim_holdings.run_sim()

# get sim_info / results
sim_starting_info = sim_holdings.get_sim_info()
sim_results_info = sim_holdings.get_results_info()
full_results = sim_holdings.get_historical()
