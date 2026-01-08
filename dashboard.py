import streamlit as st
import pandas as pd
import sqlite3
import time
import plotly.express as px

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Net-Sentry Dashboard", layout="wide")
st.title("🛡️ Net-Sentry: Network Observability")

# 2. DATABASE CONNECTION
def load_data():
    """
    Connects to the SQLite database and loads the latest data.
    """
    conn = sqlite3.connect("network_data.db")
    df = pd.read_sql_query("SELECT * FROM devices", conn)
    conn.close()
    return df

# 3. AUTO-REFRESH LOOP
# We create a placeholder. This is an empty box we will fill and empty repeatedly.
placeholder = st.empty()

while True:
    # Fetch latest data from the "Brain"
    df = load_data()
    
    with placeholder.container():
        # --- TOP METRICS ---
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Metric 1: Total Devices Found
        kpi1.metric(label="Total Devices", value=len(df))
        
        # Metric 2: Active System Status
        kpi2.metric(label="System Status", value="Online 🟢")
        
        # Metric 3: Last Scan Time (Just using current time for display)
        kpi3.metric(label="Last Refresh", value=time.strftime("%H:%M:%S"))
        
        # --- DATA TABLE ---
        st.markdown("### 📡 Live Device Inventory")
        st.dataframe(df, use_container_width=True)
        
        # --- CHART ---
        if not df.empty:
            st.markdown("### 📊 Network Composition")
            # A simple chart showing devices
            fig = px.scatter(df, x="ip", y="status", title="Device Connectivity Map", color="status")
            # We add a unique 'key' using the current time so Streamlit knows it's a new update
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")
            
        # Wait 5 seconds before reloading the page automatically
        time.sleep(5)