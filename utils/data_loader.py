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

def load_product_analytics_existing():
    """Load product analytics data from your existing table structure."""
    query = """
    SELECT 
        product_code,
        product_name,
        product_type,
        current_unit_price,
        total_quantity_all_time,
        total_revenue_all_time,
        unique_customers_all_time,
        avg_monthly_quantity,
        avg_monthly_revenue,
        rank_by_revenue,
        rank_by_quantity,
        rank_in_category,
        percentile_rank,
        customer_penetration_pct,
        avg_quantity_per_customer,
        quantity_last_3mo,
        revenue_last_3mo,
        quantity_previous_3mo,
        quantity_growth_pct,
        revenue_growth_pct,
        trend_direction,
        coefficient_of_variation,
        demand_stability,
        peak_month,
        top_customer_1,
        top_customer_1_qty,
        top_customer_2,
        top_customer_2_qty
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.product_analytics`
    ORDER BY total_revenue_all_time DESC
    """
    return run_query(query)

def load_product_historical_monthly(product_code):
    """
    Load monthly aggregated historical data for a specific product.
    This creates the orange line in the product performance graph.
    """
    query = f"""
    SELECT 
        DATE_TRUNC(date, MONTH) as month,
        Product_code,
        ANY_VALUE(Product_name) as product_name,
        SUM(Quantity_sold) as total_quantity,
        SUM(Quantity_sold * unit_price) as total_revenue,
        COUNT(DISTINCT Customer_ID) as customer_count,
        COUNT(*) as transaction_count
    FROM `ml-goldman-hotels-vit-vertex.sales_forecasting.features_history`
    WHERE Product_code = '{product_code}'
      AND Quantity_sold >= 0
    GROUP BY DATE_TRUNC(date, MONTH), Product_code
    ORDER BY month
    """
    return run_query(query)

def load_multiple_products_historical(product_codes, months_back=12):
    """
    Load historical data for multiple products for comparison.
    Used in the Product Comparison tab.
    """
    if not product_codes:
        return None
    
    # Create safe product list for SQL
    product_list = "', '".join(product_codes)
    
    query = f"""
    SELECT 
        DATE_TRUNC(date, MONTH) as month,
        Product_code,
        ANY_VALUE(Product_name) as product_name,
        SUM(Quantity_sold) as total_quantity,
        SUM(Quantity_sold * unit_price) as total_revenue,
        COUNT(DISTINCT Customer_ID) as customer_count
    FROM `ml-goldman-hotels-vit-vertex.sales_forecasting.features_history`
    WHERE Product_code IN ('{product_list}')
      AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL {months_back} MONTH)
      AND Quantity_sold >= 0
    GROUP BY DATE_TRUNC(date, MONTH), Product_code
    ORDER BY month, Product_code
    """
    return run_query(query)

def load_product_prediction_aggregated_fixed(product_code, prediction_month):
    """
    Load aggregated prediction for a specific product from Cloud Storage CSV.
    Sums all customer predictions for this product to get total market demand.
    """
    from utils.cloud_storage import load_predictions_from_gcs
    
    predictions_df = load_predictions_from_gcs(prediction_month)
    
    if predictions_df.empty:
        return None
    
    # Debug: Check what columns we actually have
    print(f"Available columns in predictions CSV: {list(predictions_df.columns)}")
    
    # Try different possible column name combinations
    customer_cols = ['Customer_ID', 'customer_id', 'Customer', 'customer']
    product_cols = ['Product_code', 'product_code', 'Product', 'product']
    pred_cols = ['predicted_quantity', 'prediction', 'forecast', 'quantity_predicted', 'Predicted_Quantity']
    
    customer_col = None
    product_col = None
    pred_col = None
    
    # Find matching column names
    for col in customer_cols:
        if col in predictions_df.columns:
            customer_col = col
            break
    
    for col in product_cols:
        if col in predictions_df.columns:
            product_col = col
            break
            
    for col in pred_cols:
        if col in predictions_df.columns:
            pred_col = col
            break
    
    if not all([customer_col, product_col, pred_col]):
        print(f"Missing required columns: customer={customer_col}, product={product_col}, prediction={pred_col}")
        return None
    
    # Filter for this specific product
    product_predictions = predictions_df[
        predictions_df[product_col] == product_code
    ]
    
    if product_predictions.empty:
        print(f"No predictions found for product {product_code}")
        return None
    
    # Aggregate across all customers
    total_prediction = product_predictions[pred_col].sum()
    customer_count = len(product_predictions[customer_col].unique())
    
    # Get average confidence if available
    confidence_cols = ['confidence_score', 'confidence', 'score']
    avg_confidence = None
    for col in confidence_cols:
        if col in product_predictions.columns:
            avg_confidence = product_predictions[col].mean()
            break
    
    return {
        'total_predicted_quantity': total_prediction,
        'customer_count': customer_count,
        'avg_confidence': avg_confidence,
        'individual_predictions': len(product_predictions)
    }

def get_product_categories_existing():
    """Get unique product categories from your existing data."""
    query = """
    SELECT DISTINCT product_type
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.product_analytics`
    WHERE product_type IS NOT NULL
    ORDER BY product_type
    """
    result = run_query(query)
    if result is not None and not result.empty:
        return result['product_type'].tolist()
    return []

def load_seasonal_patterns_for_products():
    """
    Load seasonality data for products from your seasonal_patterns table.
    Used for the seasonality heatmap.
    """
    query = """
    SELECT 
        entity_id as product_code,
        entity_name as product_name,
        jan_index, feb_index, mar_index, apr_index, may_index, jun_index,
        jul_index, aug_index, sep_index, oct_index, nov_index, dec_index,
        peak_month, trough_month, seasonality_strength, seasonality_classification
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.seasonal_patterns`
    WHERE entity_type = 'product'
    ORDER BY seasonality_strength DESC
    """
    return run_query(query)

def get_category_revenue_breakdown():
    """
    Get revenue breakdown by product category for pie chart.
    """
    query = """
    SELECT 
        product_type,
        COUNT(*) as product_count,
        SUM(total_revenue_all_time) as category_revenue,
        SUM(total_quantity_all_time) as category_quantity,
        AVG(customer_penetration_pct) as avg_penetration
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.product_analytics`
    GROUP BY product_type
    ORDER BY category_revenue DESC
    """
    return run_query(query)

def get_top_growing_products(limit=10):
    """
    Get top growing products for growth chart.
    """
    query = f"""
    SELECT 
        product_code,
        product_name,
        product_type,
        quantity_growth_pct,
        revenue_growth_pct,
        trend_direction,
        total_revenue_all_time
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.product_analytics`
    WHERE quantity_growth_pct > 0
    ORDER BY quantity_growth_pct DESC
    LIMIT {limit}
    """
    return run_query(query)

def get_products_for_dropdown(category=None):
    """
    Get products for dropdown selection, optionally filtered by category.
    """
    where_clause = ""
    if category and category != "All Categories":
        where_clause = f"WHERE product_type = '{category}'"
    
    query = f"""
    SELECT 
        product_code,
        product_name,
        product_type,
        total_revenue_all_time,
        rank_by_revenue
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.product_analytics`
    {where_clause}
    ORDER BY total_revenue_all_time DESC
    """
    return run_query(query)

def load_basket_analysis():
    """Load basket analysis data from BigQuery."""
    query = """
    SELECT 
        product_a,
        product_b,
        product_a_name,
        product_b_name,
        category_relationship,
        customers_buying_both,
        customers_buying_a_total,
        customers_buying_b_total,
        support_pct,
        confidence_a_to_b_pct,
        confidence_b_to_a_pct,
        lift,
        association_strength,
        avg_qty_a_in_bundle,
        avg_qty_b_in_bundle,
        avg_bundle_revenue,
        bundle_score,
        bundle_name_suggestion,
        sample_customers
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.basket_analysis`
    ORDER BY lift DESC, bundle_score DESC
    """
    return run_query(query)

def load_top_bundles(limit=10):
    """Load top bundle opportunities by bundle score."""
    query = f"""
    SELECT 
        product_a,
        product_b,
        product_a_name,
        product_b_name,
        bundle_name_suggestion,
        bundle_score,
        lift,
        support_pct,
        confidence_a_to_b_pct,
        avg_bundle_revenue,
        association_strength
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.basket_analysis`
    WHERE bundle_score >= 50
    ORDER BY bundle_score DESC, lift DESC
    LIMIT {limit}
    """
    return run_query(query)

def load_cross_sell_recommendations(product_code):
    """Load cross-sell recommendations for a specific product."""
    query = f"""
    SELECT 
        CASE 
            WHEN product_a = '{product_code}' THEN product_b
            WHEN product_b = '{product_code}' THEN product_a
        END as recommended_product,
        CASE 
            WHEN product_a = '{product_code}' THEN product_b_name
            WHEN product_b = '{product_code}' THEN product_a_name
        END as recommended_product_name,
        CASE 
            WHEN product_a = '{product_code}' THEN confidence_a_to_b_pct
            WHEN product_b = '{product_code}' THEN confidence_b_to_a_pct
        END as confidence_pct,
        lift,
        support_pct,
        bundle_score,
        avg_bundle_revenue,
        bundle_name_suggestion
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.basket_analysis`
    WHERE product_a = '{product_code}' OR product_b = '{product_code}'
    ORDER BY confidence_pct DESC, lift DESC
    """
    return run_query(query)

def get_category_cross_sell_stats():
    """Get cross-selling statistics by category relationships."""
    query = """
    SELECT 
        category_relationship,
        COUNT(*) as pair_count,
        AVG(lift) as avg_lift,
        AVG(support_pct) as avg_support,
        AVG(bundle_score) as avg_bundle_score,
        AVG(avg_bundle_revenue) as avg_revenue
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.basket_analysis`
    GROUP BY category_relationship
    ORDER BY avg_lift DESC
    """
    return run_query(query)

def get_association_strength_distribution():
    """Get distribution of association strengths."""
    query = """
    SELECT 
        association_strength,
        COUNT(*) as count,
        AVG(lift) as avg_lift,
        AVG(bundle_score) as avg_bundle_score
    FROM `ml-goldman-hotels-vit-vertex.sales_analytics.basket_analysis`
    GROUP BY association_strength
    ORDER BY avg_lift DESC
    """
    return run_query(query)

def load_product_list_for_basket():
    """Load product list for basket analysis selections."""
    query = """
    SELECT DISTINCT 
        Product_code,
        Product_name,
        product_type
    FROM `ml-goldman-hotels-vit-vertex.sales_forecasting.features_history`
    WHERE Product_name IS NOT NULL 
      AND Product_name != 'Unknown Product'
    ORDER BY Product_name
    """
    return run_query(query)
