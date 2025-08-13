import pandas as pd
from utils.database import run_query

def load_kpi_data():
    """
    Load KPI summary data for all months.
    
    This function:
    - Fetches KPI metrics from the kpi_summary table
    - Filters out months with zero revenue (no data)
    - Orders by most recent month first
    - Used for: Overview page metrics and month selector
    
    Returns:
        DataFrame with columns: report_month, total_revenue, total_orders, 
        active_customers, active_products, growth percentages
    """
    query = """
    SELECT *
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.kpi_summary`
    WHERE total_revenue > 0
    ORDER BY report_month DESC
    """
    return run_query(query)

def load_customer_analytics():
    """
    Load customer 360-degree view data.
    
    This function:
    - Fetches customer analytics from customer_analytics table
    - Includes customer segments, revenue, growth status, churn risk
    - Orders by highest revenue customers first
    - Used for: Customer analytics page
    
    Returns:
        DataFrame with customer metrics and segments
    """
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

def load_product_analytics():
    """
    Load product performance data.
    
    This function:
    - Fetches top 20 products by revenue
    - Includes rankings, trends, and product types
    - Used for: Product analytics page
    
    Returns:
        DataFrame with product performance metrics
    """
    query = """
    SELECT 
        product_code,
        product_name,
        product_type,
        total_revenue_all_time,
        rank_by_revenue,
        trend_direction
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.product_analytics`
    ORDER BY rank_by_revenue
    LIMIT 20
    """
    return run_query(query)

def load_monthly_sales():
    """
    Load monthly sales summary for trend analysis.
    
    This function:
    - Fetches aggregated monthly sales data
    - Includes customer counts, product counts, revenue totals
    - Used for: Trend charts and historical analysis
    
    Returns:
        DataFrame with monthly aggregated metrics
    """
    query = """
    SELECT *
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.monthly_sales_summary`
    ORDER BY month DESC
    """
    return run_query(query)

def load_predictions_from_gcs(month="2025_07"):
    """
    Load prediction data from Cloud Storage CSV files.
    
    This function:
    - Reads prediction CSV from GCS bucket
    - Handles missing files gracefully
    - Used for: Prediction graphs (orange historical + blue forecast)
    
    Args:
        month (str): Month identifier like "2025_07"
        
    Returns:
        DataFrame with predictions or None if file not found
    """
    # Implementation for GCS reading would go here
    # For now, returning placeholder
    return None
