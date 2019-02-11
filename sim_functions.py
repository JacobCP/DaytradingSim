import numpy as np

class Holdings:

    def __init__(self, initial_capital, start_price, lowest_expected_price, growth_step_size):
        # store what we'll need later
        self.capital = initial_capital
        self.lowest_expected_price = lowest_expected_price
        # other attributes
        self.positions = {}
        self.price_points = None
        self.num_points = None
        self.shares_to_buy = None
        self.current_index = None
        # historical attributes
        self.hist_capital_available = []
        self.hist_num_positions = []
        self.hist_profit_made = []

        # create list of price buy/sell points
        price_points = []
        new_point = round(lowest_expected_price,2) # lowest point
        while new_point < start_price:
            price_points.append(new_point) # other points
            new_point = round(new_point * growth_step_size, 2)
        price_points.append(round(start_price,2) + .01) # starting price_point (we're selling once we get to a new high)
        # convert to np.array
        price_points = np.array(price_points)
        # store in Class object
        self.price_points = price_points

        # set amount to buy of each (only whole shares)
        num_points = len(price_points)
        available_per_point = self.capital / num_points
        shares_to_buy = np.floor(available_per_point / price_points)
        # store in Class object
        self.shares_to_buy = shares_to_buy

        # initialize first position
        self.buy_position(num_points - 1, price_points[-1])
 
    def buy_position(self, price_point_index, current_price):
        shares_to_buy = self.shares_to_buy[price_point_index]
        self.positions[price_point_index] = [(current_price, shares_to_buy)] # price_point_index: [(price_bought, num_shares_bought)*]
        self.capital -= current_price * shares_to_buy

    def sim_step(self, new_price):
        # some notes
        # for rollover, it needs to reach higher
        # for buying at lower, it just needs to reach exact
        new_position = self.price_points.searchsorted(new_price)
        if new_position in [self.current_index, self.current_index + 1]: # nothing happened, just move on
            pass
        elif new_position < self.current_index:
            pass
            # time to buy a new position
        else: 
            pass
            # time to sell/rollover positions
