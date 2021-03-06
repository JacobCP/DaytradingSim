import numpy as np
from sim_functions import Holdings
from data_in_out import read_hist_data, save_results
import pandas as pd

# choose parameters
STOCK_SYMBOL = "IVV" 
START_DATE_TIME = "2003-01-02 09:32:00" # beginning of 2002
MIN_MONTH_DURATION = 13 * 12 # till end of 2015
CAPITAL_AMOUNT = 1000000
MAX_EXPECTED_DEPRECIATION_RATE = .60
GROWTH_STEP_SIZES = np.linspace(.002,.1,50)

# get the high and low prices
historical_prices = read_hist_data(STOCK_SYMBOL)

# prepare dataset to compare different trials
compare_results_columns = ["profit_made", "percent_return", "total_sales", "max_positions", "min_capital_available"]
compare_results = pd.DataFrame(columns = compare_results_columns)

for growth_size_step in GROWTH_STEP_SIZES:
	# Create simulation object
	sim_holdings = Holdings(historical_prices, START_DATE_TIME, CAPITAL_AMOUNT, growth_size_step, MAX_EXPECTED_DEPRECIATION_RATE, min_months_duration=MIN_MONTH_DURATION)

	# run the simulation
	sim_holdings.run_sim()

	# get sim_info / results
	sim_start_info = sim_holdings.get_sim_info()
	sim_results_info = sim_holdings.get_results_info()
	full_historical = sim_holdings.get_historical()

	compare_results.loc[growth_size_step] = sim_results_info

	# save full history for each growth_step_size
	save_results([full_historical], STOCK_SYMBOL, ["full_historical_" + str(round(growth_size_step,3))])

# save datasets with other info, and comparing results for different growth_step_sizes 
sim_start_info = sim_start_info.drop(["appreciation_step_size", "num_price_points"])
save_results([sim_start_info, compare_results], STOCK_SYMBOL, ["sim_parameters", "compare_results"])
	


