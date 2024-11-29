##NOTE this is a working prototype 1 we have more to implement and work on but this is a good START. 


import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from recommendations import RecommendationEngine
from dashboard import DashboardComponents
import os
import json
import plotly.graph_objects as go

def initialize_session_state():
    """Initialize session state variables"""
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = True
    if 'name' not in st.session_state:
        st.session_state.name = "Test User"
    if 'username' not in st.session_state:
        st.session_state.username = "test_user"
    if 'selected_date_range' not in st.session_state:
        st.session_state.selected_date_range = '1W'  # Default to 1 week

@st.cache_data
def load_data():
    """Load and cache multiple JSON files from energy_data folder"""
    try:
        data_folder = 'synthetic_data'
        if not os.path.exists(data_folder):
            st.error(f"Data folder '{data_folder}' not found!")
            return pd.DataFrame()

        json_files = [f for f in os.listdir(data_folder) 
                     if f.startswith('data_') and f.endswith('.json')]
        
        if not json_files:
            st.warning("No energy data files found!")
            return pd.DataFrame()

        all_data = []
        for file in json_files:
            try:
                file_path = os.path.join(data_folder, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    all_data.append(pd.json_normalize(data))
            except Exception as e:
                st.error(f"Error loading {file}: {str(e)}")
                continue
        
        df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def filter_data(df, date_range):
    """Filter data based on selected date range"""
    end_date = df['timestamp'].max()
    if date_range == '1W':
        start_date = end_date - timedelta(days=7)
    elif date_range == '1M':
        start_date = end_date - timedelta(days=30)
    elif date_range == '3M':
        start_date = end_date - timedelta(days=90)
    else:  # All time
        return df
    
    return df[df['timestamp'].between(start_date, end_date)]

def display_overview(dashboard, metrics):
    """Display overview page components"""
    st.title("Energy Management Dashboard")
    
    # Date range selector
    date_range = st.sidebar.selectbox(
        "Select Time Range",
        options=['1W', '1M', '3M', 'All'],
        index=['1W', '1M', '3M', 'All'].index(st.session_state.selected_date_range)
    )
    if date_range != st.session_state.selected_date_range:
        st.session_state.selected_date_range = date_range
        st.experimental_rerun()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Consumption", f"{metrics['total_consumption']/1000:.2f} kWh")
    with col2:
        st.metric("Daily Average", f"{metrics['avg_daily_consumption']/1000:.2f} kWh")
    with col3:
        st.metric("Total Cost", f"₹{metrics['total_cost']:.2f}")
    with col4:
        st.metric("Avg Occupancy", f"{metrics['avg_occupancy']:.1f}%")

    # Consumption Timeline
    st.subheader("Energy Consumption Over Time")
    timeline_fig = dashboard.create_consumption_timeline()
    st.plotly_chart(timeline_fig, use_container_width=True)

    # Two-column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Hourly Consumption Patterns")
        heatmap_fig = dashboard.create_heatmap()
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        st.subheader("Floor-wise Consumption")
        floor_fig = dashboard.create_floor_comparison()
        st.plotly_chart(floor_fig, use_container_width=True)

    with col2:
        st.subheader("Equipment Breakdown")
        equipment_data = {
            'HVAC': 45,
            'Lighting': 25,
            'Equipment': 20,
            'Others': 10
        }
        equipment_fig = dashboard.create_equipment_breakdown(equipment_data)
        st.plotly_chart(equipment_fig, use_container_width=True)
        
        st.subheader("Occupancy vs Consumption")
        occupancy_fig = dashboard.create_occupancy_correlation()
        st.plotly_chart(occupancy_fig, use_container_width=True)

def display_detailed_analysis(dashboard):
    """Display detailed analysis page with time frame selection"""
    st.title("Detailed Energy Analysis")
    
    # Sidebar Time Frame Selector
    st.sidebar.subheader("Select Time Frame")
    time_frame = st.sidebar.selectbox("Time Frame", ["Daily", "Weekly", "Monthly", "Yearly"])

    # Energy Efficiency Score and Consumption Prediction
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Energy Efficiency Score")
        score, metrics = dashboard.calculate_efficiency_score()  # Calculate real score
        efficiency_fig = dashboard.create_efficiency_gauge(score)
        st.plotly_chart(efficiency_fig, use_container_width=True)
        
        # Add metrics breakdown in an expander
        with st.expander("View Efficiency Metrics Breakdown"):
            dashboard.display_efficiency_metrics(metrics)
            
        # Add recommendations in an expander
        with st.expander("View Optimization Recommendations"):
            recommendations = dashboard.create_optimization_recommendations(metrics)
            for rec in recommendations:
                st.markdown(f"**{rec['category']} - {rec['priority']} Priority**")
                st.write(rec['suggestion'])
                st.markdown("---")
    
    with col2:
        st.subheader("Consumption Prediction")
        # Sample data for prediction plot
        dates = dashboard.df['timestamp'].tail(30)
        actual = dashboard.df['total_consumption'].tail(30)
        predicted = actual * 1.1  # Example prediction data
        prediction_fig = dashboard.create_prediction_plot(actual, predicted, dates)
        st.plotly_chart(prediction_fig, use_container_width=True)

    # Additional Visualizations Based on Selected Time Frame
    st.subheader("Energy Consumption Over Time")
    consumption_trend_fig = dashboard.plot_consumption_trend(time_frame=time_frame)
    st.plotly_chart(consumption_trend_fig, use_container_width=True)

    st.subheader("Peak Consumption Times")
    peak_consumption_fig = dashboard.plot_peak_consumption(time_frame=time_frame)
    st.plotly_chart(peak_consumption_fig, use_container_width=True)

    st.subheader("Monthly Trends") #Placeholder until we decide how to handle seasonal trend
    seasonal_trend_fig = dashboard.plot_monthly_trend(time_frame=time_frame)
    st.plotly_chart(seasonal_trend_fig, use_container_width=True)


def display_recommendations(dashboard, recommendations):
    """Display recommendations page with implementation tracking and reminders"""
    st.title("Energy Saving Recommendations")
    recommendations.generate_recommendations()
    formatted_recs = recommendations.display_recommendations()
    
    if isinstance(formatted_recs, str):
        st.warning(formatted_recs)
    else:
        # Add filters
        st.sidebar.subheader("Filter Recommendations")
        priority_filter = st.sidebar.multiselect(
            "Priority Level",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
        
        # Display recommendations with metrics
        total_savings = 0
        implementation_cost = 0
        
        for rec in formatted_recs:
            rec_id = hash(rec[:50])  # Create unique ID for each recommendation
            
            with st.expander(f"💡 {rec.split('###')[1].split('(')[0].strip()}", 
                            expanded=rec_id not in st.session_state.implemented_recommendations):
                cols = st.columns([2, 1])
                
                with cols[0]:
                    if rec_id in st.session_state.implemented_recommendations:
                        st.success("✅ Implemented")
                    st.markdown(rec)
                
                with cols[1]:
                    # Implementation tracking
                    if st.button("Mark as Implemented", key=f"impl_{rec_id}"):
                        st.session_state.implemented_recommendations.add(rec_id)
                        st.experimental_rerun()
                    
                    # Reminder setting
                    reminder_date = st.date_input(
                        "Set Reminder Date",
                        value=None,
                        key=f"date_{rec_id}"
                    )
                    if st.button("Set Reminder", key=f"rem_{rec_id}"):
                        if reminder_date:
                            st.session_state.recommendation_reminders[rec_id] = {
                                'date': reminder_date,
                                'title': rec.split('###')[1].split('(')[0].strip(),
                                'status': 'pending'
                            }
                            st.success(f"Reminder set for {reminder_date}")
                    
                    # Show existing reminder
                    if rec_id in st.session_state.recommendation_reminders:
                        reminder = st.session_state.recommendation_reminders[rec_id]
                        st.info(f"⏰ Reminder set for {reminder['date']}")
                    
                    # Implementation progress
                    if rec_id in st.session_state.implemented_recommendations:
                        progress = 1.0
                    elif rec_id in st.session_state.recommendation_reminders:
                        progress = 0.5
                    else:
                        progress = 0.0
                    st.progress(progress)

        # Add summary metrics
        st.sidebar.metric("Potential Monthly Savings", "₹25,000")
        st.sidebar.metric("Implementation Cost", "₹50,000")
        st.sidebar.metric("ROI Period", "2 months")

def display_cost_analysis(dashboard):
    st.title("Cost Analysis")
    
    # First, let's ensure we have the correct timestamp format from synthetic data
    dashboard.df['timestamp'] = pd.to_datetime(dashboard.df['timestamp'])
    
    # Get the actual date range from our data
    min_date = dashboard.df['timestamp'].min()
    max_date = dashboard.df['timestamp'].max()
    
    # Time period selector
    col1, col2 = st.columns([2, 1])
    with col1:
        analysis_period = st.selectbox(
            "Analysis Period",
            ["All Data", "Last Month", "Last Quarter", "Last Year", "Custom Range"],
            key="cost_analysis_period"
        )
    
    # Calculate date range based on selection
    if analysis_period == "All Data":
        filtered_df = dashboard.df.copy()
        start_date = min_date
        end_date = max_date
    else:
        end_date = max_date
        if analysis_period == "Last Month":
            start_date = end_date - pd.Timedelta(days=30)
        elif analysis_period == "Last Quarter":
            start_date = end_date - pd.Timedelta(days=90)
        elif analysis_period == "Last Year":
            start_date = end_date - pd.Timedelta(days=365)
        elif analysis_period == "Custom Range":
            with col2:
                dates = st.date_input(
                    "Select Date Range",
                    value=(min_date.date(), max_date.date()),
                    min_value=min_date.date(),
                    max_value=max_date.date(),
                    key="custom_date_range"
                )
                if isinstance(dates, tuple):
                    start_date = pd.Timestamp(dates[0])
                    end_date = pd.Timestamp(dates[1])
                else:
                    start_date = min_date
                    end_date = max_date
        
        # Filter data based on selected date range
        filtered_df = dashboard.df[
            (dashboard.df['timestamp'] >= start_date) & 
            (dashboard.df['timestamp'] <= end_date)
        ].copy()

    if filtered_df.empty:
        st.warning("No data available for the selected time period.")
        return
        
    # Debug information
    st.write(f"Data range: from {min_date} to {max_date}")
    st.write(f"Selected range: from {start_date} to {end_date}")
    st.write(f"Number of records: {len(filtered_df)}")

    # Rest of the code remains the same...
    # Calculate basic metrics
    total_consumption = filtered_df['total_consumption'].sum() / 1000  # Convert to kWh
    days_in_period = (end_date - start_date).days or 1
    
    # Calculate peak and off-peak consumption
    filtered_df['hour'] = filtered_df['timestamp'].dt.hour
    peak_mask = (filtered_df['hour'] >= 9) & (filtered_df['hour'] < 18)
    peak_consumption = filtered_df[peak_mask]['total_consumption'].sum() / 1000
    off_peak_consumption = filtered_df[~peak_mask]['total_consumption'].sum() / 1000
    
    # Calculate costs
    peak_rate = 8  # ₹8 per kWh during peak hours
    off_peak_rate = 6  # ₹6 per kWh during off-peak hours
    
    peak_cost = peak_consumption * peak_rate
    off_peak_cost = off_peak_consumption * off_peak_rate
    total_cost = peak_cost + off_peak_cost
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Consumption",
            f"{total_consumption:.2f} kWh",
            help="Total energy consumption for the period"
        )
    with col2:
        st.metric(
            "Total Cost",
            f"₹{total_cost:,.2f}",
            help="Total cost including peak and off-peak rates"
        )
    with col3:
        st.metric(
            "Peak Hours Cost",
            f"₹{peak_cost:,.2f}",
            help="Cost during peak hours (9 AM - 6 PM)"
        )
    with col4:
        st.metric(
            "Average Daily Cost",
            f"₹{total_cost/days_in_period:,.2f}",
            help="Average cost per day"
        )

    # Detailed Analysis Tabs
    tabs = st.tabs(["Cost Breakdown", "Usage Analysis", "Efficiency Metrics"])
    
    with tabs[0]:
        st.subheader("Cost Breakdown Analysis")
        
        # Floor-wise breakdown
        floor_costs = {}
        for _, row in filtered_df.iterrows():
            hour = row['timestamp'].hour
            rate = peak_rate if 9 <= hour < 18 else off_peak_rate
            
            for floor_data in row['floor_data']:
                floor_name = floor_data['floor']
                if floor_name not in floor_costs:
                    floor_costs[floor_name] = {
                        'consumption': 0,
                        'peak_consumption': 0,
                        'off_peak_consumption': 0,
                        'total_cost': 0
                    }
                
                consumption = floor_data['total_floor_consumption'] / 1000  # Convert to kWh
                floor_costs[floor_name]['consumption'] += consumption
                
                if 9 <= hour < 18:
                    floor_costs[floor_name]['peak_consumption'] += consumption
                else:
                    floor_costs[floor_name]['off_peak_consumption'] += consumption
                
                floor_costs[floor_name]['total_cost'] += consumption * rate
        
        # Create DataFrame for floor-wise costs
        floor_df = pd.DataFrame([
            {
                'Floor': floor,
                'Total Consumption (kWh)': data['consumption'],
                'Peak Consumption (kWh)': data['peak_consumption'],
                'Off-Peak Consumption (kWh)': data['off_peak_consumption'],
                'Total Cost (₹)': data['total_cost']
            }
            for floor, data in floor_costs.items()
        ])
        
        if not floor_df.empty:
            st.dataframe(floor_df.set_index('Floor'), use_container_width=True)
            
            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Peak Cost',
                x=floor_df['Floor'],
                y=floor_df['Peak Consumption (kWh)'] * peak_rate,
                marker_color='#FF9B9B'
            ))
            fig.add_trace(go.Bar(
                name='Off-Peak Cost',
                x=floor_df['Floor'],
                y=floor_df['Off-Peak Consumption (kWh)'] * off_peak_rate,
                marker_color='#9CC5FF'
            ))
            
            fig.update_layout(
                title='Floor-wise Cost Distribution',
                barmode='stack',
                xaxis_title='Floor',
                yaxis_title='Cost (₹)',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.subheader("Usage Pattern Analysis")
        
        # Hourly consumption pattern
        hourly_consumption = filtered_df.groupby('hour')['total_consumption'].mean() / 1000
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_consumption.index,
            y=hourly_consumption.values,
            mode='lines+markers',
            name='Average Consumption',
            line=dict(color='#2E86C1', width=2),
            marker=dict(size=8)
        ))
        
        # Add peak hour highlighting
        fig.add_vrect(
            x0=9, x1=18,
            fillcolor="rgba(255, 0, 0, 0.1)",
            layer="below",
            line_width=0,
            annotation_text="Peak Hours",
            annotation_position="top left"
        )
        
        fig.update_layout(
            title='Average Hourly Consumption Pattern',
            xaxis_title='Hour of Day',
            yaxis_title='Average Consumption (kWh)',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        st.subheader("Efficiency Metrics")
        
        # Calculate efficiency metrics
        avg_daily_consumption = total_consumption / days_in_period
        peak_ratio = peak_consumption / total_consumption if total_consumption > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Average Daily Consumption",
                f"{avg_daily_consumption:.2f} kWh",
                help="Average consumption per day"
            )
        with col2:
            st.metric(
                "Peak Usage Ratio",
                f"{peak_ratio:.1%}",
                help="Proportion of consumption during peak hours"
            )
        with col3:
            cost_per_kwh = total_cost / total_consumption if total_consumption > 0 else 0
            st.metric(
                "Average Cost per kWh",
                f"₹{cost_per_kwh:.2f}",
                help="Average cost per kilowatt-hour"
            )

def main():
    st.set_page_config(
        page_title="Energy Management Dashboard",
        page_icon="⚡",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    st.sidebar.write(f"Welcome, {st.session_state.name}!")
    
    # Role-based page access
    user_role = 'admin'  # Default role for testing
    available_pages = {
        "admin": ["Overview", "Detailed Analysis", "Recommendations", "Cost Analysis"],
        "manager": ["Overview", "Detailed Analysis", "Recommendations"],
        "user": ["Overview", "Recommendations"]
    }
    
    page = st.sidebar.radio("Select Page", available_pages.get(user_role, ["Overview"]))

    # Load and filter data
    df = load_data()
    if df.empty:
        st.error("No data available. Please check the data source.")
        return

    filtered_df = filter_data(df, st.session_state.selected_date_range)
    dashboard = DashboardComponents(filtered_df)
    recommendations = RecommendationEngine(filtered_df)
    
    # Page routing
    if page == "Overview":
        display_overview(dashboard, dashboard.get_summary_metrics())
    
    elif page == "Detailed Analysis":
        display_detailed_analysis(dashboard)
    
    elif page == "Recommendations":
        display_recommendations(dashboard, recommendations)
    
    elif page == "Cost Analysis":
        display_cost_analysis(dashboard)

if __name__ == "__main__":
    main()