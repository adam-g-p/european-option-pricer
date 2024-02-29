from monte_carlo_pricer import MonteCarloPricer, Option, PayoffType
from black_scholer_pricer import BlackScholesPricer
from scipy import optimize


class TaskRunner:  
    """
    Given the relatively small number of assets, we could have prepared and store those instead of recalculating for every trade
    """
    def __init__(self, df, cfg):  

        self.df = df
        self.cfg = cfg
        

    def get_implied_volatility(self):
        quantity = 1
        spot_price = 100
        #volatility = 0.5
        expiry = 5 * 252
        payment_time = 5 * 252
        strike = 90
        call_put = Option.CALL
        type = PayoffType.regular
        price = 49.46603
       
        # Inleder med quantity = 1
        black_scholes_func = lambda vol : BlackScholesPricer(quantity , spot_price, vol, expiry, payment_time, strike, call_put, type, self.cfg['Modelling']).pv - price
        
        vol = optimize.newton(black_scholes_func, 0.2)
        print(vol)
    
    def do_task_1(self):
        decimals = 3
        n = self.df.shape[0]
        n = min(50,n)
        output = list(range(n))

        trade_ids, quantities, underlyings, expiries, payment_times, strikes, call_puts, types, spot_prices, volatilities = self.df.T.to_numpy() 
        mcp =  MonteCarloPricer(quantities[0], spot_prices[0], volatilities[0], expiries[0], payment_times[0], strikes[0], call_puts[0], types[0], self.cfg['Modelling'])

        for i in range(n):
            if types[i] == PayoffType.odd:
                mcp = MonteCarloPricer(quantities[i], spot_prices[i], volatilities[i], expiries[i], payment_times[i], strikes[i], call_puts[i], types[i], self.cfg['Modelling'])
                output[i] = [trade_ids[i], round(mcp.pv, decimals), round(mcp.delta, decimals), round(mcp.vega, decimals)]
            else:
                bsp = BlackScholesPricer(quantities[i], spot_prices[i], volatilities[i], expiries[i], payment_times[i], strikes[i], call_puts[i], types[i], self.cfg['Modelling'])
                output[i] = [trade_ids[i], round(bsp.pv, decimals), round(bsp.delta, decimals), round(bsp.vega, decimals)]

        return output


