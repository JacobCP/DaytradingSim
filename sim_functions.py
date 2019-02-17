import numpy as np
import pandas as pd

class Holdings:

    def __init__(self, initial_capital, start_date_time, start_price, lowest_expected_price, growth_step_size, num_rows=0):

        # store what we'll need later
        self.capital = initial_capital
        self.lowest_expected_price = lowest_expected_price
        # other attributes
        self.price_points = None
        self.shares_to_buy = None
        # keep track as simulation moves along
        self.positions = {}
        self.current_index = None
        self.num_positions = 0
        # historical attributes
        self.historical_index = 0
        self.historical_data = pd.DataFrame(index=np.arange(num_rows), columns=["date_time", "capital_available", "num_positions", "step_profit", "step_transactions"])

        # create list of price buy/sell points
        print("starting to create price points, from {} until {}".format(round(lowest_expected_price,2), start_price))
        price_points = []
        new_point = round(lowest_expected_price,2) # lowest point
        growth_step_ratio = 1 + growth_step_size
        while new_point < start_price:
            price_points.append(new_point) # other points
            new_point = round(new_point * growth_step_ratio, 2)
        price_points.append(round(start_price,2) + .01) # starting price_point (we're selling once we get to a new high)
        # convert to np.array
        price_points = np.array(price_points)
        print("price points created")
        # store in Class object
        self.price_points = price_points

        # set amount to buy of each (only whole shares)
        num_points = len(price_points)
        available_per_point = self.capital / num_points
        shares_to_buy = np.floor(available_per_point / price_points)

        # store in Class object
        self.shares_to_buy = shares_to_buy

        # initialize first step
        self.first_sim_step(start_date_time)

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

    #############################################
    # buying, selling and rollover
    #############################################


    def buy_position(self, price_point_index, current_price):
		# make sure we're not buying a position that exists already		
        assert price_point_index not in self.positions        

        shares_to_buy = self.shares_to_buy[price_point_index]
        self.positions[price_point_index] = (current_price, shares_to_buy) # price_point_index: [(price_bought, num_shares_bought)*]
        self.capital -= current_price * shares_to_buy
        self.num_positions += 1
        # debugging
        print("Bought {}".format(price_point_index))

    def sell_position(self, price_point_index, current_price):
        bought_price, shares_bought = self.positions.pop(price_point_index)
        profit = (current_price - bought_price) * shares_bought
        self.num_positions -= 1
        self.capital += current_price * shares_bought
        # debugging
        print("Sold {}".format(price_point_index))

        return profit

    def rollover_position(self, from_price_point_index, to_price_point_index):
		# make sure we're not buying a position that exists already		
        assert to_price_point_index not in self.positions        

        self.positions[to_price_point_index] = self.positions.pop(from_price_point_index)
        # debugging
        print("Rolled over {} to {}".format(from_price_point_index, to_price_point_index))
    
    ###############################################
    # historical information
    ###############################################

    def update_historical(self, new_date_time, step_profit_made, step_transactions_made):
        self.historical_data.loc[self.historical_index] = [new_date_time, self.capital, self.num_positions, step_profit_made, step_transactions_made]
        self.historical_index += 1

    ###############################################
    # actual simulation steps
    ###############################################

    def first_sim_step(self, start_date_time):
        # initialize first position
        initial_index = len(self.price_points) - 1
        self.buy_position(initial_index, self.price_points[-1])
        self.current_index = initial_index
        # initialize historical information
        self.update_historical(start_date_time, 0.0, 1)

    def sim_step(self, new_price, new_date_time):
        # debugging
        debugging_index = self.historical_index + 1
        
        # some notes
        # for rollover, it needs to reach higher
        # for buying at lower, it just needs to reach exact
        step_position = self.price_points.searchsorted(new_price)

        profit_made = 0.0
        transactions_made = 0

        # do selling / buying / rollover
        if step_position in [self.current_index, self.current_index + 1]: # nothing happened, just move on
            pass
        
        elif step_position < self.current_index:
            new_position = step_position

			# debugging			
            print("{}: {} -> {}".format(debugging_index, self.current_index, new_position))
            print("positions: {}".format(sorted(self.positions)))

            self.buy_position(new_position, new_price)
            self.current_index = new_position
            transactions_made += 1

            #print("updated keys: " + str(list(self.positions.keys())))

        elif step_position > self.current_index + 1: 
            new_position = step_position - 1

			# debugging			
            print("{}: {} -> {}".format(debugging_index, self.current_index, new_position))
            print("positions: {}".format(sorted(self.positions)))

            # get all lower positions
            lower_positions = sorted([key for key in self.positions if key < new_position])
            print("lower_positions: {}".format(lower_positions))

            # sell all lower ones
            for position in lower_positions[:-1]:
                profit_made += self.sell_position(position, new_price)
                transactions_made += 1

            # either rollover or sell highest one
            if new_position in self.positions:
                profit_made += self.sell_position(lower_positions[-1], new_price)
            else:
                self.rollover_position(lower_positions[-1], new_position)

            # update current index
            self.current_index = new_position


        # save historical data
        self.update_historical(new_date_time, profit_made, transactions_made)

        # debugging
        assert self.num_positions == len(self.positions.keys()), \
            "Problem at index {}: num_positions is {} and actual keys are {}".format(self.historical_index, self.num_positions, len(self.positions.keys()))


    def last_sim_step(self, close_price, close_date_time):
        profit_made = 0.0
        transactions_made = 0
        
        for position_index in self.positions:
            profit_made += self.sell_position(position_index, close_price)
            transaction_made += 1

        self.update_historical(close_date_time, profit_made, transactions_made)

