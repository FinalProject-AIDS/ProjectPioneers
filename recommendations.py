import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class RecommendationEngine:
    def __init__(self, df):
        self.df = df.copy()  # Create a copy to avoid modifying original
        # Add necessary time-based columns
        self.df['hour'] = pd.to_datetime(self.df['timestamp']).dt.hour
        self.df['month'] = pd.to_datetime(self.df['timestamp']).dt.month
        self.df['is_weekend'] = pd.to_datetime(self.df['timestamp']).dt.dayofweek.isin([5, 6])
        self.recommendations = []
        
        # Add tracking for implementation status and reminders
        if 'implemented_recommendations' not in st.session_state:
            st.session_state.implemented_recommendations = set()
        if 'recommendation_reminders' not in st.session_state:
            st.session_state.recommendation_reminders = {}
        
    def generate_recommendations(self):
        """Generate comprehensive energy savings recommendations"""
        self._analyze_peak_usage()
        self._analyze_equipment_usage()
        self._analyze_occupancy_patterns()
        self._analyze_after_hours()
        self._analyze_efficiency_patterns()
        self._analyze_seasonal_patterns()
        self._analyze_maintenance_needs()
        self._generate_cost_savings()
        
        return self.recommendations
    
    def _analyze_peak_usage(self):
        """Analyze and recommend based on peak usage patterns"""
        peak_hours = self.df.groupby('hour')['total_consumption'].mean()
        top_peak_hours = peak_hours.nlargest(3)
        
        recommendation = {
            'category': 'Peak Usage',
            'findings': f"Peak consumption occurs at {', '.join(str(h) for h in top_peak_hours.index)}:00",
            'recommendations': [
                "Consider load balancing during peak hours",
                "Schedule high-consumption tasks during off-peak hours",
                f"Reduce non-essential equipment usage during {top_peak_hours.index[0]}:00"
            ],
            'potential_savings': f"{(top_peak_hours.mean() - peak_hours.mean()) * 30:.2f} Watt-hours per month"
        }
        self.recommendations.append(recommendation)
    
    def _analyze_equipment_usage(self):
        """Analyze and recommend based on equipment usage patterns"""
        avg_consumption = self.df['total_consumption'].mean()
        
        equipment_recommendations = {
            'category': 'Equipment Usage',
            'findings': "Analysis of overall consumption patterns",
            'recommendations': [
                "Configure all computers to enter sleep mode after 15 minutes of inactivity",
                "Install motion sensors for automatic equipment shutdown",
                "Implement a policy for turning off non-essential equipment during breaks",
                "Use smart power strips to reduce standby power consumption"
            ],
            'potential_savings': "10-15% of current equipment energy usage"
        }
        
        self.recommendations.append(equipment_recommendations)
    
    def _analyze_occupancy_patterns(self):
        """Analyze and recommend based on occupancy patterns"""
        if 'occupancy_level' not in self.df.columns:
            recommendation = {
                'category': 'Occupancy Optimization',
                'findings': "No detailed occupancy data available",
                'recommendations': [
                    "Install occupancy sensors in all areas",
                    "Implement zone-based lighting controls",
                    "Set up automated HVAC scheduling",
                    "Consider smart building management system"
                ],
                'potential_savings': "15-20% on lighting and HVAC costs"
            }
            self.recommendations.append(recommendation)
            return

        avg_consumption_per_occupant = (
            self.df['total_consumption'] / self.df['occupancy_level']
        ).mean()
        
        recommendation = {
            'category': 'Occupancy Optimization',
            'findings': f"Average consumption per occupant: {avg_consumption_per_occupant:.2f} Watt-hours",
            'recommendations': [
                "Implement zone-based lighting controls",
                "Install occupancy sensors in less frequently used areas",
                "Optimize HVAC settings based on occupancy patterns"
            ],
            'potential_savings': "15-25% on lighting and HVAC costs"
        }
        self.recommendations.append(recommendation)
    
    def _analyze_after_hours(self):
        """Analyze and recommend based on after-hours usage"""
        after_hours = self.df[
            (self.df['hour'] >= 18) | (self.df['hour'] <= 6)
        ]['total_consumption'].mean()
        
        if after_hours > 100:  # Threshold can be adjusted
            recommendation = {
                'category': 'After-Hours Usage',
                'findings': f"Significant after-hours consumption detected: {after_hours:.2f} Watt-hours",
                'recommendations': [
                    "Implement automatic shutdown procedures for non-essential equipment",
                    "Review and adjust timer settings for all systems",
                    "Consider motion-sensor-based lighting for after-hours operations"
                ],
                'potential_savings': f"{(after_hours * 0.5 * 30):.2f} Watt-hours per month"
            }
            self.recommendations.append(recommendation)
    
    def _analyze_efficiency_patterns(self):
        """Analyze and recommend based on efficiency patterns"""
        weekend_consumption = self.df[
            self.df['is_weekend']
        ]['total_consumption'].mean()
        weekday_consumption = self.df[
            ~self.df['is_weekend']
        ]['total_consumption'].mean()
        
        if weekend_consumption > (weekday_consumption * 0.3):
            recommendation = {
                'category': 'Weekend Efficiency',
                'findings': f"Weekend consumption ({weekend_consumption:.2f} Wh) is significant compared to weekday usage ({weekday_consumption:.2f} Wh)",
                'recommendations': [
                    "Schedule complete equipment shutdown during weekends",
                    "Implement weekend-specific HVAC schedules",
                    "Review and optimize weekend security lighting",
                    "Consider motion sensors for weekend lighting control"
                ],
                'potential_savings': f"{(weekend_consumption - weekday_consumption * 0.2) * 8:.2f} Watt-hours per month"
            }
            self.recommendations.append(recommendation)

    def _analyze_seasonal_patterns(self):
        """Analyze and recommend based on seasonal patterns"""
        if 'month' not in self.df.columns:
            self.df['month'] = pd.to_datetime(self.df['timestamp']).dt.month

        monthly_consumption = self.df.groupby('month')['total_consumption'].mean()
        peak_month = monthly_consumption.idxmax()
        peak_consumption = monthly_consumption.max()
        avg_consumption = monthly_consumption.mean()

        if peak_consumption > (avg_consumption * 1.3):
            recommendation = {
                'category': 'Seasonal Optimization',
                'findings': f"Peak seasonal consumption in month {peak_month}",
                'recommendations': [
                    "Adjust HVAC settings based on seasonal weather patterns",
                    "Implement seasonal lighting schedules",
                    "Consider natural ventilation during moderate weather",
                    "Schedule preventive maintenance before peak seasons"
                ],
                'potential_savings': f"{(peak_consumption - avg_consumption) * 30:.2f} Watt-hours per month during peak season"
            }
            self.recommendations.append(recommendation)

    def _analyze_maintenance_needs(self):
        """Analyze and recommend based on maintenance patterns"""
        # Calculate efficiency decline over time
        recent_efficiency = self.df.tail(24)['total_consumption'].mean()
        past_efficiency = self.df.head(24)['total_consumption'].mean()
        efficiency_decline = (recent_efficiency - past_efficiency) / past_efficiency

        if efficiency_decline > 0.1:  # 10% decline in efficiency
            recommendation = {
                'category': 'Maintenance Requirements',
                'findings': f"System efficiency has declined by {efficiency_decline*100:.1f}%",
                'recommendations': [
                    "Schedule comprehensive system maintenance",
                    "Clean or replace HVAC filters",
                    "Inspect and clean lighting fixtures",
                    "Check and calibrate all sensors",
                    "Verify equipment operating parameters"
                ],
                'potential_savings': f"{(recent_efficiency - past_efficiency) * 30:.2f} Watt-hours per month"
            }
            self.recommendations.append(recommendation)

    def _generate_cost_savings(self):
        """Generate cost-based recommendations with detailed ROI analysis"""
        total_consumption = self.df['total_consumption'].sum()
        avg_daily_consumption = self.df.groupby(pd.to_datetime(self.df['timestamp']).dt.date)['total_consumption'].mean().mean()
        
        # Enhanced cost calculations
        energy_rates = {
            'peak': 12.0,    # ₹/kWh during peak hours
            'off_peak': 6.0, # ₹/kWh during off-peak
            'solar': 3.0,    # ₹/kWh with solar
        }
        
        implementation_costs = {
            'motion_sensors': {
                'cost': 2500,  # ₹ per sensor
                'units_needed': 10,
                'installation': 5000,
                'maintenance_yearly': 2000,
            },
            'solar_panels': {
                'cost': 50000,  # ₹ per kW
                'capacity_kw': 10,
                'installation': 100000,
                'maintenance_yearly': 25000,
            },
            'smart_monitoring': {
                'cost': 75000,
                'subscription_yearly': 12000,
            }
        }
        
        # Using ₹8 per kWh (typical Indian rate)
        daily_cost = (avg_daily_consumption * 8) / 1000
        
        recommendation = {
            'category': 'Cost Optimization',
            'findings': f"Average daily energy cost: ₹{daily_cost:.2f}",
            'recommendations': [
                {
                    'title': "Time-of-Day Usage Optimization",
                    'description': "Shift non-essential operations to off-peak hours (10 PM - 6 AM) for better rates",
                    'impact': "High",
                    'implementation_cost': "Low",
                    'payback_period': "1-2 months"
                },
                {
                    'title': "Solar Energy Integration",
                    'description': "Install solar panels for sustainable energy generation",
                    'impact': "Very High",
                    'implementation_cost': "High",
                    'payback_period': "3-4 years"
                },
                {
                    'title': "Smart Monitoring System",
                    'description': "Implement real-time energy monitoring with mobile alerts",
                    'impact': "Medium",
                    'implementation_cost': "Medium",
                    'payback_period': "6-8 months"
                }
            ],
            'potential_savings': f"₹{(daily_cost * 0.2 * 30):.2f} per month through optimizations",
            'priority': 'High'
        }
        self.recommendations.append(recommendation)

    def get_priority_recommendations(self, top_n=3):
        """Return top N recommendations based on potential savings"""
        def extract_savings(rec):
            # Extract numeric value from potential_savings string
            try:
                return float(''.join(filter(str.isdigit, rec['potential_savings'])))
            except:
                return 0

        sorted_recommendations = sorted(
            self.recommendations,
            key=extract_savings,
            reverse=True
        )
        return sorted_recommendations[:top_n]

    def get_recommendations_by_category(self, category):
        """Filter recommendations by category"""
        return [rec for rec in self.recommendations if rec['category'] == category]

    def export_recommendations(self, format='dict'):
        """Export recommendations in various formats"""
        if format == 'dict':
            return self.recommendations
        elif format == 'df':
            return pd.DataFrame(self.recommendations)
        elif format == 'json':
            return pd.DataFrame(self.recommendations).to_json(orient='records')
        else:
            raise ValueError("Unsupported format. Use 'dict', 'df', or 'json'")

    def display_recommendations(self):
        """Display all recommendations in a formatted way"""
        if not self.recommendations:
            return "No recommendations generated yet. Please run generate_recommendations() first."
            
        formatted_recommendations = []
        for rec in self.recommendations:
            # Create a more structured and detailed format
            formatted_rec = f"""
### {rec['category']} (Priority: {rec.get('priority', 'Medium')})

**Current Status:**
{rec['findings']}

**Potential Impact:**
{rec.get('potential_savings', 'Savings to be calculated')}

**Recommended Actions:**
"""
            # Check if recommendations is a list of dictionaries (new format) or list of strings (old format)
            if isinstance(rec['recommendations'][0], dict):
                for action in rec['recommendations']:
                    formatted_rec += f"""
* **{action['title']}**
  - {action['description']}
  - Impact: {action['impact']}
  - Implementation Cost: {action['implementation_cost']}
  - Payback Period: {action['payback_period']}
"""
            else:
                for action in rec['recommendations']:
                    formatted_rec += f"* {action}\n"

            formatted_rec += "\n---"
            formatted_recommendations.append(formatted_rec)
            
        return formatted_recommendations

    def calculate_roi(self, recommendation_type):
        """Calculate detailed ROI for different types of recommendations"""
        
        roi_data = {
            'lighting_optimization': {
                'initial_cost': 50000,
                'monthly_savings': 8000,
                'lifespan_years': 5,
                'maintenance_cost_yearly': 2000
            },
            'hvac_optimization': {
                'initial_cost': 150000,
                'monthly_savings': 25000,
                'lifespan_years': 10,
                'maintenance_cost_yearly': 15000
            },
            'solar_installation': {
                'initial_cost': 600000,
                'monthly_savings': 45000,
                'lifespan_years': 25,
                'maintenance_cost_yearly': 25000
            }
        }
        
        if recommendation_type not in roi_data:
            return None
            
        data = roi_data[recommendation_type]
        
        # Calculate NPV and ROI
        monthly_rate = 0.10 / 12  # 10% annual interest rate
        total_months = data['lifespan_years'] * 12
        
        npv = -data['initial_cost']
        for month in range(total_months):
            monthly_benefit = data['monthly_savings'] - (data['maintenance_cost_yearly'] / 12)
            npv += monthly_benefit / (1 + monthly_rate) ** month
            
        roi = (npv / data['initial_cost']) * 100
        payback_months = data['initial_cost'] / data['monthly_savings']
        
        return {
            'npv': npv,
            'roi_percentage': roi,
            'payback_months': payback_months,
            'monthly_savings': data['monthly_savings'],
            'initial_cost': data['initial_cost']
        }