"""
KPI card components for displaying metrics.
All currency in Rubles (₽).
"""
import streamlit as st
import pandas as pd

def display_kpi_metrics(kpi_data):
    """Display main KPI metric cards in 4-column layout."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"₽{kpi_data['total_revenue'].iloc[0]:,.0f}",
            f"{kpi_data['revenue_growth_mom_pct'].iloc[0]:.1f}%" 
            if pd.notna(kpi_data['revenue_growth_mom_pct'].iloc[0]) else "N/A"
        )
    
    with col2:
        st.metric(
            "Total Orders",
            f"{kpi_data['total_orders'].iloc[0]:,}",
            f"{kpi_data['orders_growth_mom_pct'].iloc[0]:.1f}%" 
            if pd.notna(kpi_data['orders_growth_mom_pct'].iloc[0]) else "N/A"
        )
    
    with col3:
        st.metric(
            "Active Customers",
            f"{kpi_data['active_customers'].iloc[0]}"
        )
    
    with col4:
        st.metric(
            "Active Products",
            f"{kpi_data['active_products'].iloc[0]}"
        )

def display_summary_stats(data):
    """Display summary statistics in info cards."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Average Monthly Revenue**  
        ₽{data['total_revenue'].mean():,.0f}
        """)
    
    with col2:
        if not data.empty:
            best_month = data.loc[data['total_revenue'].idxmax(), 'month_label_display']
            st.info(f"""
            **Best Month**  
            {best_month}
            """)
    
    with col3:
        st.info(f"""
        **Total Revenue (All Time)**  
        ₽{data['total_revenue'].sum():,.0f}
        """)
