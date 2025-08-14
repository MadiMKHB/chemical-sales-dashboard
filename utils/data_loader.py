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

"""
Add these functions to utils/data_loader.py
"""

def load_customer_product_combinations():
    """Load unique customer-product combinations with product names."""
    query = """
    SELECT DISTINCT 
        Customer_ID,
        Product_code,
        Product_name
    FROM `ml-goldman-hotels-vit-vertex.sales_forecasting.features_history`
    WHERE Quantity_sold > 0
    ORDER BY Customer_ID, Product_code
    """
    return run_query(query)

def load_historical_for_customer_product(customer_id, product_code):
    """Load historical data for specific customer-product combination."""
    query = f"""
    SELECT 
        date,
        Customer_ID,
        Product_code,
        Product_name,
        Quantity_sold
    FROM `ml-goldman-hotels-vit-vertex.sales_forecasting.features_history`
    WHERE Customer_ID = '{customer_id}'
      AND Product_code = '{product_code}'
      AND Quantity_sold >= 0
    ORDER BY date
    """
    return run_query(query)

def get_customers_with_products():
    """Get customers and their purchased products for dropdowns."""
    query = """
    SELECT 
        Customer_ID,
        COUNT(DISTINCT Product_code) as product_count,
        SUM(Quantity_sold) as total_quantity
    FROM `ml-goldman-hotels-vit-vertex.sales_forecasting.features_history`
    WHERE Quantity_sold > 0
    GROUP BY Customer_ID
    HAVING product_count > 0
    ORDER BY total_quantity DESC
    """
    return run_query(query)
