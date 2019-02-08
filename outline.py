# some notes
# for rollover, it needs to reach higher
# for buying at lower, it just needs to reach exact

import numpy as np

# choose parameters
STOCK_SYMBOL = None #stock_symbol
START_DATE_TIME = None #start_date_time
CAPITAL_AMOUNT = 1 #capital_amount
MAX_EXPECTED_DEPRECIATION_RATE = 0 #max_expected_depreciation_rate
RATIO_STEP_SIZE = 0 #ratio_step_size

# get the high and low prices
historical_prices = read_hist_data(STOCK_SYMBOL, start=START_DATE_TIME) # (ToDo - create read_hist_data functions)
start_price = historical_prices["price"][0]
lowest_expected_price = start_price * (1 - MAX_EXPECTED_DEPRECIATION_RATE)

# create list of price buy/sell points
price_points = []
new_point = round(lowest_expected_price,2) # lowest point
while new_point < start_price:
	price_points.append(new_point) # other points
	new_point = round(new_point * RATIO_STEP_SIZE, 2)
price_points.append(round(start_price,2) + .01) # starting price_point (we're selling once we get to a new high)
# conver to np.array
price_points = np.array(price_points)

# set amount to buy of each (only whole shares)
num_points = len(price_points)
available_per_point = CAPITAL_AMOUNT / num_points
shares_to_buy = [round(available_per_point / price_point, 0) for price_point in price_points)]
# convert to np.array
shares_to_buy = np.array(shares_to_buy)

# set up current state variables (we start with one position of current start point)
current_capital_available = CAPITAL_AMOUNT
price_point_index = num_points - 1
positions = {}
positions[current_price_point_index] = [(price_points[initial_index], shares_to_buy[initial_index])] # price_point_index: [(price_bought, num_shares_bought)*]
current_capital_available -= price_points[initial_index] * shares_to_buy[initial_index] 

# set up historical variables
capital_available = []
num_positions = []
profit_made = []

# run the simulation

for sim_index in range(1,num_points):
	new_price = historical_prices[sim_index]
	new_position = price_points.searchsorted(new_price)
	if new_position in [price_point_index, price_point_index + 1]: # nothing happened, just move on
		pass
	elif new_position < price_point_index:
		pass
		# time to buy a new position
	else: 
		pass
		# time to sell/rollover positions

