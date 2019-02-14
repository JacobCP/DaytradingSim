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

# create series of sim information:
sim_info = pd.Series()
# starting parameters
sim_info["stock"] = STOCK_SYMBOL
sim_info["start"] = START_DATE_TIME
sim_info["end"] = END_DATE_TIME
sim_info["capital"] = CAPITAL_AMOUNT
sim_info["depreciation_accounted_for"] = MAX_EXPECTED_DEPRECIATION_RATE
sim_info["appreciation_step_size"] = GROWTH_STEP_SIZE
sim_info["num_price_points"] = sim_holdings.get_num_price_points()

# run the simulation
for sim_index in range(1, len(historical_prices)-1):
	new_price = historical_prices.iloc[sim_index, 0]
	new_date_time = historical_prices.iloc[sim_index, 1]
	sim_holdings.sim_step(new_price, new_date_time)

last_index = historical_prices[-1]
sim_holdings.last_sim_step(historical_prices.iloc[last_index ,0], historical_prices.iloc[last_index, 1])

#################
# get results
#################

# add results to sim_info
sim_info["profit_made"] = sim_holdings.get_current_total_profit()
sim_info["total_transactions"] = sim_holdings.get_current_total_transactions()
sim_info["max_positions"] = sim_holdings.get_max_positions_held()
sim_info["min_capital_available"] = sim_holdings.get_min_capital_available()	

full_results = sim_holdings.get_historical()