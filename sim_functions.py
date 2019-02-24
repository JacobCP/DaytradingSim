import numpy as np
import pandas as pd
import sys

class Holdings:

    def __init__(self, historical_prices, sim_start_date, initial_capital, growth_step_size, max_expected_depreciation_rate, min_months_duration=12, all_time_high=None):
        # get col_names to use for readable code
        date_time_col = historical_prices.columns[0]
        price_col = historical_prices.columns[1]

        # get the index of the simulation start date - to find the previous high, and afterwards drop previous records
        date_values = historical_prices[date_time_col]
        start_date_index = np.where(date_values == sim_start_date)[0][0]
 
        # before filtering, get the previous high
        def get_previous_high(historical_prices, before_date_index):
            return np.max(historical_prices[price_col][:before_date_index+1])

        if all_time_high is not None:
            self.all_time_high = all_time_high
        else:
            self.all_time_high = get_previous_high(historical_prices, start_date_index)
        historical_prices = historical_prices.iloc[start_date_index:,:].copy()

        # store arguments
        self.historical_data = historical_prices
        self.min_months_duration = min_months_duration
        self.min_end_date = pd.Timestamp(sim_start_date) + np.timedelta64(min_months_duration, "M")
        self.initial_capital = initial_capital
        self.growth_step_size = growth_step_size		
        self.max_expected_depreciation_rate = max_expected_depreciation_rate

        # point in time attributes
        self.capital = initial_capital
        self.positions = {}
        self.current_position_index = None
        self.num_positions = 0
        self.price_points = None
        self.highest_buying_price = 0

        # historical logging attributes
        self.historical_index = 0
        for column_name in ["capital_available", "num_positions", "step_profit", "step_transactions"]:
            self.historical_data[column_name] = np.nan

        self.price_points = self.create_price_points(self.all_time_high, self.max_expected_depreciation_rate, self.growth_step_size)

        
        # report on basic simulation info
        self.report_on_start()

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

    def get_current_step_date(self):
        return self.historical_data.iloc[self.historical_index, 0]
        
    def get_current_step_price(self):
        return self.historical_data.iloc[self.historical_index, 1]

    def is_past_min_end_date(self):
        return self.get_current_step_date() >= self.min_end_date

    def report_on_start(self):
        print("Starting simulation at {} for a minimum duration of {} years and {} months.".format(self.get_current_step_date(), int(self.min_months_duration / 12), self.min_months_duration % 12))
        print("We have a virtual ${:,} in capital.".format(self.initial_capital))
        print("The stock price is currently ${}, with the all-time high before this date calculated at ${}".format(self.get_current_step_price(), self.all_time_high))
        print("We're accounting for a possible depreciation of {:.0%} from the all-time high".format(self.max_expected_depreciation_rate))
        print("Each position will be sold after appreciating {:.1%}\n".format(self.growth_step_size))

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

        if current_price > self.highest_buying_price:
            self.highest_buying_price = current_price

        # debugging
        # print("Bought {}".format(price_point_index))

    def sell_position(self, price_point_index, current_price):
        bought_price, shares_bought = self.positions.pop(price_point_index)
        profit = (current_price - bought_price) * shares_bought
        self.num_positions -= 1
        self.capital += current_price * shares_bought
        # debugging
        # print("Sold {}".format(price_point_index))
        #print("Sold {}, bought at {}, for profit of {:.2f}".format(price_point_index, bought_price, profit))

        return profit

    def rollover_position(self, from_price_point_index, to_price_point_index):
		# make sure we're not buying a position that exists already		
        assert to_price_point_index not in self.positions        

        self.positions[to_price_point_index] = self.positions.pop(from_price_point_index)
        # debugging
        # print("Rolled over {} to {}".format(from_price_point_index, to_price_point_index))
    
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
    def create_price_points(self, all_time_high, max_expected_depreciation_rate, growth_step_size):
        lowest_expected_price = all_time_high * (1 - max_expected_depreciation_rate)

        price_points = []
        
        new_point = round(all_time_high, 2) + .01 # second to highest price point (current price)
        growth_step_ratio = 1 + growth_step_size
        lower_step_ratio = 1 / growth_step_ratio
        while new_point > lowest_expected_price:
            price_points.insert(0, new_point)
            new_point = round(new_point * lower_step_ratio, 2)
        price_points.append(round(price_points[-1] * growth_step_ratio,2)) # highest price point
        
        # convert to np.array
        price_points = np.array(price_points)

        
        return price_points

    def shift_price_points(self):
        step_price = self.get_current_step_price()
        price_points = list(self.price_points)
        growth_step_ratio = 1 + self.growth_step_size

        shift_counter = 0
        
        # create new price points
        while step_price > price_points[-1]:
            new_point = round(price_points[-1] * (growth_step_ratio), 2)
            price_points.append(new_point)
            shift_counter += 1

        # delete corresponding lower price_points
        del price_points[:shift_counter]

        # shift all positions
        for position in sorted(list(self.positions)):
            self.positions[position - shift_counter] = self.positions.pop(position)

        return np.array(price_points)

    ###############################################
    # actual simulation steps
    ###############################################

    def run_sim(self, log_full_history=False):
        print("Running simulation...\n\nReached step:")

        # initialize first step
        self.first_sim_step()

        while True:
            # if step_price_point_index == len(self.price_points): # means it's above last index
            if self.get_current_step_price() > self.highest_buying_price and self.is_past_min_end_date():
                break
            self.sim_step(log_full_history)
        
        # for when the loop ends
        self.last_sim_step()
        
        print("\n Simulation has ended\n")

    def first_sim_step(self):
        # initialize first position
        initial_price = self.historical_data.iloc[0, 1]
        initial_position_index = self.price_points.searchsorted(initial_price)
        self.buy_position(initial_position_index, initial_price)
        self.current_position_index = initial_position_index
        
        # initialize historical information
        self.update_historical(0.0, 1)
        # move historical_index
        self.historical_index += 1

    def sim_step(self, log_full_history=False):
        # logging
        if self.historical_index % 10000 == 0:
            print("#{:,} | ".format(self.historical_index), end="")
            sys.stdout.flush()
        
        # debugging
        # debugging_index = self.historical_index
        
        step_price = self.get_current_step_price()

        step_price_point_index = self.price_points.searchsorted(step_price)
           
        profit_made = 0.0
        transactions_made = 0

        # do selling / buying / rollover
        if step_price_point_index in [self.current_position_index, self.current_position_index + 1]: # nothing happened, just move on
            pass
        
        elif step_price_point_index < self.current_position_index: # lower, need to buy new
            new_position_price_point_index = step_price_point_index

			# debugging			
            # print("{}: {} -> {}".format(debugging_index, self.current_position_index, new_position_price_point_index))
            # print("positions: {}".format(sorted(self.positions)))

            self.buy_position(new_position_price_point_index, step_price)
            self.current_position_index = new_position_price_point_index
            transactions_made += 1

        elif step_price_point_index > self.current_position_index + 1: # higher, need to sell/rollover

            # if we've passed the max price_point, we need to do a shift 
            if step_price_point_index == len(self.price_points): # it's past the highest index
                # debugging
                # print("Shifting point, at date: {} and price {}, the step_pp_index was {}".format(step_date, step_price, step_price_point_index))
                # print("Old price_points were: {}".format(self.price_points))
                # print("Old positions were: {}".format(self.positions))
                self.price_points = self.shift_price_points()
                # print("New price_points were: {}".format(self.price_points))
                # print("New positions are: {}".format(self.positions))
                # step_price_point_index -= 1 # after shifting, it's now the highest index

            new_position_price_point_index = step_price_point_index - 1

			# debugging			
            # print("{}: {} -> {}".format(debugging_index, self.current_position_index, new_position_price_point_index))
            # print("positions: {}".format(sorted(self.positions)))

            # get all lower positions
            lower_positions = sorted([key for key in self.positions if key < new_position_price_point_index])
            #print("lower_positions: {}".format(lower_positions))

            # sell all lower ones
            for position in lower_positions[:-1]:
                profit_made += self.sell_position(position, step_price)
                transactions_made += 1

            # either rollover or sell highest one
            if new_position_price_point_index in self.positions:
                profit_made += self.sell_position(lower_positions[-1], step_price)
                transactions_made += 1
            else:
                self.rollover_position(lower_positions[-1], new_position_price_point_index)

            # update current index
            self.current_position_index = new_position_price_point_index
            #print("{} (end of sales): profit made was: {:.2f}".format(debugging_index, profit_made))


        # save historical data 
        if transactions_made != 0 or log_full_history:
            self.update_historical(profit_made, transactions_made)

        # debugging
        assert self.num_positions == len(self.positions.keys()), \
            "Problem at index {}: num_positions is {} and actual keys are {}".format(self.historical_index, self.num_positions, len(self.positions.keys()))

		# move historical_index
        self.historical_index += 1

    def last_sim_step(self):
        print("\n\nEnding sim at date: {} and price: {}".format(self.get_current_step_date(), self.get_current_step_price()))
        profit_made = 0.0
        transactions_made = 0
        
        for position_index in list(self.positions.keys()):
            profit_made += self.sell_position(position_index, self.get_current_step_price())
            transactions_made += 1

        self.update_historical(profit_made, transactions_made)
        self.historical_index += 1

        self.historical_data = self.historical_data.iloc[:self.historical_index]
        

