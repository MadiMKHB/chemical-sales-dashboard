import streamlit as st
import pandas as pd

def display_kpi_metrics(kpi_data):
    """
    Display main KPI metric cards in a 4-column layout.
    
    This component:
    - Shows Revenue, Orders, Customers, Products in metric cards
    - Includes growth percentages with color indicators (green=up, red=down)
    - Handles missing data by showing "N/A"
    - Auto-formats numbers with commas and currency symbols
    
    Args:
        kpi_data (DataFrame): Single row of KPI data for selected month
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${kpi_data['total_revenue'].iloc[0]:,.0f}",
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
    """
    Display summary statistics in info cards.
    
    This component:
    - Shows 3 summary cards: Average, Best Month, Total
    - Calculates statistics across all available months
    - Uses blue info boxes for visual distinction
    - Auto-formats large numbers for readability
    
    Args:
        data (DataFrame): All months of KPI data for calculations
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Average Monthly Revenue**  
        ${data['total_revenue'].mean():,.0f}
        """)
    
    with col2:
        best_month = data.loc[data['total_revenue'].idxmax(), 'month_label_display']
        st.info(f"""
        **Best Month**  
        {best_month}
        """)
    
    with col3:
        st.info(f"""
        **Total Revenue (All Time)**  
        ${data['total_revenue'].sum():,.0f}
        """)

def display_customer_metrics(customer_data):
    """
    Display individual customer metrics.
    
    This component:
    - Shows 4 metrics for a selected customer
    - Uses emoji indicators for status (🟢 good, 🟡 warning, 🔴 danger)
    - Formats revenue with currency
    - Shows growth and risk indicators
    
    Args:
        customer_data (Series): Single customer's data row
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Lifetime Revenue", 
            f"${customer_data['total_lifetime_revenue']:,.0f}"
        )
    
    with col2:
        st.metric(
            "Last 3 Months", 
            f"${customer_data['revenue_last_3_months']:,.0f}"
        )
    
    with col3:
        # Color code based on growth status
        if customer_data['growth_status'] == 'Growing':
            status_color = "🟢"
        elif customer_data['growth_status'] == 'Stable':
            status_color = "🟡"
        else:
            status_color = "🔴"
        st.metric("Growth Status", f"{status_color} {customer_data['growth_status']}")
    
    with col4:
        # Color code based on risk level
        if "High" in str(customer_data['churn_risk']):
            risk_color = "🔴"
        elif "Medium" in str(customer_data['churn_risk']):
            risk_color = "🟡"
        else:
            risk_color = "🟢"
        st.metric("Churn Risk", f"{risk_color} {customer_data['churn_risk']}")
