"""Data loading functions for all analytics tables."""
import pandas as pd
from utils.database import run_query

def load_kpi_data():
    """Load KPI summary data for all months."""
    query = """
    SELECT *
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.kpi_summary`
    WHERE total_revenue > 0
    ORDER BY report_month DESC
    """
    return run_query(query)

def load_customer_analytics():
    """Load customer analytics data."""
    query = """
    SELECT 
        customer_id,
        customer_segment,
        total_lifetime_revenue,
        revenue_last_3_months,
        growth_status,
        favorite_product_1_name,
        churn_risk
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.customer_analytics`
    ORDER BY total_lifetime_revenue DESC
    """
    return run_query(query)
