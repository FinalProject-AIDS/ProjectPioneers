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
    # def create_consumption_timeline(self):
    #     """Create interactive timeline of energy consumption"""
    #     fig = go.Figure()
        
    #     fig.add_trace(go.Scatter(
    #         x=self.df['timestamp'],
    #         y=self.df['total_consumption'],
    #         mode='lines',
    #         name='Total Consumption',
    #         line=dict(color=self.colors['primary'])
    #     ))
        
    #     fig.update_layout(
    #         title='Energy Consumption Timeline',
    #         xaxis_title='Time',
    #         yaxis_title='Consumption (Watt-hour)',
    #         template='plotly_white',
    #         hovermode='x unified'
    #     )
        
    #     return fig

    def create_consumption_timeline(self, time_frame="Daily"):
        """Create interactive timeline of energy consumption with adjustable time frame."""
        if time_frame == "Weekly":
            df_resampled = self.df.resample('W', on='timestamp').sum()
        elif time_frame == "Monthly":
            df_resampled = self.df.resample('M', on='timestamp').sum()
        elif time_frame == "Yearly":
            df_resampled = self.df.resample('Y', on='timestamp').sum()
        else:  # Default to daily
            df_resampled = self.df.resample('D', on='timestamp').sum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_resampled.index,
            y=df_resampled['total_consumption'],
            mode='lines',
            name='Total Consumption',
            line=dict(color=self.colors['primary'])
        ))

        fig.update_layout(
            title=f'Energy Consumption Timeline ({time_frame})',
            xaxis_title='Time',
            yaxis_title='Consumption (Watt-hour)',
            template='plotly_white',
            hovermode='x unified'
        )

        return fig

    def plot_consumption_trend(self, time_frame="Daily"):
        """
        Plots energy consumption trend based on the selected time frame.

        Parameters:
            time_frame (str): Time frame for aggregation ("Daily", "Weekly", "Monthly", "Yearly")
        
        Returns:
            fig (plotly.graph_objs._figure.Figure): Plotly figure for energy consumption trend
        """
        # Ensure timestamp is datetime
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        # Resample data based on selected time frame
        if time_frame == "Daily":
            df_resampled = self.df.resample('D', on='timestamp').sum()
        elif time_frame == "Weekly":
            df_resampled = self.df.resample('W', on='timestamp').sum()
        elif time_frame == "Monthly":
            df_resampled = self.df.resample('M', on='timestamp').sum()
        elif time_frame == "Yearly":
            df_resampled = self.df.resample('Y', on='timestamp').sum()
        else:
            raise ValueError("Invalid time frame. Choose from 'Daily', 'Weekly', 'Monthly', or 'Yearly'.")

        # Plot the resampled data
        fig = px.line(
            df_resampled,
            x=df_resampled.index,
            y="total_consumption",
            title=f"Energy Consumption Trend ({time_frame})",
            labels={"total_consumption": "Energy Consumption (Wh)", "timestamp": "Time"}
        )

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Total Consumption (Wh)",
            template="plotly_dark"
        )

        return fig

    def plot_peak_consumption(self, time_frame="Daily"):
        """Plot peak consumption over a specified time frame."""
        # Filter for numeric columns
        numeric_df = self.df.set_index('timestamp').select_dtypes(include=[np.number])

        if time_frame == "Weekly":
             df_resampled = numeric_df.resample('W').max()
        elif time_frame == "Monthly":
            df_resampled = numeric_df.resample('M').max()
        elif time_frame == "Yearly":
           df_resampled = numeric_df.resample('Y').max()
        else:  # Default to daily
            df_resampled = numeric_df.resample('D').max()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_resampled.index,
            y=df_resampled['total_consumption'],
            mode='lines+markers',
            name='Peak Consumption',
            line=dict(color=self.colors['tertiary'])
        ))

        fig.update_layout(
            title=f'Peak Energy Consumption ({time_frame})',
            xaxis_title='Time',
            yaxis_title='Peak Consumption (Watt-hour)',
            template='plotly_white'
        )

        return fig


    def plot_monthly_trend(self, time_frame="Daily"):
        """Create consumption trend based on the selected time frame"""
        
        # Set numeric columns and index
        numeric_df = self.df.set_index('timestamp').select_dtypes(include=[np.number])
        
        # Resample data based on the time frame
        if time_frame == "Weekly":
            df_resampled = numeric_df.resample('W').sum()  # Summing up weekly consumption
        elif time_frame == "Monthly":
            df_resampled = numeric_df.resample('M').sum()  # Summing up monthly consumption
        elif time_frame == "Yearly":
            df_resampled = numeric_df.resample('Y').sum()  # Summing up yearly consumption
        else:  # Default to daily
            df_resampled = numeric_df.resample('D').sum()  # Summing up daily consumption
        
        # Create the figure based on the resampled data
        fig = go.Figure(data=go.Bar(
            x=df_resampled.index,
            y=df_resampled['total_consumption'],  # Adjust according to your column name
            marker_color=self.colors['primary']
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{time_frame} Consumption Trend',
            xaxis_title=f'{time_frame} Period',
            yaxis_title='Total Consumption (Watt-hour)',
            template='plotly_white'
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
        """Create improved floor-wise consumption comparison"""
        # Aggregate floor-wise consumption
        floor_data = {}
        
        for _, row in self.df.iterrows():
            for floor in row['floor_data']:
                floor_name = floor['floor']
                if floor_name not in floor_data:
                    floor_data[floor_name] = {
                        'total': 0,
                        'fan': 0,
                        'light': 0
                    }
                floor_data[floor_name]['total'] += floor['total_floor_consumption']
                floor_data[floor_name]['fan'] += floor['fan_consumption']
                floor_data[floor_name]['light'] += floor['light_consumption']
        
        # Create grouped bar chart
        fig = go.Figure()
        
        # Add bars for each consumption type
        floors = list(floor_data.keys())
        
        fig.add_trace(go.Bar(
            name='Total Consumption',
            x=floors,
            y=[floor_data[floor]['total'] for floor in floors],
            marker_color=self.colors['primary']
        ))
        
        fig.add_trace(go.Bar(
            name='Fan Consumption',
            x=floors,
            y=[floor_data[floor]['fan'] for floor in floors],
            marker_color=self.colors['secondary']
        ))
        
        fig.add_trace(go.Bar(
            name='Light Consumption',
            x=floors,
            y=[floor_data[floor]['light'] for floor in floors],
            marker_color=self.colors['tertiary']
        ))
        
        fig.update_layout(
            title='Floor-wise Energy Consumption Breakdown',
            xaxis_title='Floor',
            yaxis_title='Consumption (Watt-hour)',
            barmode='group',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_occupancy_correlation(self):
        """Create improved occupancy vs consumption visualization"""
        # Prepare data
        df_hourly = pd.DataFrame({
            'timestamp': self.df['timestamp'],
            'occupancy': self.df['occupancy_level'],
            'consumption': self.df['total_consumption'],
            'hour': self.df['timestamp'].dt.hour,
            'day': self.df['timestamp'].dt.date
        })
        
        # Calculate average consumption for different occupancy levels
        occupancy_consumption = df_hourly.groupby('occupancy').agg({
            'consumption': 'mean'
        }).reset_index()
        
        # Create scatter plot with trend line
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=occupancy_consumption['occupancy'],
            y=occupancy_consumption['consumption'],
            mode='markers',
            name='Actual Data',
            marker=dict(
                size=8,
                color=occupancy_consumption['consumption'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Consumption (Wh)')
            )
        ))
        
        # Add trend line
        z = np.polyfit(occupancy_consumption['occupancy'], 
                       occupancy_consumption['consumption'], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=occupancy_consumption['occupancy'],
            y=p(occupancy_consumption['occupancy']),
            mode='lines',
            name='Trend Line',
            line=dict(color='red', dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='Occupancy vs Energy Consumption Correlation',
            xaxis_title='Occupancy Level (%)',
            yaxis_title='Average Consumption (Watt-hour)',
            template='plotly_white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add annotations for correlation insights
        correlation = occupancy_consumption['occupancy'].corr(
            occupancy_consumption['consumption']
        )
        
        fig.add_annotation(
            text=f'Correlation: {correlation:.2f}',
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        
        return fig

    # def create_efficiency_gauge(self, score):
    #     """Create efficiency score gauge"""
    #     fig = go.Figure(go.Indicator(
    #         mode="gauge+number",
    #         value=score,
    #         domain={'x': [0, 1], 'y': [0, 1]},
    #         gauge={
    #             'axis': {'range': [0, 100]},
    #             'bar': {'color': self.colors['primary']},
    #             'steps': [
    #                 {'range': [0, 50], 'color': "lightgray"},
    #                 {'range': [50, 75], 'color': "gray"},
    #                 {'range': [75, 100], 'color': "darkgray"}
    #             ]
    #         }
    #     ))
        
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

    # def get_summary_metrics(self):
    #     """Calculate and return summary metrics"""
    #     total_consumption = self.df['total_consumption'].sum()
    #     avg_daily_consumption = self.df.groupby(self.df['timestamp'].dt.date)['total_consumption'].sum().mean()
    #     total_cost = total_consumption * 0.12  # Assuming cost per Watt-hour
    #     avg_occupancy = self.df['occupancy_level'].mean()
        
    #     return {
    #         "total_consumption": total_consumption,
    #         "avg_daily_consumption": avg_daily_consumption,
    #         "total_cost": total_cost,
    #         "avg_occupancy": avg_occupancy
    #     }
    
    def display_cost_analysis(self):
        """Display cost analysis"""
        total_consumption = self.df['total_consumption'].sum()
        total_cost = total_consumption * 0.12  # Assuming cost per Watt-hour
        st.write(f"Total Consumption: {total_consumption / 1000:.2f} kWh")
        st.write(f"Total Cost: ${total_cost:.2f}")

    def get_summary_metrics(self):
        """Calculate and return summary metrics for the dashboard"""
        try:
            # Calculate total consumption
            total_consumption = self.df['total_consumption'].sum()
            
            # Calculate daily average consumption
            daily_consumption = self.df.groupby(
                self.df['timestamp'].dt.date
            )['total_consumption'].sum().mean()
            
            # Calculate total cost (using peak/off-peak rates)
            peak_hours = range(9, 18)  # 9 AM to 6 PM
            peak_consumption = self.df[
                self.df['timestamp'].dt.hour.isin(peak_hours)
            ]['total_consumption'].sum()
            offpeak_consumption = self.df[
                ~self.df['timestamp'].dt.hour.isin(peak_hours)
            ]['total_consumption'].sum()
            total_cost = (peak_consumption * 8 + offpeak_consumption * 6) / 1000  # Convert to kWh
            
            # Calculate average occupancy
            avg_occupancy = self.df['occupancy_level'].mean()
            
            return {
                'total_consumption': total_consumption,
                'avg_daily_consumption': daily_consumption,
                'total_cost': total_cost,
                'avg_occupancy': avg_occupancy,
                'peak_consumption': peak_consumption,
                'offpeak_consumption': offpeak_consumption
            }
        except Exception as e:
            st.error(f"Error calculating summary metrics: {str(e)}")
            return {
                'total_consumption': 0,
                'avg_daily_consumption': 0,
                'total_cost': 0,
                'avg_occupancy': 0,
                'peak_consumption': 0,
                'offpeak_consumption': 0
            }
    def calculate_efficiency_score(self):
        """Calculate energy efficiency score based on multiple metrics"""
        try:
            latest_data = self.df.iloc[-1]  # Get most recent data point
            
            score = 100
            metrics = {}
            
            # 1. Occupancy Efficiency (30 points)
            per_person_consumption = latest_data['total_consumption'] / latest_data['occupancy_level']
            metrics['occupancy_score'] = min(30, (30 * (1000 / per_person_consumption)))
            
            # 2. Peak Load Efficiency (20 points)
            peak_load_ratio = latest_data['total_consumption'] / latest_data['peak_load']
            metrics['peak_load_score'] = 20 * peak_load_ratio
            
            # 3. Equipment Utilization (20 points)
            floor_data = latest_data['floor_data'] if isinstance(latest_data['floor_data'], list) else []
            total_equipment = sum(
                floor.get('fan_consumption', 0) + floor.get('light_consumption', 0) 
                for floor in floor_data
            )
            equipment_ratio = total_equipment / latest_data['total_consumption']
            metrics['equipment_score'] = 20 * (1 - equipment_ratio)
            
            # 4. Temperature Optimization (15 points)
            optimal_temp = 22
            temp_diff = abs(latest_data['temperature'] - optimal_temp)
            metrics['temperature_score'] = 15 * (1 - (temp_diff / 10))
            
            # 5. Time-based Usage (15 points)
            time_scores = {
                "Morning": 15,
                "Afternoon": 10,
                "Evening": 5
            }
            metrics['time_score'] = time_scores.get(latest_data['time_of_day'], 5)
            
            # Calculate final score
            final_score = sum(metrics.values())
            final_score = max(0, min(100, round(final_score)))
            
            return final_score, metrics
            
        except Exception as e:
            st.error(f"Error calculating efficiency score: {str(e)}")
            return 0, {}

    def create_efficiency_gauge(self, score):
        """Create an efficiency gauge visualization"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            },
            title={'text': "Energy Efficiency Score"}
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=50, b=10),
            font={'size': 16}
        )
        
        return fig

    def display_efficiency_metrics(self, metrics):
        """Display detailed breakdown of efficiency metrics"""
        col1, col2 = st.columns(2)
        
        with col1:
            metrics_data = {
                "Occupancy Efficiency": {"score": metrics['occupancy_score'], "max": 30},
                "Peak Load Efficiency": {"score": metrics['peak_load_score'], "max": 20},
                "Equipment Utilization": {"score": metrics['equipment_score'], "max": 20},
            }
            
            for metric, data in metrics_data.items():
                st.metric(
                    metric,
                    f"{data['score']:.1f}/{data['max']}",
                    delta=f"{(data['score']/data['max']*100):.1f}%"
                )
                
        with col2:
            metrics_data = {
                "Temperature Optimization": {"score": metrics['temperature_score'], "max": 15},
                "Time-based Usage": {"score": metrics['time_score'], "max": 15}
            }
            
            for metric, data in metrics_data.items():
                st.metric(
                    metric,
                    f"{data['score']:.1f}/{data['max']}",
                    delta=f"{(data['score']/data['max']*100):.1f}%"
                )

    def create_optimization_recommendations(self, metrics):
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        if metrics['occupancy_score'] < 20:
            recommendations.append({
                "category": "Occupancy",
                "priority": "High",
                "suggestion": "Consider adjusting HVAC and lighting schedules to better match occupancy patterns"
            })
            
        if metrics['peak_load_score'] < 15:
            recommendations.append({
                "category": "Peak Load",
                "priority": "Medium",
                "suggestion": "Implement load shifting strategies to reduce peak demand"
            })
            
        if metrics['equipment_score'] < 15:
            recommendations.append({
                "category": "Equipment",
                "priority": "High",
                "suggestion": "Review equipment scheduling and consider upgrading to more efficient models"
            })
            
        if metrics['temperature_score'] < 10:
            recommendations.append({
                "category": "Temperature",
                "priority": "Medium",
                "suggestion": "Adjust temperature setpoints closer to optimal range (22°C)"
            })
            
        return recommendations
    def display_recommendations(self):
        """Display energy-saving recommendations"""
        # Here you can call the RecommendationEngine or define some placeholder recommendations
        st.write("Here are some energy-saving recommendations:")
        st.write("- Consider turning off unnecessary lights.")
        st.write("- Adjust the thermostat based on occupancy levels.")
        st.write("- Optimize equipment usage during peak hours.")

    def calculate_total_cost(self):
        """Calculate total energy cost"""
        # Using standard rates: Peak (₹8/kWh), Off-peak (₹6/kWh)
        peak_hours = range(9, 18)  # 9 AM to 6 PM
        
        peak_consumption = self.df[
            self.df['timestamp'].dt.hour.isin(peak_hours)
        ]['total_consumption'].sum()
        
        offpeak_consumption = self.df[
            ~self.df['timestamp'].dt.hour.isin(peak_hours)
        ]['total_consumption'].sum()
        
        total_cost = (peak_consumption * 8 + offpeak_consumption * 6) / 1000  # Convert to kWh
        return total_cost

    def calculate_cost_change(self):
        """Calculate percentage change in cost compared to previous period"""
        current_period = self.df['total_consumption'].sum()
        previous_period = self.df.shift(1)['total_consumption'].sum()
        
        if previous_period == 0:
            return 0
        
        change = ((current_period - previous_period) / previous_period) * 100
        return round(change, 2)

    def calculate_cost_per_kwh(self):
        """Calculate average cost per kWh"""
        total_consumption_kwh = self.df['total_consumption'].sum() / 1000
        total_cost = self.calculate_total_cost()
        
        if total_consumption_kwh == 0:
            return 0
        
        return total_cost / total_consumption_kwh

    def calculate_peak_hour_cost(self):
        """Calculate cost during peak hours"""
        peak_hours = range(9, 18)
        peak_consumption = self.df[
            self.df['timestamp'].dt.hour.isin(peak_hours)
        ]['total_consumption'].sum()
        
        return (peak_consumption * 8) / 1000  # ₹8 per kWh during peak hours

    def project_monthly_cost(self):
        """Project next month's cost based on current trends"""
        # Calculate daily average cost
        daily_costs = self.df.groupby(self.df['timestamp'].dt.date)['total_consumption'].sum()
        avg_daily_cost = (daily_costs.mean() * 7) / 1000  # ₹7 average per kWh
        
        # Project for 30 days
        return avg_daily_cost * 30

    def plot_time_of_use_costs(self):
        """Create time-of-use cost distribution visualization"""
        hourly_consumption = self.df.groupby(
            self.df['timestamp'].dt.hour
        )['total_consumption'].mean()
        
        # Apply different rates for peak and off-peak hours
        hourly_costs = hourly_consumption.copy()
        peak_hours = range(9, 18)
        
        for hour, consumption in hourly_consumption.items():
            rate = 8 if hour in peak_hours else 6  # ₹8 peak, ₹6 off-peak
            hourly_costs[hour] = (consumption * rate) / 1000
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hourly_costs.index,
            y=hourly_costs.values,
            name='Hourly Cost',
            marker_color=self.colors['primary']
        ))
        
        fig.update_layout(
            title='Hourly Cost Distribution',
            xaxis_title='Hour of Day',
            yaxis_title='Average Cost (₹)',
            template='plotly_white'
        )
        
        return fig

    def plot_peak_vs_offpeak(self):
        """Create peak vs off-peak comparison visualization"""
        peak_hours = range(9, 18)
        
        peak_data = self.df[
            self.df['timestamp'].dt.hour.isin(peak_hours)
        ]['total_consumption'].sum()
        
        offpeak_data = self.df[
            ~self.df['timestamp'].dt.hour.isin(peak_hours)
        ]['total_consumption'].sum()
        
        fig = go.Figure(data=[go.Pie(
            labels=['Peak Hours', 'Off-Peak Hours'],
            values=[peak_data, offpeak_data],
            hole=.3,
            marker_colors=[self.colors['primary'], self.colors['secondary']]
        )])
        
        fig.update_layout(
            title='Peak vs Off-Peak Consumption',
            template='plotly_white'
        )
        
        return fig

    def plot_equipment_costs(self):
        """Create equipment-wise cost distribution visualization using actual data"""
        # Initialize containers for equipment costs
        equipment_costs = {
            'Fans': 0,
            'Lights': 0,
            'Computers': 0,
            'Projectors': 0
        }
        
        # Aggregate floor-wise equipment consumption
        for _, row in self.df.iterrows():
            for floor in row['floor_data']:
                equipment_costs['Fans'] += floor['fan_consumption']
                equipment_costs['Lights'] += floor['light_consumption']
            
            # Add shared equipment consumption
            equipment_costs['Computers'] += row['shared_equipment']['computer_consumption']
            equipment_costs['Projectors'] += row['shared_equipment']['projector_consumption']
        
        # Convert consumption to costs (₹8 per kWh for peak, ₹6 for off-peak)
        rate = 8 if 9 <= pd.to_datetime(row['timestamp']).hour < 18 else 6
        equipment_costs = {k: (v * rate) / 1000 for k, v in equipment_costs.items()}
        
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
            title='Equipment-wise Cost Distribution',
            template='plotly_white'
        )
        
        return fig

    def get_top_consuming_equipment(self):
        """Get top energy consuming equipment with costs"""
        # Sample data - replace with actual equipment data
        equipment_data = {
            'Equipment': ['HVAC', 'Lighting', 'Computers', 'Server Room'],
            'Consumption (kWh)': [1500, 800, 500, 400],
            'Cost (₹)': [12000, 6400, 4000, 3200],
            'Usage Hours': [24, 12, 8, 24]
        }
        return pd.DataFrame(equipment_data)

    def plot_floor_costs(self):
        """Create floor-wise cost analysis visualization"""
        # Assuming floor data is available in self.df
        floor_consumption = {
            'Floor 1': self.df['total_consumption'].sum() * 0.3,
            'Floor 2': self.df['total_consumption'].sum() * 0.25,
            'Floor 3': self.df['total_consumption'].sum() * 0.25,
            'Floor 4': self.df['total_consumption'].sum() * 0.2
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(floor_consumption.keys()),
            y=list(floor_consumption.values()),
            marker_color=self.colors['primary']
        )])
        
        fig.update_layout(
            title='Floor-wise Cost Distribution',
            xaxis_title='Floor',
            yaxis_title='Cost (₹)',
            template='plotly_white'
        )
        
        return fig

    def calculate_saving_opportunities(self):
        """Calculate potential cost saving opportunities"""
        total_consumption = self.df['total_consumption'].sum()
        
        return [
            {
                'title': 'HVAC Optimization',
                'current_cost': total_consumption * 0.45 * 7 / 1000,  # 45% of total
                'potential_savings': total_consumption * 0.45 * 7 * 0.2 / 1000,  # 20% savings
                'implementation_cost': 50000,
                'payback_period': '8 months',
                'roi': 25,
                'action_plan': 'Implement smart HVAC controls and scheduling'
            },
            {
                'title': 'Lighting Upgrade',
                'current_cost': total_consumption * 0.25 * 7 / 1000,  # 25% of total
                'potential_savings': total_consumption * 0.25 * 7 * 0.3 / 1000,  # 30% savings
                'implementation_cost': 30000,
                'payback_period': '6 months',
                'roi': 35,
                'action_plan': 'Replace with LED lights and motion sensors'
            }
        ]

    def plot_cost_trends(self):
        """Create historical cost trends visualization"""
        daily_costs = self.df.groupby(self.df['timestamp'].dt.date).agg({
            'total_consumption': 'sum'
        }).reset_index()
        
        daily_costs['cost'] = daily_costs['total_consumption'] * 7 / 1000  # Average ₹7 per kWh
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_costs['timestamp'],
            y=daily_costs['cost'],
            mode='lines',
            name='Daily Cost',
            line=dict(color=self.colors['primary'])
        ))
        
        fig.update_layout(
            title='Historical Cost Trends',
            xaxis_title='Date',
            yaxis_title='Daily Cost (₹)',
            template='plotly_white'
        )
        
        return fig

    def plot_budget_vs_actual(self):
        """Create budget vs actual comparison visualization"""
        # Sample budget data - replace with actual budget data
        dates = self.df['timestamp'].dt.date.unique()
        budget_data = pd.DataFrame({
            'date': dates,
            'budget': [5000] * len(dates),  # Sample daily budget
            'actual': self.df.groupby(self.df['timestamp'].dt.date)['total_consumption'].sum() * 7 / 1000
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=budget_data['date'],
            y=budget_data['budget'],
            mode='lines',
            name='Budget',
            line=dict(color=self.colors['secondary'])
        ))
        fig.add_trace(go.Scatter(
            x=budget_data['date'],
            y=budget_data['actual'],
            mode='lines',
            name='Actual',
            line=dict(color=self.colors['primary'])
        ))
        
        fig.update_layout(
            title='Budget vs Actual Cost',
            xaxis_title='Date',
            yaxis_title='Cost (₹)',
            template='plotly_white'
        )
        
        return fig

    def calculate_budget_utilization(self):
        """Calculate budget utilization percentage"""
        total_actual = self.df['total_consumption'].sum() * 7 / 1000
        total_budget = len(self.df['timestamp'].dt.date.unique()) * 5000  # Sample budget
        
        return (total_actual / total_budget) * 100 if total_budget > 0 else 0

    def project_budget_variance(self):
        """Project budget variance for the period"""
        total_actual = self.df['total_consumption'].sum() * 7 / 1000
        total_budget = len(self.df['timestamp'].dt.date.unique()) * 5000  # Sample budget
        
        return total_budget - total_actual

    def get_cost_alerts(self):
        """Generate cost-related alerts"""
        alerts = []
        
        # Check for unusual consumption patterns
        avg_daily_consumption = self.df.groupby(
            self.df['timestamp'].dt.date
        )['total_consumption'].mean().mean()
        
        recent_consumption = self.df.groupby(
            self.df['timestamp'].dt.date
        )['total_consumption'].mean().iloc[-1]
        
        if recent_consumption > avg_daily_consumption * 1.2:
            alerts.append(f"⚠️ Recent consumption is {((recent_consumption/avg_daily_consumption)-1)*100:.1f}% above average")
        
        # Check budget utilization
        if self.calculate_budget_utilization() > 90:
            alerts.append("⚠️ Budget utilization above 90%")
        
        # Check peak hour usage
        peak_ratio = self.calculate_peak_hour_cost() / self.calculate_total_cost()
        if peak_ratio > 0.6:
            alerts.append("⚠️ High peak hour usage (>60% of total cost)")
        
        return alerts

    def generate_cost_report(self, format='Excel'):
        """Generate exportable cost report"""
        # Create a comprehensive report
        report_data = {
            'total_cost': self.calculate_total_cost(),
            'peak_hour_cost': self.calculate_peak_hour_cost(),
            'cost_per_kwh': self.calculate_cost_per_kwh(),
            'budget_utilization': self.calculate_budget_utilization(),
            'projected_variance': self.project_budget_variance()
        }
        
        # Return formatted report based on selected format
        if format == 'Excel':
            return pd.DataFrame([report_data]).to_excel()
        elif format == 'CSV':
            return pd.DataFrame([report_data]).to_csv()
        else:  # PDF
            return pd.DataFrame([report_data]).to_json()  # Placeholder for PDF generation

    def calculate_floor_costs(self):
        """Calculate detailed floor-wise costs"""
        floor_details = {}
        
        for _, row in self.df.iterrows():
            for floor_data in row['floor_data']:
                floor_name = floor_data['floor']
                if floor_name not in floor_details:
                    floor_details[floor_name] = {
                        'total_consumption': 0,
                        'peak_consumption': 0,
                        'off_peak_consumption': 0,
                        'fan_consumption': 0,
                        'light_consumption': 0,
                        'total_cost': 0
                    }
                
                # Add consumption data
                floor_details[floor_name]['total_consumption'] += floor_data['total_floor_consumption']
                floor_details[floor_name]['fan_consumption'] += floor_data['fan_consumption']
                floor_details[floor_name]['light_consumption'] += floor_data['light_consumption']
                
                # Calculate costs based on time of day
                hour = pd.to_datetime(row['timestamp']).hour
                rate = 8 if 9 <= hour < 18 else 6  # ₹8 for peak, ₹6 for off-peak
                
                if 9 <= hour < 18:
                    floor_details[floor_name]['peak_consumption'] += floor_data['total_floor_consumption']
                else:
                    floor_details[floor_name]['off_peak_consumption'] += floor_data['total_floor_consumption']
                
                floor_details[floor_name]['total_cost'] += (floor_data['total_floor_consumption'] * rate) / 1000
        
        return floor_details

    def calculate_efficiency_metrics(self):
        """Calculate efficiency metrics for each floor and overall building"""
        try:
            metrics = {}
            
            # Calculate overall building metrics first
            total_consumption = self.df['total_consumption'].sum()
            total_peak_load = self.df['peak_load'].sum()
            avg_occupancy = self.df['occupancy_level'].mean()
            
            # Calculate metrics for each floor
            for _, row in self.df.iterrows():
                for floor_data in row['floor_data']:
                    floor_name = floor_data['floor']
                    if floor_name not in metrics:
                        metrics[floor_name] = {
                            'total_consumption': 0,
                            'consumption_per_occupant': 0,
                            'peak_efficiency': 0,
                            'utilization_rate': 0
                        }
                    
                    # Update floor metrics
                    floor_consumption = floor_data['total_floor_consumption']
                    metrics[floor_name]['total_consumption'] += floor_consumption
                    
                    # Calculate consumption per occupant (if occupancy data available)
                    if row['occupancy_level'] > 0:
                        metrics[floor_name]['consumption_per_occupant'] = (
                            floor_consumption / row['occupancy_level']
                        )
                    
                    # Calculate peak efficiency (consumption vs peak load)
                    if row['peak_load'] > 0:
                        metrics[floor_name]['peak_efficiency'] = (
                            floor_consumption / row['peak_load']
                        )
                    
                    # Calculate utilization rate (actual vs maximum possible consumption)
                    max_possible = (floor_data['fan_consumption'] + 
                                  floor_data['light_consumption']) * 24  # assuming 24h max
                    if max_possible > 0:
                        metrics[floor_name]['utilization_rate'] = (
                            floor_consumption / max_possible
                        )
            
            # Add overall building efficiency
            metrics['Overall'] = {
                'total_consumption': total_consumption,
                'consumption_per_occupant': total_consumption / avg_occupancy if avg_occupancy > 0 else 0,
                'peak_efficiency': total_consumption / total_peak_load if total_peak_load > 0 else 0,
                'utilization_rate': sum(m['utilization_rate'] for m in metrics.values()) / len(metrics)
            }
            
            return metrics
        
        except Exception as e:
            st.error(f"Error calculating efficiency metrics: {str(e)}")
            return {
                'Overall': {
                    'total_consumption': 0,
                    'consumption_per_occupant': 0,
                    'peak_efficiency': 0,
                    'utilization_rate': 0
                }
            }

    def plot_appliance_costs(self):
        """Create appliance-wise cost distribution visualization"""
        try:
            # Initialize appliance consumption dictionary
            appliance_consumption = {
                'Fan': 0,
                'Light': 0,
                'Computer': 0,
                'Projector': 0,
                'Other': 0
            }
            
            # Aggregate consumption by appliance type
            for _, row in self.df.iterrows():
                for floor_data in row['floor_data']:
                    appliance_consumption['Fan'] += floor_data['fan_consumption']
                    appliance_consumption['Light'] += floor_data['light_consumption']
                
                # Add shared equipment consumption
                if 'shared_equipment' in row:
                    appliance_consumption['Computer'] += row['shared_equipment'].get('computer_consumption', 0)
                    appliance_consumption['Projector'] += row['shared_equipment'].get('projector_consumption', 0)
            
            # Calculate costs (using average rate of ₹7/kWh)
            appliance_costs = {
                appliance: (consumption * 7) / 1000  # Convert to kWh and multiply by rate
                for appliance, consumption in appliance_consumption.items()
                if consumption > 0  # Only include appliances with consumption
            }
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(appliance_costs.keys()),
                values=list(appliance_costs.values()),
                hole=.3,
                marker_colors=[
                    self.colors['primary'],
                    self.colors['secondary'],
                    self.colors['tertiary'],
                    self.colors['quaternary']
                ]
            )])
            
            fig.update_layout(
                title='Appliance-wise Cost Distribution',
                template='plotly_white',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating appliance cost plot: {str(e)}")
            return go.Figure()