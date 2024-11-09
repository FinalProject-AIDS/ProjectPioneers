import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

class DashboardComponents:
    def __init__(self, df, theme_colors=None):
        self.df = df.copy()
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])  # Add this line
        self.colors = theme_colors if theme_colors is not None else {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'tertiary': '#2ca02c',
            'quaternary': '#d62728'
        }

    # Rest of the class methods remain unchanged
    def create_consumption_timeline(self):
        """Create interactive timeline of energy consumption"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df['timestamp'],
            y=self.df['total_consumption'],
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

    def create_heatmap(self):
        """Create hourly consumption heatmap"""
        # Pivot data for heatmap
        heatmap_data = self.df.pivot_table(
            values='total_consumption',
            index=self.df['timestamp'].dt.day_name(),
            columns=self.df['timestamp'].dt.hour,
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
                          self.colors['tertiary'],
                          self.colors['quaternary']]
        )])
        
        fig.update_layout(
            title='Equipment-wise Consumption',
            template='plotly_white'
        )
        
        return fig

    def create_floor_comparison(self):
        """Create floor-wise consumption comparison"""
        floor_consumption = {
            f'Floor {i}': self.df[f'floor_{i}_fan'].sum() + self.df[f'floor_{i}_light'].sum()
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

    def create_occupancy_correlation(self):
        """Create occupancy vs consumption scatter plot"""
        fig = px.scatter(
            self.df,
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

    def get_summary_metrics(self):
        """Calculate and return summary metrics"""
        total_consumption = self.df['total_consumption'].sum()
        avg_daily_consumption = self.df.groupby(self.df['timestamp'].dt.date)['total_consumption'].sum().mean()
        total_cost = total_consumption * 0.12  # Assuming cost per Watt-hour
        avg_occupancy = self.df['occupancy_level'].mean()
        
        return {
            "total_consumption": total_consumption,
            "avg_daily_consumption": avg_daily_consumption,
            "total_cost": total_cost,
            "avg_occupancy": avg_occupancy
        }
    
    def display_cost_analysis(self):
        """Display cost analysis"""
        total_consumption = self.df['total_consumption'].sum()
        total_cost = total_consumption * 0.12  # Assuming cost per Watt-hour
        st.write(f"Total Consumption: {total_consumption / 1000:.2f} kWh")
        st.write(f"Total Cost: ${total_cost:.2f}")

    def display_recommendations(self):
        """Display energy-saving recommendations"""
        # Here you can call the RecommendationEngine or define some placeholder recommendations
        st.write("Here are some energy-saving recommendations:")
        st.write("- Consider turning off unnecessary lights.")
        st.write("- Adjust the thermostat based on occupancy levels.")
        st.write("- Optimize equipment usage during peak hours.")