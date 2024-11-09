import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf

class EnergyLSTM:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.scaler = MinMaxScaler()
        self.sequence_length = config['sequence_length']
        
    def create_sequences(self, data):
        """Create sequences for LSTM model"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def preprocess_data(self, df):
        """Preprocess data for LSTM model"""
        # Scale the features
        scaled_data = self.scaler.fit_transform(df)
        
        # Create sequences
        X, y = self.create_sequences(scaled_data)
        
        # Split into training and validation sets
        train_size = int(len(X) * 0.8)
        X_train, X_val = X[:train_size], X[train_size:]
        y_train, y_val = y[:train_size], y[train_size:]
        
        return X_train, X_val, y_train, y_val
    
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        self.model = Sequential([
            LSTM(self.config['lstm_units'], return_sequences=True, input_shape=input_shape),
            Dropout(self.config['dropout_rate']),
            LSTM(self.config['lstm_units'] // 2, return_sequences=True),
            Dropout(self.config['dropout_rate']),
            LSTM(self.config['lstm_units'] // 4),
            Dense(input_shape[-1])  # Output dimension matches input features
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
    def train(self, X_train, y_train, X_val, y_val):
        """Train the LSTM model"""
        if self.model is None:
            self.build_model(X_train.shape[1:])
            
        # Early stopping callback
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        history = self.model.fit(
            X_train, y_train,
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            validation_data=(X_val, y_val),
            callbacks=[early_stopping],
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """Make predictions using the trained model"""
        if self.model is None:
            raise ValueError("Model needs to be trained before making predictions")
        
        predictions = self.model.predict(X)
        # Inverse transform predictions
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        predictions = self.predict(X_test)
        y_test = self.scaler.inverse_transform(y_test)
        
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse
        }

    def forecast_next_24h(self, last_sequence):
        """Forecast next 24 hours of consumption"""
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(24):  # Predict next 24 hours
            # Reshape sequence for prediction
            sequence = current_sequence.reshape(1, self.sequence_length, -1)
            # Get prediction
            pred = self.model.predict(sequence)[0]
            # Add prediction to list
            predictions.append(pred)
            # Update sequence
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1] = pred
            
        return self.scaler.inverse_transform(np.array(predictions))