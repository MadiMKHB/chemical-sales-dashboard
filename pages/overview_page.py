"""
Overview page showing KPIs and trends.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_kpi_data
from components.kpi_cards import display_kpi_metrics, display_summary_stats
from components.charts import create_revenue_trend_chart

def render_overview_page():
    """Render the complete overview/KPI page."""
    st.header("Key Performance Indicators")
    
    # Load all KPI data
    all_kpi_df = load_kpi_data()
    
    if all_kpi_df is not None and not all_kpi_df.empty:
        # Create readable month labels
        all_kpi_df['month_label_display'] = pd.to_datetime(
            all_kpi_df['report_month']
        ).dt.strftime('%B %Y')
        
        # Month selector
        col1, col2, col3 = st.columns([2, 3, 3])
        with col1:
            selected_month = st.selectbox(
                "Select Month:",
                options=all_kpi_df['month_label_display'].tolist(),
                index=0  # Default to most recent month
            )
        
        # Filter data for selected month
        kpi_df = all_kpi_df[all_kpi_df['month_label_display'] == selected_month]
        
        # Display KPI metrics
        st.markdown("---")
        display_kpi_metrics(kpi_df)
        
        # Revenue trend chart
        st.markdown("---")
        st.subheader("Revenue Trend")
        fig = create_revenue_trend_chart(all_kpi_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        display_summary_stats(all_kpi_df)
    else:
        st.error("No data available. Please check your BigQuery connection.")
