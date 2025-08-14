"""
Update pages/overview_page.py with enhanced features
Replace your existing render_overview_page function with this enhanced version
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_kpi_data, load_customer_analytics, load_product_analytics_existing
from components.kpi_cards import display_kpi_metrics, display_summary_stats
from components.charts import (
    create_revenue_trend_chart, 
    create_month_comparison_radar,
    create_comparison_metrics_table,
    generate_smart_insights,
    create_performance_gauge
)

def render_overview_page():
    """Render the enhanced overview/KPI page with comparisons and insights."""
    st.header("Key Performance Indicators")
    
    # Load all KPI data
    all_kpi_df = load_kpi_data()
    
    if all_kpi_df is not None and not all_kpi_df.empty:
        # Create readable month labels
        all_kpi_df['month_label_display'] = pd.to_datetime(
            all_kpi_df['report_month']
        ).dt.strftime('%B %Y')
        
        # Main dashboard layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Month selector for main KPIs
            selected_month = st.selectbox(
                "Select Month for KPI Display:",
                options=all_kpi_df['month_label_display'].tolist(),
                index=0,  # Default to most recent month
                help="Choose which month's KPIs to display in detail"
            )
        
        with col2:
            # Performance gauge
            st.markdown("### 🎯 Performance Score")
            gauge_fig = create_performance_gauge(all_kpi_df)
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        # Filter data for selected month
        kpi_df = all_kpi_df[all_kpi_df['month_label_display'] == selected_month]
        
        # Display main KPI metrics
        st.markdown("---")
        st.markdown(f"### 📊 {selected_month} Performance")
        display_kpi_metrics(kpi_df)
        
        # Interactive Month Comparison Section
        st.markdown("---")
        st.markdown("### 🔄 Interactive Month Comparison")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            month_1 = st.selectbox(
                "First Month:",
                options=all_kpi_df['month_label_display'].tolist(),
                index=0,
                help="Select first month for comparison"
            )
        
        with col2:
            month_2 = st.selectbox(
                "Second Month:",
                options=all_kpi_df['month_label_display'].tolist(),
                index=min(1, len(all_kpi_df) - 1),
                help="Select second month for comparison"
            )
        
        with col3:
            compare_button = st.button("🔍 Compare", type="primary", use_container_width=True)
        
        # Show comparison when button clicked or months are different
        if compare_button or month_1 != month_2:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Radar chart comparison
                radar_fig = create_month_comparison_radar(all_kpi_df, month_1, month_2)
                st.plotly_chart(radar_fig, use_container_width=True)
            
            with col2:
                # Detailed comparison table
                st.markdown("#### 📋 Detailed Comparison")
                comparison_df = create_comparison_metrics_table(all_kpi_df, month_1, month_2)
                if not comparison_df.empty:
                    st.dataframe(comparison_df, hide_index=True, use_container_width=True)
                    
                    # Comparison insights
                    st.markdown("#### 💡 Key Changes")
                    m1_data = all_kpi_df[all_kpi_df['month_label_display'] == month_1].iloc[0]
                    m2_data = all_kpi_df[all_kpi_df['month_label_display'] == month_2].iloc[0]
                    
                    revenue_change = ((m2_data['total_revenue'] - m1_data['total_revenue']) / m1_data['total_revenue']) * 100
                    
                    if revenue_change > 10:
                        st.success(f"📈 Revenue increased {revenue_change:.1f}% from {month_1} to {month_2}")
                    elif revenue_change < -10:
                        st.warning(f"📉 Revenue decreased {abs(revenue_change):.1f}% from {month_1} to {month_2}")
                    else:
                        st.info(f"📊 Revenue remained stable ({revenue_change:+.1f}%) between months")
        
        # Revenue trend chart
        st.markdown("---")
        st.markdown("### 📈 Revenue Trend Analysis")
        fig = create_revenue_trend_chart(all_kpi_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # AI-Generated Insights Section
        st.markdown("---")
        st.markdown("### 🧠 AI-Generated Business Insights")
        
        with st.expander("📊 **Smart Analytics Report**", expanded=True):
            # Load additional data for insights
            try:
                customer_data = load_customer_analytics()
                product_data = load_product_analytics_existing()
            except:
                customer_data = None
                product_data = None
            
            # Generate insights
            insights = generate_smart_insights(all_kpi_df, customer_data, product_data)
            
            # Display insights with nice formatting
            for i, insight in enumerate(insights):
                if i % 2 == 0:
                    st.info(insight)
                else:
                    st.success(insight)
            
            # Refresh insights button
            if st.button("🔄 Refresh Insights"):
                st.rerun()
        
        # Summary statistics
        st.markdown("---")
        st.markdown("### 📋 Summary Statistics")
        display_summary_stats(all_kpi_df)
        
        # Quick Actions Section
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 View Top Customers", use_container_width=True):
                st.switch_page("pages/customers_page.py")
        
        with col2:
            if st.button("📦 Analyze Products", use_container_width=True):
                st.switch_page("pages/products_page.py")
        
        with col3:
            if st.button("🔮 See Predictions", use_container_width=True):
                st.switch_page("pages/predictions_page.py")
        
        with col4:
            if st.button("🛒 Basket Analysis", use_container_width=True):
                st.switch_page("pages/basket_analysis_page.py")
        
        # Data freshness indicator
        st.markdown("---")
        latest_update = all_kpi_df['last_updated'].max() if 'last_updated' in all_kpi_df.columns else "Unknown"
        st.caption(f"📅 Data last updated: {latest_update}")
        
    else:
        st.error("No data available. Please check your BigQuery connection.")
        
        # Show helpful debugging info
        with st.expander("🔧 Debugging Information"):
            st.write("**Possible issues:**")
            st.write("- BigQuery connection not configured")
            st.write("- `kpi_summary` table is empty")
            st.write("- No data in date range")
            st.write("- Service account permissions issue")
            
            st.write("**Quick fixes:**")
            st.write("1. Check your BigQuery connection in `utils/database.py`")
            st.write("2. Verify data exists: `SELECT COUNT(*) FROM sales_analytics.kpi_summary`")
            st.write("3. Check service account has BigQuery read permissions")
