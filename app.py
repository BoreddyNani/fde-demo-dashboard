import streamlit as st
import pandas as pd
import plotly.express as px

# --- Config ---
st.set_page_config(page_title="Supply Chain Control Tower", layout="wide", page_icon="📦")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('shipments.csv', parse_dates=['scheduled_date', 'actual_date'])
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Date Range Filter
min_date = df['scheduled_date'].min().date()
max_date = df['scheduled_date'].max().date()
date_range = st.sidebar.date_input("Scheduled Date Range", [min_date, max_date])

# Status Filter
all_statuses = df['status'].unique()
selected_statuses = st.sidebar.multiselect("Status", all_statuses, default=all_statuses)

# Origin Filter
all_origins = df['origin'].unique()
selected_origins = st.sidebar.multiselect("Origin City", all_origins, default=all_origins)

# Apply Filters
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (
        (df['scheduled_date'].dt.date >= start_date) & 
        (df['scheduled_date'].dt.date <= end_date) &
        (df['status'].isin(selected_statuses)) &
        (df['origin'].isin(selected_origins))
    )
    filtered_df = df[mask]
else:
    filtered_df = df

# --- Main App ---
st.title("📦 Supply Chain Control Tower")

# --- Metrics Calculations ---
total_shipments = len(filtered_df)

# On-Time Rate
delivered_df = filtered_df[filtered_df['status'] == 'DELIVERED']
if not delivered_df.empty:
    on_time_df = delivered_df[delivered_df['actual_date'] <= delivered_df['scheduled_date']]
    on_time_rate = (len(on_time_df) / len(delivered_df)) * 100
else:
    on_time_rate = 0.0

# Avg Delay Days
delayed_df = filtered_df[filtered_df['status'] == 'DELAYED']
if not delayed_df.empty:
    avg_delay = (delayed_df['actual_date'] - delayed_df['scheduled_date']).dt.days.mean()
else:
    avg_delay = 0.0

# Render Metric Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Shipments", f"{total_shipments:,}")
col2.metric("On-Time Rate (Delivered)", f"{on_time_rate:.1f}%")
col3.metric("Avg Delay (Days)", f"{avg_delay:.1f}")

st.markdown("---")

# --- Visuals & Data Table ---
chart_col, table_col = st.columns([1, 1.5])

with chart_col:
    st.subheader("Volume by Status")
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig = px.bar(
        status_counts, x='Status', y='Count', 
        color='Status',
        color_discrete_map={
            'DELIVERED': '#00C851', 'IN_TRANSIT': '#33b5e5', 
            'PENDING': '#ffbb33', 'DELAYED': '#ff4444'
        }
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Number of Shipments")
    st.plotly_chart(fig, use_container_width=True)

with table_col:
    st.subheader("Shipment Ledger")
    
    # Pandas Styling Function for the Status Column
    def color_status(val):
        colors = {
            'DELIVERED': 'color: #00C851; font-weight: bold',
            'DELAYED': 'color: #ff4444; font-weight: bold',
            'IN_TRANSIT': 'color: #33b5e5; font-weight: bold',
            'PENDING': 'color: #ffbb33; font-weight: bold'
        }
        return colors.get(val, '')

    # Apply styling using .map (modern pandas)
    styled_df = filtered_df.style.map(color_status, subset=['status']).format(
        {'weight_lbs': "{:,.2f}", 'scheduled_date': lambda t: t.strftime("%Y-%m-%d")}
    )
    
    st.dataframe(styled_df, width='stretch', hide_index=True, height=400)
