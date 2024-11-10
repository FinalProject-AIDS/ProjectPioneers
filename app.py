##NOTE this is a working prototype 1 we have more to implement and work on but this is a good START. 


import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from recommendations import RecommendationEngine
from dashboard import DashboardComponents
import os
import json

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
        st.metric("Total Cost", f"${metrics['total_cost']:.2f}")
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
        efficiency_score = 75  # Placeholder; calculate based on metrics as needed
        efficiency_fig = dashboard.create_efficiency_gauge(efficiency_score)
        st.plotly_chart(efficiency_fig, use_container_width=True)
    
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
        st.title("Energy Saving Recommendations")
        recommendations.display_recommendations()
    
    elif page == "Cost Analysis":
        st.title("Cost Analysis")
        dashboard.display_cost_analysis()

if __name__ == "__main__":
    main()