import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class VisualizationHelper:
    def __init__(self, theme_colors):
        self.colors = theme_colors
        
    def create_consumption_timeline(self, df):
        """Create interactive timeline of energy consumption"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['total_consumption'],
            mode='lines',
            name='Total Consumption',
            line=dict(color=self.colors['primary'])
        ))
        
        fig.update_layout(
            title='Energy Consumption Timeline',
            xaxis_title='Time',
            yaxis_title='Consumption (Watt-hour)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_heatmap(self, df):
        """Create hourly consumption heatmap"""
        # Pivot data for heatmap
        heatmap_data = df.pivot_table(
            values='total_consumption',
            index=df['timestamp'].dt.day_name(),
            columns=df['timestamp'].dt.hour,
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Blues',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Hourly Consumption Patterns',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            template='plotly_white'
        )
        
        return fig
    
    def create_equipment_breakdown(self, equipment_data):
        """Create equipment consumption breakdown"""
        fig = go.Figure(data=[go.Pie(
            labels=list(equipment_data.keys()),
            values=list(equipment_data.values()),
            hole=.3,
            marker_colors=[self.colors['primary'], 
                          self.colors['secondary'],
                          '#00CC96',
                          '#AB63FA']
        )])
        
        fig.update_layout(
            title='Equipment-wise Consumption',
            template='plotly_white'
        )
        
        return fig
    
    def create_floor_comparison(self, df):
        """Create floor-wise consumption comparison"""
        floor_consumption = {
            f'Floor {i}': df[f'floor_{i}_fan'].sum() + df[f'floor_{i}_light'].sum()
            for i in range(1, 5)
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(floor_consumption.keys()),
            y=list(floor_consumption.values()),
            marker_color=self.colors['primary']
        )])
        
        fig.update_layout(
            title='Floor-wise Consumption',
            xaxis_title='Floor',
            yaxis_title='Total Consumption (Watt-hour)',
            template='plotly_white'
        )
        
        return fig
    
    def create_occupancy_correlation(self, df):
        """Create occupancy vs consumption scatter plot"""
        fig = px.scatter(
            df,
            x='occupancy_level',
            y='total_consumption',
            trendline='ols',
            color_discrete_sequence=[self.colors['primary']]
        )
        
        fig.update_layout(
            title='Occupancy vs Consumption Correlation',
            xaxis_title='Occupancy Level (%)',
            yaxis_title='Consumption (Watt-hour)',
            template='plotly_white'
        )
        
        return fig
    
    def create_efficiency_gauge(self, score):
        """Create efficiency score gauge"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': self.colors['primary']},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 100], 'color': "darkgray"}
                ]
            }
        ))
        
        fig.update_layout(
            title='Energy Efficiency Score',
            template='plotly_white'
        )
        
        return fig
    
    def create_prediction_plot(self, actual, predicted, dates):
        """Create prediction comparison plot"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=actual,
            mode='lines',
            name='Actual',
            line=dict(color=self.colors['primary'])
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=predicted,
            mode='lines',
            name='Predicted',
            line=dict(color=self.colors['secondary'])
        ))
        
        fig.update_layout(
            title='Actual vs Predicted Consumption',
            xaxis_title='Time',
            yaxis_title='Consumption (Watt-hour)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig