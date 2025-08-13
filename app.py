import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import json

# Page config
st.set_page_config(
    page_title="Chemical Sales Dashboard",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Chemical Sales Dashboard")

# Create connection to BigQuery
@st.cache_resource
def init_connection():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)
        return client
    except Exception as e:
        st.error(f"Failed to connect to BigQuery: {e}")
        return None

# Load KPI data
@st.cache_data(ttl=600)
def load_kpi_data():
    client = init_connection()
    if client:
        query = """
        SELECT *
        FROM `ml-goldman-hotels-vit-vertex.sales_analytics.kpi_summary`
        ORDER BY report_month DESC
        LIMIT 1
        """
        df = client.query(query).to_dataframe()
        return df
    return pd.DataFrame()

# Main app
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Predictions", "👥 Customers"])

with tab1:
    st.header("Key Performance Indicators")
    
    # Load data
    kpi_df = load_kpi_data()
    
    if not kpi_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${kpi_df['total_revenue'].iloc[0]:,.0f}",
                f"{kpi_df['revenue_growth_mom_pct'].iloc[0]:.1f}%"
            )
        
        with col2:
            st.metric(
                "Total Orders",
                f"{kpi_df['total_orders'].iloc[0]:,}",
                f"{kpi_df['orders_growth_mom_pct'].iloc[0]:.1f}%"
            )
        
        with col3:
            st.metric(
                "Active Customers",
                f"{kpi_df['active_customers'].iloc[0]}"
            )
        
        with col4:
            st.metric(
                "Active Products",
                f"{kpi_df['active_products'].iloc[0]}"
            )
    else:
        st.info("Connect to BigQuery to see real data")

with tab2:
    st.header("Sales Predictions")
    st.info("Prediction graph coming soon...")

with tab3:
    st.header("Customer Analytics")
    st.info("Customer details coming soon...")
