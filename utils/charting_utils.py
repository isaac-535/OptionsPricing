import pandas as pd
import numpy as np
from utils.BS_utils import black_scholes_greek_and_value_calculator

def generate_data_for_independent_variable(
        unchanged_values: dict, # Dictionary for S, K, r, sigma, t with initial values (include that of the independent variable)
        independent_variable: str, # str for the variable we want to vary
        independent_variable_range: list[float, float], # List with two elements [start, stop] for the independent variable
        option_type: str = 'call', # 'call' or 'put'
        dependent_variable: str = 'value', # The greek/value we want to plot as the dependent variable
        n: int = 100 # Number of points we want in the graph
):
    start, stop = independent_variable_range
    x = np.linspace(start, stop, n).tolist()
    plotting_dict = {}
    for parameter in unchanged_values.keys():
        if parameter == independent_variable:
            plotting_dict[parameter] = x
        else:
            plotting_dict[parameter] = [unchanged_values[parameter]]*n
    S, K, r, sigma, t = plotting_dict['S'], plotting_dict['K'], plotting_dict['r'], plotting_dict['sigma'], plotting_dict['t']
    y = [black_scholes_greek_and_value_calculator(S=S[i], K=K[i], r=r[i], sigma=sigma[i], t=t[i], option_type=option_type, greek = dependent_variable) for i in range(n)]
    df = pd.DataFrame({'x': x, 'y': y})
    return df