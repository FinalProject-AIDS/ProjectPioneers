import pandas as pd
import numpy as np
from scipy.optimize import minimize

def estimate_appliance_usage(total_kwh, appliances, constraints=None):
    """
    Estimate the usage of each appliance based on the total kWh consumed.
    
    :param total_kwh: Total electricity consumed in the month (in kWh)
    :param appliances: Dictionary of appliances with their wattages
    :param constraints: Dictionary of known constraints (e.g., {'Fan': {'min': 4, 'max': 12}})
    :return: DataFrame with estimated hours of usage and kWh consumed for each appliance
    """
    def objective(x):
        return np.sum((x - np.mean(x))**2)  # Try to distribute usage evenly

    def constraint(x):
        return total_kwh - np.sum(np.array(list(appliances.values())) * x / 1000)

    x0 = [8] * len(appliances)  # Initial guess: 8 hours per day for each appliance
    bounds = [(0, 24*30)] * len(appliances)  # Between 0 and 24*30 hours per month

    if constraints:
        for i, appliance in enumerate(appliances.keys()):
            if appliance in constraints:
                bounds[i] = (constraints[appliance]['min']*30, constraints[appliance]['max']*30)

    res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints={'type': 'eq', 'fun': constraint})

    hours = res.x
    kwh = np.array(list(appliances.values())) * hours / 1000

    df = pd.DataFrame({
        'Appliance': list(appliances.keys()),
        'Wattage': list(appliances.values()),
        'Estimated Hours': hours,
        'Estimated kWh': kwh
    })
    
    df['Percentage of Bill'] = df['Estimated kWh'] / total_kwh * 100
    return df.sort_values('Estimated kWh', ascending=False)

# Example usage
total_kwh = 300  # Total kWh consumed in a month
appliances = {
    'Refrigerator': 150,
    'Air Conditioner': 1500,
    'Television': 100,
    'Washing Machine': 500,
    'Fan': 75,
    'LED Bulb': 9,
    'Microwave': 1000,
    'Water Heater': 2000
}

constraints = {
    'Refrigerator': {'min': 24, 'max': 24},  # Runs 24 hours a day
    'Fan': {'min': 6, 'max': 12},  # Runs between 6 and 12 hours a day
    'LED Bulb': {'min': 4, 'max': 8}  # Used between 4 and 8 hours a day
}

result = estimate_appliance_usage(total_kwh, appliances, constraints)
print(result.to_string(index=False))