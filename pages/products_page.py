"""
Create/Replace pages/products_page.py
Product Analytics page adapted for your existing data structure
"""
import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_product_analytics_existing, 
    load_product_historical_monthly,
    load_product_prediction_aggregated_fixed,
    load_multiple_products_historical,
    get_product_categories_existing,
    get_products_for_dropdown,
    load_seasonal_patterns_for_products,
    get_category_revenue_breakdown,
    get_top_growing_products
)
from utils.cloud_storage import get_available_prediction_months, format_month_display
from components.charts import (
    create_product_performance_graph_existing,
    create_product_comparison_chart_existing,
    create_category_revenue_pie_existing,
    create_growth_chart_existing,
    create_seasonality_heatmap_existing,
    create_penetration_scatter_existing
)

def render_products_page():
    """Render the complete product analytics page using existing data structure."""
    st.header("📦 Product Analytics")
    
    # Load product analytics data
    product_df = load_product_analytics_existing()
    
    if product_df is None or product_df.empty:
        st.error("Unable to load product analytics data. Please check your BigQuery connection.")
        return
    
    # Page tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Product Performance", 
        "📊 Rankings & Metrics", 
        "🔄 Product Comparison",
        "📈 Market Insights"
    ])
    
    with tab1:
        render_product_performance_tab_existing(product_df)
    
    with tab2:
        render_product_rankings_tab_existing(product_df)
    
    with tab3:
        render_product_comparison_tab_existing(product_df)
    
    with tab4:
        render_market_insights_tab_existing(product_df)

def render_product_performance_tab_existing(product_df):
    """Individual product performance analysis using existing data."""
    st.subheader("📈 Individual Product Performance")
    
    # Get available prediction months
    available_months = get_available_prediction_months()
    
    # Controls
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        # Category filter
        categories = get_product_categories_existing()
        selected_category = st.selectbox(
            "📂 Filter by Category:",
            options=["All Categories"] + categories,
            help="Filter products by category"
        )
    
    with col2:
        # Product selector
        filtered_products = get_products_for_dropdown(selected_category)
        
        if filtered_products is not None and not filtered_products.empty:
            product_display = {}
            for _, row in filtered_products.iterrows():
                product_display[row['product_code']] = f"{row['product_code']} - {row['product_name']}"
            
            selected_product = st.selectbox(
                "📦 Select Product:",
                options=list(product_display.keys()),
                format_func=lambda x: product_display.get(x, x),
                help="Choose product to analyze"
            )
        else:
            selected_product = None
            st.selectbox(
                "📦 Select Product:",
                options=[],
                help="No products available"
            )
    
    with col3:
        # Month selector
        if available_months:
            month_options = {}
            for month in available_months:
                month_options[month] = format_month_display(month)
            
            selected_month = st.selectbox(
                "📅 Prediction Month:",
                options=list(month_options.keys()),
                format_func=lambda x: month_options[x],
                help="Choose forecast month"
            )
        else:
            selected_month = None
            st.selectbox(
                "📅 Prediction Month:",
                options=[],
                help="No predictions available"
            )
    
    if selected_product:
        st.markdown("---")
        
        # Load historical and prediction data
        with st.spinner("Loading product performance data..."):
            historical_data = load_product_historical_monthly(selected_product)
            prediction_data = None
            
            if selected_month:
                prediction_data = load_product_prediction_aggregated_fixed(selected_product, selected_month)
        
        if historical_data is not None and not historical_data.empty:
            product_name = product_display.get(selected_product, selected_product)
            
            # Create and display graph
            fig = create_product_performance_graph_existing(
                historical_data, 
                prediction_data, 
                product_name,
                selected_month or "2025_07"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Product metrics
            st.markdown("### 📊 Product Performance Metrics")
            
            # Get product details from analytics table
            product_details = product_df[product_df['product_code'] == selected_product].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_historical = product_details['total_quantity_all_time']
                st.metric(
                    "Total Historical Sales",
                    f"{total_historical:,.0f}",
                    help="Total units sold across all time"
                )
            
            with col2:
                avg_monthly = product_details['avg_monthly_quantity']
                st.metric(
                    "Monthly Average",
                    f"{avg_monthly:.1f}",
                    help="Average monthly demand"
                )
            
            with col3:
                if prediction_data:
                    pred_value = prediction_data['total_predicted_quantity']
                    st.metric(
                        "Next Month Forecast",
                        f"{pred_value:.1f}",
                        help="Predicted total demand next month"
                    )
                else:
                    st.metric("Next Month Forecast", "N/A")
            
            with col4:
                growth_rate = product_details['quantity_growth_pct']
                if pd.notna(growth_rate):
                    st.metric(
                        "Growth Rate",
                        f"{growth_rate:+.1f}%",
                        delta=f"{growth_rate:+.1f}%",
                        help="Recent quantity growth percentage"
                    )
                else:
                    st.metric("Growth Rate", "N/A")
            
            # Additional product insights
            st.markdown("### 💡 Product Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                penetration = product_details['customer_penetration_pct']
                customers_last_3mo = product_details.get('quantity_last_3mo', 0)
                st.info(f"""
                **Market Penetration**  
                {penetration:.1f}% of customers  
                (Recent activity: {customers_last_3mo:.0f} units last 3 months)
                """)
            
            with col2:
                trend_direction = product_details['trend_direction']
                growth_emoji = "📈" if "Growth" in trend_direction else "📊" if "Stable" in trend_direction else "📉"
                st.info(f"""
                **Growth Trend**  
                {growth_emoji} {trend_direction}  
                ({growth_rate:+.1f}% growth rate)
                """)
            
            with col3:
                rank_revenue = product_details['rank_by_revenue']
                percentile = product_details['percentile_rank']
                st.info(f"""
                **Market Position**  
                #{rank_revenue} by revenue  
                (Top {percentile:.0f}% of products)
                """)
            
            # Seasonality and top customers
            if pd.notna(product_details['peak_month']):
                month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                
                try:
                    peak_month_name = month_names[int(product_details['peak_month'])]
                    st.success(f"📅 **Peak Season**: {peak_month_name}")
                except:
                    st.info("📅 Seasonality data available")
            
            # Top customers
            if pd.notna(product_details['top_customer_1']):
                top_customer = product_details['top_customer_1']
                top_quantity = product_details['top_customer_1_qty']
                st.info(f"👑 **Top Customer**: {top_customer} ({top_quantity:.0f} units)")
        
        else:
            st.warning(f"No historical data found for product {selected_product}")

def render_product_rankings_tab_existing(product_df):
    """Product rankings using existing data structure."""
    st.subheader("🏆 Product Rankings")
    
    # Ranking options
    col1, col2 = st.columns(2)
    
    with col1:
        ranking_metric = st.selectbox(
            "📊 Rank by:",
            options=["Revenue", "Quantity", "Growth Rate", "Customer Penetration"],
            help="Choose ranking criteria"
        )
    
    with col2:
        category_filter = st.selectbox(
            "📂 Category:",
            options=["All Categories"] + get_product_categories_existing(),
            help="Filter by product category"
        )
    
    # Filter data
    display_df = product_df.copy()
    if category_filter != "All Categories":
        display_df = display_df[display_df['product_type'] == category_filter]
    
    # Sort by selected metric
    if ranking_metric == "Revenue":
        display_df = display_df.sort_values('total_revenue_all_time', ascending=False)
        value_col = 'total_revenue_all_time'
        format_func = lambda x: f"₽{x:,.0f}"
    elif ranking_metric == "Quantity":
        display_df = display_df.sort_values('total_quantity_all_time', ascending=False)
        value_col = 'total_quantity_all_time'
        format_func = lambda x: f"{x:,.0f}"
    elif ranking_metric == "Growth Rate":
        display_df = display_df.sort_values('quantity_growth_pct', ascending=False)
        value_col = 'quantity_growth_pct'
        format_func = lambda x: f"{x:+.1f}%"
    else:  # Customer Penetration
        display_df = display_df.sort_values('customer_penetration_pct', ascending=False)
        value_col = 'customer_penetration_pct'
        format_func = lambda x: f"{x:.1f}%"
    
    # Display top 20
    st.markdown(f"### Top Products by {ranking_metric}")
    
    top_products = display_df.head(20)
    
    # Create display table
    ranking_table = pd.DataFrame({
        'Rank': range(1, len(top_products) + 1),
        'Product Code': top_products['product_code'],
        'Product Name': top_products['product_name'],
        'Category': top_products['product_type'],
        ranking_metric: top_products[value_col].apply(format_func),
        'Trend': top_products['trend_direction']
    })
    
    st.dataframe(ranking_table, hide_index=True, use_container_width=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(display_df)
        st.metric("Total Products", f"{total_products}")
    
    with col2:
        growing_products = len(display_df[display_df['trend_direction'].str.contains('Growth', na=False)])
        st.metric("Growing Products", f"{growing_products}")
    
    with col3:
        avg_penetration = display_df['customer_penetration_pct'].mean()
        st.metric("Avg. Penetration", f"{avg_penetration:.1f}%")
    
    with col4:
        avg_growth = display_df['quantity_growth_pct'].mean()
        st.metric("Avg. Growth", f"{avg_growth:.1f}%")

def render_product_comparison_tab_existing(product_df):
    """Compare multiple products using existing data."""
    st.subheader("🔄 Product Comparison")
    
    # Product selection for comparison
    product_options = {}
    for _, row in product_df.iterrows():
        product_options[row['product_code']] = f"{row['product_code']} - {row['product_name']}"
    
    selected_products = st.multiselect(
        "📦 Select Products to Compare (max 5):",
        options=list(product_options.keys()),
        format_func=lambda x: product_options.get(x, x),
        max_selections=5,
        help="Choose 2-5 products to compare their demand trends"
    )
    
    if len(selected_products) >= 2:
        # Time period selector
        time_period = st.selectbox(
            "📅 Time Period:",
            options=[6, 12, 18, 24],
            format_func=lambda x: f"Last {x} months",
            index=1
        )
        
        # Load comparison data
        with st.spinner("Loading comparison data..."):
            comparison_data = load_multiple_products_historical(selected_products, time_period)
        
        if comparison_data is not None and not comparison_data.empty:
            # Create comparison chart
            fig = create_product_comparison_chart_existing(comparison_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Comparison metrics table
            st.markdown("### 📊 Comparison Metrics")
            
            comparison_metrics = []
            for product_code in selected_products:
                product_info = product_df[product_df['product_code'] == product_code].iloc[0]
                product_data = comparison_data[comparison_data['Product_code'] == product_code]
                
                if not product_data.empty:
                    total_demand = product_data['total_quantity'].sum()
                    avg_monthly = product_data['total_quantity'].mean()
                else:
                    total_demand = 0
                    avg_monthly = 0
                
                comparison_metrics.append({
                    'Product': f"{product_code} - {product_info['product_name']}",
                    'Total Demand': f"{total_demand:,.0f}",
                    'Monthly Avg': f"{avg_monthly:.1f}",
                    'Growth Rate': f"{product_info['quantity_growth_pct']:+.1f}%",
                    'Penetration': f"{product_info['customer_penetration_pct']:.1f}%"
                })
            
            comparison_df = pd.DataFrame(comparison_metrics)
            st.dataframe(comparison_df, hide_index=True, use_container_width=True)
        else:
            st.warning("No historical data available for comparison.")
    
    elif len(selected_products) == 1:
        st.info("👆 Please select at least 2 products for comparison")
    else:
        st.info("👆 Select products to compare their performance")

def render_market_insights_tab_existing(product_df):
    """Market insights using existing data structure."""
    st.subheader("📈 Market Insights")
    
    # Load additional data for insights
    category_data = get_category_revenue_breakdown()
    growth_data = get_top_growing_products(8)
    seasonality_data = load_seasonal_patterns_for_products()
    
    # Category performance chart
    if category_data is not None and not category_data.empty:
        st.markdown("### 📊 Revenue by Product Category")
        category_fig = create_category_revenue_pie_existing(category_data)
        st.plotly_chart(category_fig, use_container_width=True)
    
    # Growth and seasonality
    col1, col2 = st.columns(2)
    
    with col1:
        if growth_data is not None and not growth_data.empty:
            st.markdown("### 🚀 Top Growing Products")
            growth_fig = create_growth_chart_existing(growth_data)
            st.plotly_chart(growth_fig, use_container_width=True)
    
    with col2:
        if seasonality_data is not None and not seasonality_data.empty:
            st.markdown("### 📅 Seasonality Patterns")
            seasonality_fig = create_seasonality_heatmap_existing(seasonality_data)
            st.plotly_chart(seasonality_fig, use_container_width=True)
    
    # Portfolio scatter plot
    st.markdown("### 💰 Product Portfolio Analysis")
    portfolio_fig = create_penetration_scatter_existing(product_df)
    st.plotly_chart(portfolio_fig, use_container_width=True)
    
    # Market insights summary
    st.markdown("### 💡 Key Market Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if category_data is not None and not category_data.empty:
            top_category = category_data.loc[category_data['category_revenue'].idxmax(), 'product_type']
            st.success(f"🏆 **Leading Category**\n{top_category}")
    
    with col2:
        fastest_growing = product_df.loc[product_df['quantity_growth_pct'].idxmax()]
        st.success(f"📈 **Fastest Growing**\n{fastest_growing['product_name']}\n(+{fastest_growing['quantity_growth_pct']:.1f}%)")
    
    with col3:
        highest_penetration = product_df.loc[product_df['customer_penetration_pct'].idxmax()]
        st.success(f"🎯 **Highest Penetration**\n{highest_penetration['product_name']}\n({highest_penetration['customer_penetration_pct']:.1f}%)")
    
    # Portfolio health summary
    growing_count = len(product_df[product_df['trend_direction'].str.contains('Growth', na=False)])
    declining_count = len(product_df[product_df['trend_direction'].str.contains('Declin', na=False)])
    total_count = len(product_df)
    
    st.info(f"""
    **📊 Portfolio Health:**  
    - {growing_count}/{total_count} products are growing ({growing_count/total_count*100:.1f}%)
    - {declining_count}/{total_count} products are declining ({declining_count/total_count*100:.1f}%)
    - Average customer penetration: {product_df['customer_penetration_pct'].mean():.1f}%
    - Average growth rate: {product_df['quantity_growth_pct'].mean():.1f}%
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **ℹ️ About Product Analytics:**
    - All metrics calculated from your existing BigQuery analytics tables
    - Growth rates and trends based on your data calculations
    - Seasonality patterns from your seasonal_patterns table
    - Market demand aggregated across all customers
    """)
