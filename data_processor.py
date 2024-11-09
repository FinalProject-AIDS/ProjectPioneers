import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        
    def load_and_preprocess(self):
        """Load and preprocess the energy consumption data"""
        # Load data
        self.df = pd.read_json(self.data_path)
        
        # Convert timestamp to datetime
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        # Extract temporal features
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day'] = self.df['timestamp'].dt.day
        self.df['month'] = self.df['timestamp'].dt.month
        self.df['day_of_week'] = self.df['timestamp'].dt.day_name()
        self.df['is_weekend'] = self.df['day_of_week'].isin(['Saturday', 'Sunday'])
        
        # Process floor data
        self._process_floor_data()
        
        # Process shared equipment data
        self._process_equipment_data()
        
        return self.df
    
    def _process_floor_data(self):
        """Process nested floor data"""
        # Extract total consumption for each type per floor
        for floor in range(1, 5):  # Assuming 4 floors
            floor_data = self.df['floor_data'].apply(
                lambda x: next((item for item in x if item['floor'] == floor), None)
            )
            
            self.df[f'floor_{floor}_fan'] = floor_data.apply(
                lambda x: x['fan_consumption'] if x else 0
            )
            self.df[f'floor_{floor}_light'] = floor_data.apply(
                lambda x: x['light_consumption'] if x else 0
            )
        
        # Calculate total consumption by type
        self.df['total_fan_consumption'] = sum(
            self.df[f'floor_{i}_fan'] for i in range(1, 5)
        )
        self.df['total_light_consumption'] = sum(
            self.df[f'floor_{i}_light'] for i in range(1, 5)
        )
    
    def _process_equipment_data(self):
        """Process shared equipment data"""
        self.df['computer_consumption'] = self.df['shared_equipment'].apply(
            lambda x: x['computer_consumption']
        )
        self.df['projector_consumption'] = self.df['shared_equipment'].apply(
            lambda x: x['projector_consumption']
        )
    
    def get_consumption_metrics(self):
        """Calculate key consumption metrics"""
        metrics = {
            'total_consumption': self.df['total_consumption'].sum(),
            'average_daily_consumption': self.df.groupby(
                self.df['timestamp'].dt.date
            )['total_consumption'].mean().mean(),
            'peak_consumption': self.df['total_consumption'].max(),
            'peak_time': self.df.loc[
                self.df['total_consumption'].idxmax(), 'timestamp'
            ],
            'average_occupancy': self.df['occupancy_level'].mean()
        }
        return metrics
    
    def get_hourly_patterns(self):
        """Analyze hourly consumption patterns"""
        return self.df.groupby('hour')['total_consumption'].mean()
    
    def get_equipment_usage(self):
        """Analyze equipment-wise consumption"""
        equipment_consumption = {
            'Fans': self.df['total_fan_consumption'].sum(),
            'Lights': self.df['total_light_consumption'].sum(),
            'Computers': self.df['computer_consumption'].sum(),
            'Projectors': self.df['projector_consumption'].sum()
        }
        return equipment_consumption
    
    def identify_anomalies(self, threshold=2):
        """Identify anomalous consumption patterns"""
        # Calculate Z-scores for total consumption
        self.df['consumption_zscore'] = np.abs(
            (self.df['total_consumption'] - self.df['total_consumption'].mean()) 
            / self.df['total_consumption'].std()
        )
        
        # Identify anomalies based on Z-score threshold
        anomalies = self.df[self.df['consumption_zscore'] > threshold]
        return anomalies
    
    def get_efficiency_score(self):
        """Calculate energy efficiency score"""
        # Calculate baseline metrics
        avg_consumption = self.df['total_consumption'].mean()
        occupancy_ratio = self.df['occupancy_level'].mean() / 100
        equipment_utilization = (
            self.df['computer_consumption'].mean() 
            + self.df['projector_consumption'].mean()
        ) / self.df['total_consumption'].mean()
        
        # Calculate efficiency score (0-100)
        efficiency_score = (
            (1 - (avg_consumption / self.df['total_consumption'].max())) * 40 +
            occupancy_ratio * 30 +
            (1 - equipment_utilization) * 30
        )
        
        return min(max(efficiency_score, 0), 100)  # Ensure score is between 0 and 100