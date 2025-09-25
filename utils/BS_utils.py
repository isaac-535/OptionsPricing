import pandas as pd
import numpy as np
import math
from scipy.stats import norm

class Option:
    def __init__(self, S, K, r, sigma, t, option_type):
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be either 'call' or 'put'")
        self.S = S # Current stock price
        self.K = K # Strike
        self.r = r # Interest rate
        self.sigma = sigma # Volatility
        self.t = t # Time to expiry
        self.option_type = option_type # str type: 'call' or 'put'
        self.sqrt_t = np.sqrt(t) # Defining square root of time for use in functions
        self.discount = math.exp(-self.r*self.t) # e^-rt term
        self.d1 = (np.log(S/K) + (r + sigma**2/2)*t)/(sigma*self.sqrt_t) # d1 term
        self.d2 = self.d1 - sigma*self.sqrt_t # d2 term
        self.N_d1 = norm.cdf(self.d1) # Normal cdf of d1
        self.N_d2 = norm.cdf(self.d2) # Normal cdf of d2
        self.phi_d1 = norm.pdf(self.d1) # Normal pdf of d1

    def value(self):
        call_value = self.N_d1*self.S - self.N_d2*self.K*self.discount
        if self.option_type == 'call':
            return call_value
        elif self.option_type == 'put':
            return call_value - (self.S - self.K*self.discount)
    
    def delta(self):
        if self.option_type == 'call':
            return self.N_d1
        elif self.option_type == 'put':
            return self.N_d1 - 1
    
    def gamma(self):
        return self.phi_d1/(self.S*self.sigma*self.sqrt_t)
    
    def vega(self):
        return self.S*self.phi_d1*self.sqrt_t
    
    def theta(self):
        if self.option_type == 'call':
            return -(self.S*self.phi_d1*self.sigma)/(2*self.sqrt_t) - self.r*self.K*self.discount*self.N_d2
        elif self.option_type == 'put':
            return -(self.S*self.phi_d1*self.sigma)/(2*self.sqrt_t) + self.r*self.K*self.discount*(1 - self.N_d2)
        
    def rho(self):
        if self.option_type == 'call':
            return self.K*self.t*self.discount.self.N_d2
        elif self.option_type == 'put':
            return -self.K*self.t*self.discount*(1 - self.N_d2)


def black_scholes_greek_and_value_calculator(
        S, # stock price
        K, # strike
        r, # interest rate
        sigma, # volatility
        t, # time to expiry
        option_type:str = 'call', # 'call' or 'put'
        greek:str = 'value' # 'value', 'delta', 'gamma', 'vega', 'theta' or 'rho'
):
    sqrt_t = np.sqrt(t) # Defining square root of time for use in functions
    discount = math.exp(-r*t) # e^-rt term
    d1 = (np.log(S/K) + (r + sigma**2/2)*t)/(sigma*sqrt_t) # d1 term
    d2 = d1 - sigma*sqrt_t # d2 term
    N_d1 = norm.cdf(d1) # Normal cdf of d1
    N_d2 = norm.cdf(d2) # Normal cdf of d2
    phi_d1 = norm.pdf(d1) # Normal pdf of d1

    if option_type not in ['call', 'put']:
        raise ValueError("option_type must be either 'call' or 'put'")

    if greek == 'value':
        call_price = N_d1*S - N_d2*K*discount
        if option_type == 'call':
            return call_price
        elif option_type == 'put':
            return call_price - (S - K*discount)

    if greek == 'delta':
        if option_type == 'call':
            return N_d1
        elif option_type == 'put':
            return N_d1 - 1
    
    if greek == 'gamma':
        return phi_d1/(S*sigma*sqrt_t)
    
    if greek == 'vega':
        return S*phi_d1*sqrt_t
    
    if greek == 'theta':
        if option_type == 'call':
            return -(S*phi_d1*sigma)/(2*sqrt_t) - r*K*discount*N_d2
        elif option_type == 'put':
            return -(S*phi_d1*sigma)/(2*sqrt_t) + r*K*discount*(1 - N_d2)
        
    if greek == 'rho':
        if option_type == 'call':
            return K*t*discount*N_d2
        elif option_type == 'put':
            return -K*t*discount*(1 - N_d2)

def implied_volatility(
        S, # stock price
        K, # strike
        r, # interest rate
        t, # time to expiry
        price, # market price of the option
        option_type:str = 'call', # 'call' or 'put'
):
    """
    Takes the stock price, strike, interest rate, time, option_type and price and returns the volatility
    required for the BS value of the option to be the market price (implied volatility)
    """
    x = 0.2 # TO CHANGE
    f_x = black_scholes_greek_and_value_calculator(S=S, K=K, r=r, sigma=x, t=t, option_type=option_type, greek='value')
    while abs(f_x - price) > 0.0005:
        f_prime_x = black_scholes_greek_and_value_calculator(S=S, K=K, r=r, sigma=x, t=t, option_type=option_type, greek='vega')
        x -= (f_x - price)/f_prime_x
        f_x = black_scholes_greek_and_value_calculator(S=S, K=K, r=r, sigma=x, t=t, option_type=option_type, greek='value')

    return x

