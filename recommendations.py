import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RecommendationEngine:
    def __init__(self, df):
        self.df = df
        self.recommendations = []
        
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
        avg_computer = self.df['computer_consumption'].mean()
        avg_projector = self.df['projector_consumption'].mean()
        
        equipment_recommendations = {
            'category': 'Equipment Usage',
            'findings': "Analysis of equipment consumption patterns",
            'recommendations': []
        }
        
        if avg_computer > 500:  # Threshold can be adjusted
            equipment_recommendations['recommendations'].append(
                "Configure computers to enter sleep mode after 15 minutes of inactivity"
            )
            
        if avg_projector > 300:  # Threshold can be adjusted
            equipment_recommendations['recommendations'].append(
                "Install motion sensors for projectors to auto-shutdown when rooms are empty"
            )
            
        if len(equipment_recommendations['recommendations']) > 0:
            self.recommendations.append(equipment_recommendations)
    
    def _analyze_occupancy_patterns(self):
        """Analyze and recommend based on occupancy patterns"""
        avg_consumption_per_occupant = (
            self.df['total_consumption'] / self.df['occupancy_level']
        ).mean()
        
        if avg_consumption_per_occupant > 50:  # Threshold can be adjusted
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
        """Generate cost-based recommendations"""
        total_consumption = self.df['total_consumption'].sum()
        avg_daily_consumption = self.df.groupby(pd.to_datetime(self.df['timestamp']).dt.date)['total_consumption'].mean().mean()
        
        # Assume average electricity rate of $0.12 per kWh
        daily_cost = (avg_daily_consumption * 0.12) / 1000
        
        recommendation = {
            'category': 'Cost Optimization',
            'findings': f"Average daily energy cost: ${daily_cost:.2f}",
            'recommendations': [
                "Negotiate better electricity rates during off-peak hours",
                "Consider solar panel installation for long-term savings",
                "Implement real-time energy monitoring and alerts",
                "Train staff on energy-efficient practices"
            ],
            'potential_savings': f"${(daily_cost * 0.2 * 30):.2f} per month through optimizations"
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