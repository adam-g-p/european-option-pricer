from enum import Enum
import numpy as np
 
class Option(Enum):
    CALL = 'CALL'
    PUT = 'PUT'

class PayoffType(Enum):
    regular = 'REGULAR'
    odd = 'ODD'

class MonteCarloPricer:  
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
        self.spot_fx = cfg_parameters['Financial']['spot_rate_fx']
        self.sigma_fx = cfg_parameters['Financial']['volatility_fx']
        self.sigma_corr = cfg_parameters['Financial']['corr_eq_fx']
        self.drift_fx = cfg_parameters['Financial']['drift_rate_fx']

        self.sim_batches = 1
        self.n =  int(cfg_parameters['Simulation']['n_paths'] / self.sim_batches)

        self.Sigma = np.array([[1, self.sigma_corr], 
                               [self.sigma_corr , 1]])

        

        self.batch_aggregator()
        
        
       
    def batch_aggregator(self):
        base, delta, vega = 0, 0, 0

        if self.call_put == Option.CALL:
            
            for i in range(round(self.sim_batches)):
                self.gaussian_eq, self.gaussian_fx = self.generate_correlated_gaussians()

                base += self.get_call_payoffs("base")
                delta += self.get_call_payoffs("delta")
                vega += self.get_call_payoffs("vega")
        
        if self.call_put == Option.PUT:
            
            for i in range(round(self.sim_batches)):
                self.gaussian_eq, self.gaussian_fx = self.generate_correlated_gaussians()

                base += self.get_put_payoffs("base")
                delta += self.get_put_payoffs("delta")
                vega += self.get_put_payoffs("vega")
        
        base_price = base/self.sim_batches
        delta_price = delta/self.sim_batches
        vega_price = vega/self.sim_batches

        delta = (delta_price - base_price) / (0.01 * self.S_0)
        vega = vega_price - base_price

        self.pv = self.quantity * base_price
        self.delta = self.quantity * delta
        self.vega = self.quantity * vega

    def get_call_payoffs(self, mode):

        eq_paths = self.simulate_eq_prices(mode)
        fx_paths = self.simulate_fx_prices()

        # We discount from the time of payoff, as opposed to discounting from the time of expiry
        discount_factor = np.exp(-self.r * self.T_p * self.dt)
        
        payoff = np.maximum(eq_paths - self.K, 0)

        usd_payoff = payoff * fx_paths

        discounted_payoff = discount_factor * usd_payoff

        return np.mean(discounted_payoff)

    def get_put_payoffs(self, mode):

        eq_paths = self.simulate_eq_prices(mode)
        fx_paths = self.simulate_fx_prices()

        # We discount from the time of payoff, as opposed to discounting from the time of expiry
        discount_factor = np.exp(-self.r * self.T_p * self.dt)
        
        payoff = np.maximum(self.K - eq_paths, 0)

        usd_payoff = payoff * fx_paths

        discounted_payoff = discount_factor * usd_payoff

        return np.mean(discounted_payoff)


    def simulate_fx_prices(self):

        if self.payoff_type == PayoffType.regular:
            return np.ones((self.n))

        full_paths = self.simulate_asset_prices(self.spot_fx, self.drift_fx, self.sigma_fx, self.gaussian_fx, self.T_p)

        final_states = full_paths[:, -1]

        return final_states
    
    def simulate_eq_prices(self, mode):
        if mode == "base":
            full_paths = self.simulate_asset_prices(self.S_0, self.r, self.sigma, self.gaussian_eq, self.T)
        elif mode == "delta":
            full_paths = self.simulate_asset_prices(self.S_0 * 1.01, self.r, self.sigma, self.gaussian_eq, self.T)
        elif mode == "vega":
            full_paths = self.simulate_asset_prices(self.S_0, self.r, self.sigma + 0.01, self.gaussian_eq, self.T)

        final_states = full_paths[:, -1]

        return final_states

    def simulate_asset_prices(self, S_0, r, sigma, gaussian, T):
        dt = self.dt 
        sqrt_dt = np.sqrt(dt)  

        asset_prices = np.zeros((self.n, T + 1))
        asset_prices[:, 0] = S_0  
        
        for i in range(1, T + 1):
            drift = (r - 0.5 * sigma ** 2) * dt
            diffusion = sigma * sqrt_dt * gaussian[:, i - 1]
            asset_prices[:, i] = asset_prices[:, i - 1] * np.exp(drift + diffusion)

        return asset_prices


    def generate_correlated_gaussians(self):
            """
            Method to generate two correlated stochastic processes with mean zero and variance 1

            We simulate two independent arrays at first, transform with covariance matrix to get the desired correlation, then reshape according
            to time T of days to simulate and number n of paths
            """
            T = max(self.T, self.T_p)

            ind_gaussian_processes = np.random.normal(size=(T * self.n, 2))

            cholesky_decomposition = np.linalg.cholesky(self.Sigma)

            corr_gaussian_processes = ind_gaussian_processes @ cholesky_decomposition.T

            corr_gaussian_processes = corr_gaussian_processes.reshape(self.n, T, 2)

            equity_gaussian_process = corr_gaussian_processes[:, :, 0]  
            fx_gaussian_process = corr_gaussian_processes[:, :, 1]  

            return equity_gaussian_process, fx_gaussian_process
    























    def _simulate_asset_prices(self, S_0, r, sigma, gaussian, T):
        '''
        Vectorized version that seemingly worsens perfomance 
        '''
   
        dt = 1/252 # No of business days in a year
        sqrt_dt = np.sqrt(dt)  # Square root of time step

        # Initialize array to store simulated prices for each simulation
        asset_prices = np.zeros((self.n, T + 1))
        asset_prices[:, 0] = S_0  # Set initial asset price

        drift_rate = r

        drift = (drift_rate - 0.5 * sigma ** 2) * dt
        diffusion = sigma * sqrt_dt * gaussian[:, :T]


        asset_prices[:, 1:] = S_0 * np.cumprod(np.exp(drift + diffusion), axis=1)
     

        return asset_prices

