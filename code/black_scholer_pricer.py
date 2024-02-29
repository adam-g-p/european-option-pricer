import numpy as np
from scipy.stats import norm
from monte_carlo_pricer import Option

class BlackScholesPricer:
    def __init__(self, 
                 quantity,
                 spot_price, 
                 implied_volatility,
                 days_to_expiry,
                 payment_time_days,
                 strike,
                 call_put,
                 payoff_type,
                 cfg_parameters
                 ):  
        "init"
        self.dt = 1/252.0
        self.quantity = quantity
        self.T = days_to_expiry  
        self.T_p = payment_time_days
        self.K = strike
        self.call_put = call_put
        self.S_0 = spot_price
        self.sigma = implied_volatility
        self.r = cfg_parameters['Financial']['drift_rate_eq']
        self.payoff_type = payoff_type

        self.pv = self.compute_black_scholes_price()
        self.vega = self.compute_vega()
        self.delta = self.compute_delta()

    def compute_black_scholes_price(self):
        """
        Konvertering från år till dagar i heltal och sedan tillbaka måste fixas
        """
        T = self.T * self.dt


        d1 = (np.log(self.S_0 / self.K) + (self.r + 0.5 * self.sigma ** 2) * T) / (self.sigma * np.sqrt(T))
        d2 = d1 - self.sigma * np.sqrt(T)

        if self.call_put == Option.CALL:
            option_price = (self.S_0 * norm.cdf(d1) - self.K * np.exp(-self.r * T) * norm.cdf(d2))
        elif self.call_put == Option.PUT:
            option_price = (self.K * np.exp(-self.r * T) * norm.cdf(-d2) - self.S_0 * norm.cdf(-d1))
    

        return option_price * self.quantity
    
    def compute_vega(self):
        """
        Konvertering från år till dagar i heltal och sedan tillbaka måste fixas
        """
        T = self.T * self.dt
        if self.sigma * np.sqrt(T) == 0:
            print(self.T)
        d1 = (np.log(self.S_0 / self.K) + (self.r + 0.5 * self.sigma ** 2) * T) / (self.sigma * np.sqrt(T))
        vega = 0.01 * self.S_0 * np.sqrt(T) * norm.pdf(d1)

        return vega * self.quantity

    def compute_delta(self):

        T = self.T * self.dt

        d1 = (np.log(self.S_0 / self.K) + (self.r + 0.5 * self.sigma ** 2) * T) / (self.sigma * np.sqrt(T))

        if self.call_put == Option.CALL:
            delta = norm.cdf(d1)
        elif self.call_put == Option.PUT:
            delta = norm.cdf(d1) - 1

        return delta * self.quantity