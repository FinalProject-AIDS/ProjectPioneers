import os
from pathlib import Path
import yaml
import streamlit_authenticator as stauth

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data directory
DATA_DIR = os.path.join(BASE_DIR, 'data', 'energy_data')

# Model configurations
MODEL_CONFIG = {
    'lstm_units': 50,
    'dropout_rate': 0.2,
    'epochs': 50,
    'batch_size': 32,
    'sequence_length': 24  # 24 hours of data for sequence
}

# User credentials configuration
USER_CREDENTIALS = {
    'usernames': {
        'admin': {
            'email': 'wesleyjaya2003@gmail.com',
            'name': 'wesley sam',
            'password': '12345',  # This will be hashed
            'role': 'admin'
        }
        # Add more users here as needed
    }
}

# Authentication configuration
AUTH_CONFIG = {
    'credentials': USER_CREDENTIALS,
    'cookie': {
        'name': 'energy_management_token',
        'key': 'energy_management_key',
        'expiry_days': 30
    },
    'preauthorized': ['wesleyjaya2003@gmail.com']
}

# Application settings
APP_CONFIG = {
    'page_title': 'Energy Management System',
    'page_icon': '⚡',
    'layout': 'wide'
}

# Feature configurations
FEATURE_COLUMNS = [
    'temperature',
    'occupancy_level',
    'total_fan_consumption',
    'total_light_consumption',
    'computer_consumption',
    'projector_consumption'
]

# Visualization settings
VIZ_CONFIG = {
    'theme': 'streamlit',
    'colors': {
        'primary': '#FF4B4B',
        'secondary': '#0068C9',
        'background': '#FFFFFF',
        'text': '#262730'
    }
}

def generate_auth_config():
    """Generate authentication configuration with hashed passwords"""
    # Get all passwords
    passwords = [USER_CREDENTIALS['usernames'][username]['password'] 
                for username in USER_CREDENTIALS['usernames']]
    
    # Hash all passwords
    hashed_passwords = stauth.Hasher(passwords).generate()
    
    # Update passwords in config
    for (username, hashed_pw) in zip(USER_CREDENTIALS['usernames'], hashed_passwords):
        AUTH_CONFIG['credentials']['usernames'][username]['password'] = hashed_pw
    
    # Save to yaml file
    config_path = os.path.join(BASE_DIR, 'config.yaml')
    with open(config_path, 'w') as file:
        yaml.dump(AUTH_CONFIG, file, default_flow_style=False)

# Generate authentication config file if running this script directly
if __name__ == "__main__":
    generate_auth_config()