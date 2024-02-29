from monte_carlo_pricer import MonteCarloPricer, Option, PayoffType
from black_scholer_pricer import BlackScholesPricer
from scipy import optimize


class TaskRunner:  

    def __init__(self, df, cfg):  

        self.df = df
        self.cfg = cfg
        

    def get_implied_volatility(self, quantity, spot_price, expiry, payment_time, strike, call_put, type, price):
        """
        Given a price of a quantity of options and some other data, the implied volatility is calculated

        The mathematical idea is to define a function taking volatility as input and returning difference to the actual price. Given this we use the 
        Newton-Rapson method for numerically compute the implied volatility
        """

        black_scholes_func = lambda vol : BlackScholesPricer(quantity , spot_price, vol, expiry, payment_time, strike, call_put, type, self.cfg['Modelling']).pv - price
        
        vol = optimize.newton(black_scholes_func, 0.2)
        
        return vol

    def do_task_2(self):
        """
        A method to demonstrate the get_implied_volatility function
        """

        print("An example of how to use the get_implied_volatility function with the following input: \n")
        quantity = 1
        spot_price = 100
        volatility = 0.5
        expiry = 5 * 252
        payment_time = 5 * 252
        strike = 90
        call_put = Option.CALL
        type = PayoffType.regular
        price = 49.46603

        for var_name, var_value in locals().items():
            print(f"{var_name} = {var_value}")

        print("\n")
        implied_volatility = self.get_implied_volatility(quantity, spot_price, expiry, payment_time, strike, call_put, type, price)

        print("Volatility is " + str(round(volatility, 4)) + " , implied volatility calculated to be " + str(round(implied_volatility, 4)))
        print("The difference is " + str(round(implied_volatility - volatility, 4)))

    
    def do_task_1(self):
        """
        We price a number of trades, using Black Scholes for regular options and a Monte Carlo implementation for odd options
        """
        decimals = self.cfg['Modelling']['output_decimals']
        n = self.df.shape[0]
        output = list(range(n))

        trade_ids, quantities, underlyings, expiries, payment_times, strikes, call_puts, types, spot_prices, volatilities = self.df.T.to_numpy() 

        for i in range(n):
            if types[i] == PayoffType.odd:
                mcp = MonteCarloPricer(quantities[i], spot_prices[i], volatilities[i], expiries[i], payment_times[i], strikes[i], call_puts[i], types[i], self.cfg['Modelling'])
                output[i] = [trade_ids[i], round(mcp.pv, decimals), round(mcp.delta, decimals), round(mcp.vega, decimals)]
            else:
                bsp = BlackScholesPricer(quantities[i], spot_prices[i], volatilities[i], expiries[i], payment_times[i], strikes[i], call_puts[i], types[i], self.cfg['Modelling'])
                output[i] = [trade_ids[i], round(bsp.pv, decimals), round(bsp.delta, decimals), round(bsp.vega, decimals)]

        return output


