import numpy as np
from sim_functions import Holdings

# choose parameters
STOCK_SYMBOL = None #stock_symbol
START_DATE_TIME = None #start_date_time
CAPITAL_AMOUNT = 1 #capital_amount
MAX_EXPECTED_DEPRECIATION_RATE = 0 #max_expected_depreciation_rate
GROWTH_STEP_SIZE = 0 #ratio_step_size

# get the high and low prices
historical_prices = read_hist_data(STOCK_SYMBOL, start=START_DATE_TIME) # (ToDo - create read_hist_data functions)
start_price = historical_prices["price"][0]
lowest_expected_price = start_price * (1 - MAX_EXPECTED_DEPRECIATION_RATE)

# Create Holdings Instance (automatically initializes first position)
sim_holdings = Holdings(CAPITAL_AMOUNT, start_price, lowest_expected_price, GROWTH_STEP_SIZE)

# run the simulation

for sim_index in range(1, num_points):
	new_price = historical_prices[sim_index]
	Holdings.sim_step(new_price)
