# model/data.py
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal

class DataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()

    def fit(self, X):
        self.scaler.fit(X)

    def transform(self, X):
        return self.scaler.transform(X)

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

    def generate_turbine_data(self, num_samples, cut_in, rated_speed, rated_power, cut_out, shape, scale, random_state=None):
        num_samples = int(num_samples)  # Ensure num_samples is an integer

        if random_state is not None:
            np.random.seed(random_state)
            
        # Generate random wind speeds from a Weibull distribution
        wind_speeds = np.random.weibull(shape, num_samples) * scale
        mean = [0, 15]
        covariance = [[1, 0], [0, 10]]
        wind_directions, temperatures = multivariate_normal(mean, covariance).rvs(num_samples).T

        # Initialize power outputs
        power_outputs = np.zeros(num_samples)
        
        # Compute power output for each wind speed
        for i, speed in enumerate(wind_speeds):
            if speed < cut_in or speed > cut_out:
                power = 0
            elif speed < rated_speed:
                power = rated_power * ((speed - cut_in) / (rated_speed - cut_in)) ** 3
            else:
                power = rated_power
                
            power_outputs[i] = power + np.random.normal(0, power * 0.05) 
        
        return np.stack((wind_speeds, wind_directions, temperatures), axis=-1), power_outputs

    def save_data(self, X, y, filepath):
        # Convert X and y to DataFrames
        df_X = pd.DataFrame(X, columns=['wind_speed', 'wind_direction', 'temperature'])
        df_y = pd.DataFrame(y, columns=['power_output'])
        
        # Concatenate the DataFrames along the columns
        df = pd.concat([df_X, df_y], axis=1)
        
        # Save the DataFrame to .csv
        df.to_csv(filepath, index=False)

    def generate_and_save_data(self, num_samples, cut_in, rated_speed, rated_power, cut_out, shape, scale, filepath, random_state=None):
        X, y = self.generate_turbine_data(num_samples, cut_in, rated_speed, rated_power, cut_out, shape, scale, random_state)
        self.save_data(X, y, filepath)