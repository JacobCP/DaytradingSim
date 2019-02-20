import numpy as np
import pandas as pd

class Holdings:

    def __init__(self, historical_prices, sim_start_date, initial_capital, growth_step_size, max_expected_depreciation_rate, all_time_high=None):
        # get col_names to use for readable code
        date_time_col = historical_prices.columns[0]
        price_col = historical_prices.columns[1]

        # get the index of the simulation start date - to find the previous high, and afterwards drop previous records
        date_values = historical_prices[date_time_col]
        start_date_index = np.where(date_values == sim_start_date)[0][0]
 
        # before filtering, get the previous high
        def get_previous_high(historical_prices, before_date_index):
            return np.max(date_values[:before_date_index])

        if all_time_high is not None:
            self.high = all_time_high
        else:
            self.high = get_previous_high(historical_prices, start_date_index)
        print("The previous high was {}".format(self.high))
        # once we have that, we no longer need the earlier dates
        print("filtering out earlier ones...")
        historical_prices = historical_prices.iloc[start_date_index:,:].copy()

        # store arguments
        self.historical_data = historical_prices
        self.initial_capital = initial_capital
        self.growth_step_size = growth_step_size		
        self.max_expected_depreciation_rate = max_expected_depreciation_rate
        
        # other attributes
        self.price_points = None
        # point in time attributes
        self.capital = initial_capital
        self.positions = {}
        self.current_position_index = None
        self.num_positions = 0
        # historical logging attributes
        self.historical_index = 0
        for column_name in ["capital_available", "num_positions", "step_profit", "step_transactions"]:
            self.historical_data[column_name] = np.nan

        # start the simulation steps
        print("Preparing simulation for step size of {:.1%}...\n".format(growth_step_size))

        start_price = historical_prices[price_col].iloc[0]
        self.price_points = self.create_price_points(start_price, self.max_expected_depreciation_rate, self.growth_step_size)

        # initialize first step
        self.first_sim_step()

    ############################################
    # retrieving attribute info
    ############################################


    def get_historical(self):
        return self.historical_data

    def get_num_price_points(self):
        return len(self.price_points)

    def get_current_total_profit(self):
        return np.sum(self.historical_data["step_profit"])

    def get_current_total_transactions(self):
        return np.sum(self.historical_data["step_transactions"])

    def get_max_positions_held(self):
        return np.max(self.historical_data["num_positions"])

    def get_min_capital_available(self):
        return np.min(self.historical_data["capital_available"])

    def get_sim_info(self):
		# create series of sim information:
        sim_info = pd.Series()
		# starting parameters
        sim_info["start"] = self.historical_data.iloc[0,0]
        sim_info["capital"] = self.initial_capital
        sim_info["depreciation_accounted_for"] = self.max_expected_depreciation_rate
        sim_info["appreciation_step_size"] = self.growth_step_size
        sim_info["num_price_points"] = self.get_num_price_points()

        return sim_info
    
    def get_results_info(self):
		# create series of sim information:
        results_info = pd.Series()

        results_info["profit_made"] = self.get_current_total_profit()
        results_info["total_transactions"] = self.get_current_total_transactions()
        results_info["max_positions"] = self.get_max_positions_held()
        results_info["min_capital_available"] = self.get_min_capital_available()	

        return results_info

    def get_full_info(self):
        return self.get_sim_info().append(self.get_results_info())

    #############################################
    # buying, selling and rollover
    #############################################


    def buy_position(self, price_point_index, current_price):
		# make sure we're not buying a position that exists already		
        assert price_point_index not in self.positions        

        available_per_point = self.capital / (price_point_index + 1)
        shares_to_buy = np.floor(available_per_point / current_price) 

        self.positions[price_point_index] = (current_price, shares_to_buy) # price_point_index: [(price_bought, num_shares_bought)*]
        self.capital -= current_price * shares_to_buy
        self.num_positions += 1
        # debugging
        #print("Bought {}".format(price_point_index))

    def sell_position(self, price_point_index, current_price):
        bought_price, shares_bought = self.positions.pop(price_point_index)
        profit = (current_price - bought_price) * shares_bought
        self.num_positions -= 1
        self.capital += current_price * shares_bought
        # debugging
        #print("Sold {}".format(price_point_index))
        #print("Sold {}, bought at {}, for profit of {:.2f}".format(price_point_index, bought_price, profit))

        return profit

    def rollover_position(self, from_price_point_index, to_price_point_index):
		# make sure we're not buying a position that exists already		
        assert to_price_point_index not in self.positions        

        self.positions[to_price_point_index] = self.positions.pop(from_price_point_index)
        # debugging
        #print("Rolled over {} to {}".format(from_price_point_index, to_price_point_index))
    
    ###############################################
    # historical information
    ###############################################

    def update_historical(self, step_profit_made, step_transactions_made):
        self.historical_data.iloc[self.historical_index, 2:] = [self.capital, self.num_positions, round(step_profit_made,2), step_transactions_made]
        #print("{} (record updated) {}".format(self.historical_index, list(self.historical_data.iloc[self.historical_index])))

    ###############################################
    # price point management
    ###############################################

    # create list of price buy/sell points
    def create_price_points(self, start_price, max_expected_depreciation_rate, growth_step_size):
        lowest_expected_price = start_price * (1 - max_expected_depreciation_rate)
        print("Creating price points, from {} until {}...\n".format(\
            round(lowest_expected_price,2), start_price + .01))

        price_points = []
        
        new_point = round(start_price, 2) + .01 # second to highest price point (current price)
        growth_step_ratio = 1 + growth_step_size
        lower_step_ratio = 1 / growth_step_ratio
        while new_point > lowest_expected_price:
            price_points.insert(0, new_point)
            new_point = round(new_point * lower_step_ratio, 2)
        price_points.append(round(price_points[-1] * growth_step_ratio,2)) # highest price point
        
        # convert to np.array
        price_points = np.array(price_points)

        print("Price points created are: \n{}\n".format(price_points))
        
        return price_points


    ###############################################
    # actual simulation steps
    ###############################################

    def run_sim(self, log_full_history=False):
        print("Running simulation steps...\n")
        sim_not_finished = self.sim_step(log_full_history)
        while sim_not_finished:
            sim_not_finished = self.sim_step(log_full_history)
        print("\n Simulation has ended\n")

    def first_sim_step(self):
        # initialize first position
        initial_index = len(self.price_points) - 2
        initial_price = self.historical_data.iloc[self.historical_index, 1]
        self.buy_position(initial_index, initial_price)
        self.current_position_index = initial_index
        # initialize historical information
        self.update_historical(0.0, 1)
        # move historical_index
        self.historical_index += 1

    def sim_step(self, log_full_history=False):
        if self.historical_index % 10000 == 0:
            print("Reached simulation step #{}".format(self.historical_index))
        # debugging
        #debugging_index = self.historical_index
        
        new_date = self.historical_data.iloc[self.historical_index, 0]
        new_price = self.historical_data.iloc[self.historical_index, 1]

        # some notes
        # for rollover, it needs to reach higher
        # for buying at lower, it just needs to reach exact
        step_position = self.price_points.searchsorted(new_price)

        if step_position == len(self.price_points): # means it's above last index
            print("\nEnding sim at date: {} and price: {}".format(new_date, new_price))
            return(False)
           
        profit_made = 0.0
        transactions_made = 0

        # do selling / buying / rollover
        if step_position in [self.current_position_index, self.current_position_index + 1]: # nothing happened, just move on
            pass
        
        elif step_position < self.current_position_index:
            new_position = step_position

			# debugging			
            #print("{}: {} -> {}".format(debugging_index, self.current_position_index, new_position))
            #print("positions: {}".format(sorted(self.positions)))

            self.buy_position(new_position, new_price)
            self.current_position_index = new_position
            transactions_made += 1

        elif step_position > self.current_position_index + 1: 
            new_position = step_position - 1

			# debugging			
            #print("{}: {} -> {}".format(debugging_index, self.current_position_index, new_position))
            #print("positions: {}".format(sorted(self.positions)))

            # get all lower positions
            lower_positions = sorted([key for key in self.positions if key < new_position])
            #print("lower_positions: {}".format(lower_positions))

            # sell all lower ones
            for position in lower_positions[:-1]:
                profit_made += self.sell_position(position, new_price)
                transactions_made += 1

            # either rollover or sell highest one
            if new_position in self.positions:
                profit_made += self.sell_position(lower_positions[-1], new_price)
                transactions_made += 1
            else:
                self.rollover_position(lower_positions[-1], new_position)

            # update current index
            self.current_position_index = new_position
            #print("{} (end of sales): profit made was: {:.2f}".format(debugging_index, profit_made))


        # save historical data 
        if transactions_made != 0 or log_full_history:
            self.update_historical(profit_made, transactions_made)

        # debugging
        assert self.num_positions == len(self.positions.keys()), \
            "Problem at index {}: num_positions is {} and actual keys are {}".format(self.historical_index, self.num_positions, len(self.positions.keys()))

		# move historical_index
        self.historical_index += 1

        return(True)

    def last_sim_step(self, close_price):
        profit_made = 0.0
        transactions_made = 0
        
        for position_index in list(self.positions.keys()):
            profit_made += self.sell_position(position_index, close_price)
            transactions_made += 1

        self.update_historical(profit_made, transactions_made)

