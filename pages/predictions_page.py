"""
Create new file: pages/predictions_page.py
Complete predictions page with dropdowns and visualization.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_customer_product_combinations, 
    load_historical_for_customer_product,
    get_customers_with_products
)
from utils.cloud_storage import (
    get_available_prediction_months,
    load_predictions_from_gcs,
    format_month_display
)
from components.charts import create_prediction_graph

def render_predictions_page():
    """Render the complete predictions analysis page."""
    st.header("📈 Sales Predictions")
    
    # Get available prediction months
    available_months = get_available_prediction_months()
    
    if not available_months:
        st.error("No prediction files found in Cloud Storage. Please check your data pipeline.")
        return
    
    # Month selector
    col1, col2, col3 = st.columns([2, 3, 3])
    
    with col1:
        month_options = {}
        for month in available_months:
            display_name = format_month_display(month)
            month_options[month] = display_name
        
        selected_month = st.selectbox(
            "📅 Select Forecast Month:",
            options=list(month_options.keys()),
            format_func=lambda x: month_options[x],
            help="Choose which month's predictions to view"
        )
    
    # Check if predictions are available for selected month
    predictions_df = load_predictions_from_gcs(selected_month)
    
    if predictions_df.empty:
        st.warning(f"Predictions for {format_month_display(selected_month)} are being finalized. Please check back later.")
        return
    
    # Load customer-product combinations
    options_df = load_customer_product_combinations()
    
    if options_df is None or options_df.empty:
        st.error("Unable to load customer and product data. Please check your BigQuery connection.")
        return
    
    # Customer and Product selectors
    with col2:
        customers = sorted(options_df['Customer_ID'].unique())
        selected_customer = st.selectbox(
            "🏢 Select Customer:",
            options=[''] + customers,
            format_func=lambda x: "Choose a customer..." if x == '' else x,
            help="Select customer to view their sales forecast"
        )
    
    with col3:
        if selected_customer:
            # Filter products for selected customer
            customer_products = options_df[
                options_df['Customer_ID'] == selected_customer
            ]
            
            # Create product display with names
            product_options = {}
            for _, row in customer_products.iterrows():
                pc = row['Product_code']
                pname = row['Product_name'] if pd.notna(row['Product_name']) else 'Unknown Product'
                product_options[pc] = f"{pc} - {pname}"
            
            selected_product = st.selectbox(
                "📦 Select Product:",
                options=[''] + list(product_options.keys()),
                format_func=lambda x: "Choose a product..." if x == '' else product_options.get(x, x),
                help="Select product to forecast"
            )
        else:
            selected_product = ''
            st.selectbox(
                "📦 Select Product:",
                options=[''],
                format_func=lambda x: "Select a customer first...",
                disabled=True
            )
    
    # Generate forecast button and visualization
    if selected_customer and selected_product:
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            generate_forecast = st.button(
                "🔮 Generate Forecast",
                type="primary",
                use_container_width=True
            )
        
        if generate_forecast:
            with st.spinner("Loading historical data and generating forecast..."):
                
                # Load historical data
                historical = load_historical_for_customer_product(
                    selected_customer, 
                    selected_product
                )
                
                # Find prediction for this customer-product combination
                prediction_value = None
                confidence_score = None
                
                if not predictions_df.empty:
                    # Try different possible column names for customer and product
                    customer_cols = ['Customer_ID', 'customer_id', 'Customer', 'customer']
                    product_cols = ['Product_code', 'product_code', 'Product', 'product']
                    
                    customer_col = None
                    product_col = None
                    
                    for col in customer_cols:
                        if col in predictions_df.columns:
                            customer_col = col
                            break
                    
                    for col in product_cols:
                        if col in predictions_df.columns:
                            product_col = col
                            break
                    
                    if customer_col and product_col:
                        pred_row = predictions_df[
                            (predictions_df[customer_col] == selected_customer) &
                            (predictions_df[product_col] == selected_product)
                        ]
                        
                        if not pred_row.empty:
                            # Try different possible column names for prediction
                            pred_cols = ['predicted_quantity', 'prediction', 'forecast', 'quantity_predicted']
                            for col in pred_cols:
                                if col in pred_row.columns:
                                    prediction_value = pred_row[col].iloc[0]
                                    break
                            
                            # Try to get confidence if available
                            conf_cols = ['confidence_score', 'confidence', 'score']
                            for col in conf_cols:
                                if col in pred_row.columns:
                                    confidence_score = pred_row[col].iloc[0]
                                    break
                
                # Create and display graph
                if historical is not None and not historical.empty:
                    product_name = product_options.get(selected_product, selected_product)
                    
                    fig = create_prediction_graph(
                        historical,
                        prediction_value,
                        selected_customer,
                        product_name,
                        selected_month
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display metrics below the graph
                    st.markdown("### 📊 Forecast Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if not historical.empty:
                            avg_historical = historical['Quantity_sold'].mean()
                            st.metric(
                                "Historical Average", 
                                f"{avg_historical:.1f}",
                                help="Average monthly quantity over historical period"
                            )
                    
                    with col2:
                        if prediction_value is not None:
                            st.metric(
                                "Forecast", 
                                f"{prediction_value:.1f}",
                                help=f"AI prediction for {format_month_display(selected_month)}"
                            )
                        else:
                            st.metric("Forecast", "N/A", help="No prediction available")
                    
                    with col3:
                        if prediction_value is not None and not historical.empty and avg_historical > 0:
                            change = ((prediction_value - avg_historical) / avg_historical) * 100
                            st.metric(
                                "vs Historical Avg", 
                                f"{change:+.1f}%",
                                delta=f"{change:+.1f}%",
                                help="Percentage change from historical average"
                            )
                        else:
                            st.metric("vs Historical Avg", "N/A")
                    
                    with col4:
                        if confidence_score is not None:
                            st.metric(
                                "Confidence", 
                                f"{confidence_score:.1%}" if confidence_score <= 1 else f"{confidence_score:.1f}",
                                help="Model confidence in this prediction"
                            )
                        else:
                            st.metric("Confidence", "N/A")
                    
                    # Additional insights
                    if not historical.empty:
                        st.markdown("### 💡 Insights")
                        
                        # Recent trend
                        if len(historical) >= 3:
                            recent_avg = historical['Quantity_sold'].tail(3).mean()
                            older_avg = historical['Quantity_sold'].head(-3).mean() if len(historical) > 3 else recent_avg
                            
                            if recent_avg > older_avg * 1.1:
                                st.success("📈 **Upward trend** detected in recent months")
                            elif recent_avg < older_avg * 0.9:
                                st.warning("📉 **Downward trend** detected in recent months")
                            else:
                                st.info("📊 **Stable pattern** observed in recent months")
                        
                        # Seasonality hint
                        if len(historical) >= 12:
                            st.info(f"💡 **Historical range**: {historical['Quantity_sold'].min():.0f} - {historical['Quantity_sold'].max():.0f} units per month")
                
                else:
                    st.warning(f"No historical purchase data found for {selected_customer} - {product_options.get(selected_product, selected_product)}")
                    st.info("This customer may not have purchased this product in the historical period, or there may be a data issue.")
    
    elif selected_customer and not selected_product:
        st.info("👆 Please select a product to generate forecast")
    elif not selected_customer:
        st.info("👆 Please select a customer and product to generate forecast")
    
    # Footer info
    st.markdown("---")
    st.markdown("""
    **ℹ️ About Predictions:**
    - Historical data shows actual monthly purchases
    - ML predictions are based on customer behavior patterns, seasonality, and product trends
    - Forecasts are updated monthly as new data becomes available
    """)
